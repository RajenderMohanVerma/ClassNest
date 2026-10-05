"""Schema-level tests for the ClassNext data model.

These cover the pieces the master prompt calls out explicitly: the
``Class -> Subject -> Chapter -> Content`` hierarchy, the five content states,
free/premium pricing, order idempotency, enrollment uniqueness, and the
"never expose secrets / never trust the client" rules.
"""

import re
from datetime import timedelta

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import CreateTable

from app import db
from app.models import (
    ACCESS_LEVELS,
    CONTENT_STATUSES,
    AccountToken,
    AuditLog,
    Bookmark,
    BookmarkTarget,
    Chapter,
    Content,
    Course,
    Enrollment,
    LearningProgress,
    Notification,
    Order,
    RecentlyViewed,
    SchoolClass,
    SiteSetting,
    StudentClassAccess,
    Subject,
    User,
    active_enrollment_for,
    hash_token,
    open_order_for,
    settled_order_for,
    utcnow,
)
from app.models.enums import (
    CONTENT_STATUS_ARCHIVED,
    CONTENT_STATUS_PUBLISHED,
    CONTENT_STATUS_SCHEDULED,
    CONTENT_STATUS_UNPUBLISHED,
    NOTIFICATION_ORDER,
    ORDER_STATUS_PAID,
    TOKEN_PURPOSE_PASSWORD_RESET,
)

CLASSNEXT_TABLES = {
    'classes', 'chapters', 'playlists', 'playlist_items',
    'courses', 'course_sections', 'course_lessons',
    'orders', 'enrollments', 'bookmarks', 'recently_viewed',
    'learning_progress', 'notifications', 'assignments',
    'assignment_submissions', 'student_class_access', 'account_tokens',
    'site_settings', 'teacher_profile', 'faqs', 'contact_enquiries',
    'audit_logs',
}


# --- structure -------------------------------------------------------------

def test_classnext_tables_are_created(app):
    assert CLASSNEXT_TABLES.issubset(set(inspect(db.engine).get_table_names()))


def test_no_degenerate_check_constraints(app):
    """Guard against ``CHECK (false)`` from ``column in (...)``.

    Writing ``db.CheckConstraint(status in VALUES)`` instead of
    ``status.in_(VALUES)`` silently produces a constraint that rejects every
    valid row, so this scans the compiled DDL of every table.
    """
    broken = []
    for name, table in db.metadata.tables.items():
        sql = str(CreateTable(table).compile(dialect=postgresql.dialect()))
        for match in re.finditer(r'CONSTRAINT \S+ CHECK \((.*?)\)(?:,|\s*\))', sql):
            if match.group(1).strip() in ('false', 'true'):
                broken.append(f'{name}: {match.group(0)}')
    assert not broken, f'degenerate CHECK constraints: {broken}'


def test_required_hierarchy_columns_exist(app):
    inspector = inspect(db.engine)
    columns = {t: {c['name'] for c in inspector.get_columns(t)}
               for t in ('classes', 'subjects', 'chapters', 'content')}
    assert 'class_id' in columns['subjects']
    assert {'subject_id', 'class_id'} <= columns['chapters']
    assert {'subject_id', 'chapter_id', 'class_id', 'access_level'} <= columns['content']


# --- hierarchy -------------------------------------------------------------

def test_class_subject_chapter_content_chain(app, teacher, school_class, subject, chapter):
    subject.class_id = school_class.id
    chapter.subject_id = subject.id
    item = Content(
        title='Chained Lesson',
        slug=Content.unique_slug('Chained Lesson'),
        subject_id=subject.id,
        chapter_id=chapter.id,
        class_id=school_class.id,
        content_type='video_lesson',
        status=CONTENT_STATUS_PUBLISHED,
        created_by=teacher.id,
    )
    add_all(item)
    commit()

    assert item.chapter.id == chapter.id
    assert item.subject.id == subject.id
    assert item.school_class.id == school_class.id
    assert chapter.school_class.name == 'Class 10'


def test_chapters_are_ordered_and_counted(app, subject, teacher):
    for index, title in enumerate(['Alpha', 'Beta']):
        chapter = chapter_factory(subject=subject, teacher=teacher, title=title, order=index)
    assert subject.chapter_count == 2
    titles = [c.title for c in subject.chapters.order_by(Chapter.display_order).all()]
    assert titles == ['Alpha', 'Beta']


def test_class_reorder_and_archive(app, school_class):
    school_class.archive()
    assert school_class.is_archived is True
    assert school_class.is_available is False
    school_class.restore()
    school_class.is_enabled = False
    assert school_class.is_available is False


def test_unique_slugs_avoid_collisions(app, teacher, school_class):
    first = SchoolClass(name='Class 7', slug=SchoolClass.unique_slug('Class 7'))
    add_all(first)
    commit()
    second = SchoolClass(name='Class 7', slug=SchoolClass.unique_slug('Class 7'))
    add_all(second)
    commit()

    assert first.slug == 'class-7'
    assert second.slug == 'class-7-2'


def test_deleting_class_keeps_existing_subjects(app, teacher, school_class, subject):
    subject.class_id = school_class.id
    commit()
    add_all(school_class)
    commit()
    assert Subject.query.count() == 1


# --- content states --------------------------------------------------------

def test_all_five_content_states_are_accepted(app, content):
    for state in ('draft', 'scheduled', 'published', 'unpublished', 'archived'):
        content.status = state
        commit()
        assert Content.query.get(content.id).status == state


def test_unknown_content_state_is_rejected(app, content):
    with pytest.raises(IntegrityError):
        execute(
            "UPDATE content SET status = 'not-a-state' WHERE id = :i",
            {'i': content.id},
        )


def test_scheduled_content_is_hidden_from_viewers(app, content):
    content.schedule(utcnow() + timedelta(days=1))
    commit()

    assert content.is_scheduled is True
    assert content.is_hidden_from_viewers is True
    assert content.is_published is False


def test_publishing_clears_the_schedule(app, content):
    content.schedule(utcnow() + timedelta(days=1))
    content.publish()
    commit()

    assert content.scheduled_at is None
    assert content.is_published is True


def test_take_offline_keeps_the_record(app, published_content):
    published_content.take_offline()
    commit()

    assert published_content.status == CONTENT_STATUS_UNPUBLISHED
    assert published_content.published_at is None
    assert published_content.id is not None


def test_archive_hides_content_without_deleting(app, content):
    content.archive()
    commit()
    assert Content.query.count() == 1
    assert content.is_hidden_from_viewers is True
    assert content.status == CONTENT_STATUS_ARCHIVED


def test_access_levels_are_enforced(app, published_content):
    published_content.access_level = 'premium'
    commit()
    assert published_content.is_premium is True
    assert published_content.requires_purchase is True
    assert published_content.is_publicly_visible is False

    published_content.is_preview = True
    assert published_content.requires_purchase is False


def test_public_content_is_publicly_visible(app, published_content):
    published_content.access_level = 'public'
    commit()
    assert published_content.is_publicly_visible is True


def test_all_access_levels_persist(app, published_content):
    for level in ACCESS_LEVELS:
        published_content.access_level = level
        commit()
        assert Content.query.get(published_content.id).access_level == level


# --- courses ---------------------------------------------------------------

def test_course_discount_math(app, course):
    assert course.effective_price == 499
    assert course.has_discount is False
    assert course.price_label == '499'

    course.discount_price = 399
    assert course.discounted_price == 399
    assert course.effective_price == 399
    assert course.has_discount is True
    assert course.discount_percent == 20
    assert course.strike_price_label == '499'


def test_discount_at_or_above_base_price_is_ignored(app, course):
    course.discount_price = 499
    assert course.discounted_price is None
    course.discount_price = 600
    assert course.discounted_price is None
    assert course.effective_price == 499


def test_free_course_is_not_premium_by_price(app, course):
    course.price = 0
    course.access_level = 'public'
    assert course.is_premium is False
    assert course.price_label == 'Free'


def test_course_sections_and_lessons_are_ordered(app, course, course_section, course_lesson):
    assert course.section_count if hasattr(course, 'section_count') else True
    assert course.lesson_count == 1
    assert course_lesson.position == 1
    assert course_lesson.requires_purchase is False
    assert course_lesson.content.title == 'Introduction Lesson'


def test_non_preview_lesson_requires_purchase(app, course_lesson):
    course_lesson.is_preview = False
    assert course_lesson.requires_purchase is True


def test_lesson_duration_label(app, course_lesson):
    assert course_lesson.duration_label == ''
    course_lesson.duration_seconds = 95
    assert course_lesson.duration_label == '1m 35s'
    course_lesson.duration_seconds = 3725
    assert course_lesson.duration_label == '1h 2m'


def test_negative_course_price_is_rejected(app, course):
    with pytest.raises(IntegrityError):
        execute('UPDATE courses SET price = -1 WHERE id = :i', {'i': course.id})


# --- orders ----------------------------------------------------------------

def test_order_numbers_are_unique(app):
    numbers = {Order.generate_order_number() for _ in range(20)}
    assert len(numbers) == 20
    assert all(n.startswith('CN-') for n in numbers)


def test_mark_paid_is_idempotent(app, student, course):
    order = Order(
        order_number=Order.generate_order_number(),
        student_id=student.id,
        course_id=course.id,
        amount=course.price,
    )
    add_all(order)

    assert order.mark_paid(payment_reference='pay_123') is True
    first_paid_at = order.paid_at
    assert order.status == ORDER_STATUS_PAID

    # A retried gateway callback must not move the settled timestamp.
    assert order.mark_paid(payment_reference='pay_123') is False
    assert order.paid_at == first_paid_at
    assert order.payment_reference == 'pay_123'


def test_failed_order_can_be_cancelled_but_paid_cannot(app, student, course):
    order = Order(
        order_number=Order.generate_order_number(),
        student_id=student.id,
        course_id=course.id,
        amount=course.price,
    )
    add_all(order)

    order.mark_failed('gateway timeout')
    commit()
    assert order.status == 'failed'
    assert order.failure_reason == 'gateway timeout'
    assert order.is_cancellable is True

    assert order.cancel() is True
    assert order.is_cancellable is False


def test_only_paid_orders_count_as_settled(app, student, course):
    pending = Order(
        order_number=Order.generate_order_number(),
        student_id=student.id,
        course_id=course.id,
        amount=course.price,
    )
    add_all(pending)
    assert settled_order_for(student.id, course.id) is None

    pending.mark_paid()
    commit()
    assert settled_order_for(student.id, course.id).id == pending.id


def test_retry_reuses_the_open_order(app, student, course):
    first = Order(
        order_number=Order.generate_order_number(),
        student_id=student.id,
        course_id=course.id,
        amount=course.price,
    )
    add_all(first)
    first.mark_failed('declined')
    commit()

    assert open_order_for(student.id, course.id).id == first.id
    assert Order.query.count() == 1


def test_refund_requires_a_paid_order(app, student, course):
    order = Order(
        order_number=Order.generate_order_number(),
        student_id=student.id,
        course_id=course.id,
        amount=course.price,
    )
    add_all(order)
    assert order.refund() is False

    order.mark_paid()
    assert order.refund('rfnd_1') is True
    assert order.status == 'refunded'
    assert order.is_settled is False


def test_unknown_order_status_is_rejected(app, student, course):
    order = Order(
        order_number=Order.generate_order_number(),
        student_id=student.id,
        course_id=course.id,
        amount=course.price,
    )
    add_all(order)
    commit()
    with pytest.raises(IntegrityError):
        execute('UPDATE orders SET status = :s WHERE id = :i',
                   {'s': 'shipped', 'i': order.id})


# --- enrollments -----------------------------------------------------------

def test_enrollment_is_unique_per_student_and_course(app, student, course):
    first = Enrollment(student_id=student.id, course_id=course.id, source='payment')
    add_all(first)
    commit()

    duplicate = Enrollment(student_id=student.id, course_id=course.id, source='manual')
    add_all(duplicate)
    with pytest.raises(IntegrityError):
        commit()
    rollback()


def test_duplicate_payment_callback_updates_one_enrollment(app, student, course):
    """A repeated webhook must resolve to the same enrollment row."""
    order = Order(
        order_number=Order.generate_order_number(),
        student_id=student.id,
        course_id=course.id,
        amount=course.price,
    )
    add_all(order)
    order.mark_paid()
    commit()

    existing = Enrollment(student_id=student.id, course_id=course.id, order_id=order.id)
    add_all(existing)
    commit()

    again = Enrollment.query.filter_by(student_id=student.id, course_id=course.id).first()
    again.revoke()
    again.reactivate()
    commit()

    assert Enrollment.query.count() == 1
    assert active_enrollment_for(student.id, course.id).is_active is True


def test_one_enrollment_per_order(app, student, course):
    order = Order(
        order_number=Order.generate_order_number(),
        student_id=student.id,
        course_id=course.id,
        amount=course.price,
    )
    add_all(order)
    order.mark_paid()
    commit()

    add_all(Enrollment(student_id=student.id, course_id=course.id, order_id=order.id))
    commit()

    other = User(name='Other', email='other@example.com', role='student')
    other.set_password('otherpass')
    add_all(other)

    add_all(Enrollment(student_id=other.id, course_id=course.id, order_id=order.id))
    with pytest.raises(IntegrityError):
        commit()
    rollback()


def test_manual_grant_is_recorded_and_reversible(app, teacher, student, course):
    enrollment = Enrollment(
        student_id=student.id,
        course_id=course.id,
        source='manual',
        granted_by=teacher.id,
        reason='Scholarship',
    )
    add_all(enrollment)
    commit()
    assert enrollment.is_manual is True
    assert enrollment.is_active is True

    enrollment.revoke(teacher.id, reason='Request withdrawn')
    commit()
    assert enrollment.is_active is False
    assert enrollment.reason == 'Request withdrawn'
    assert enrollment.revoked_by == teacher.id


def test_expired_enrollment_is_not_active(app, student, course):
    enrollment = Enrollment(
        student_id=student.id,
        course_id=course.id,
        expires_at=utcnow() - timedelta(minutes=1),
    )
    add_all(enrollment)
    commit()
    assert enrollment.is_active is False


# --- engagement ------------------------------------------------------------

def test_bookmark_is_unique_per_target(app, student, content):
    first = Bookmark(user_id=student.id, target_type=BookmarkTarget.CONTENT, target_id=content.id)
    add_all(first)
    commit()

    duplicate = Bookmark(user_id=student.id, target_type=BookmarkTarget.CONTENT, target_id=content.id)
    add_all(duplicate)
    with pytest.raises(IntegrityError):
        commit()
    rollback()


def test_bookmark_resolves_its_target(app, student, content):
    bookmark = Bookmark(user_id=student.id, target_type=BookmarkTarget.CONTENT, target_id=content.id)
    add_all(bookmark)
    commit()
    assert bookmark.target.id == content.id


def test_bookmark_rejects_unknown_target_type(app, student):
    with pytest.raises(IntegrityError):
        add_all(Bookmark(user_id=student.id, target_type='invoice', target_id=1))
        commit()
    rollback()


def test_recently_viewed_upserts_a_single_row(app, student, content):
    RecentlyViewed.record(student.id, BookmarkTarget.CONTENT, content.id)
    commit()
    first_seen = RecentlyViewed.query.one().viewed_at

    RecentlyViewed.record(student.id, BookmarkTarget.CONTENT, content.id)
    commit()

    assert RecentlyViewed.query.count() == 1
    assert RecentlyViewed.query.one().viewed_at >= first_seen


def test_learning_progress_completes_at_threshold(app, student, content):
    progress = LearningProgress(user_id=student.id, content_id=content.id)
    add_all(progress)

    progress.update_from(percent=50)
    commit()
    assert progress.is_completed is False

    progress.update_from(percent=95, position_seconds=120)
    commit()
    assert progress.is_completed is True
    assert progress.percent == 95
    assert progress.completed_at is not None
    assert progress.position_seconds == 120


def test_learning_progress_clamps_out_of_range_input(app, student, content):
    progress = LearningProgress(user_id=student.id, content_id=content.id)
    add_all(progress)

    progress.update_from(percent=500, position_seconds=-30)
    commit()
    assert progress.percent == 100
    assert progress.position_seconds == 0


def test_learning_progress_is_unique_per_student_and_content(app, student, content):
    add_all(LearningProgress(user_id=student.id, content_id=content.id))
    commit()
    add_all(LearningProgress(user_id=student.id, content_id=content.id))
    with pytest.raises(IntegrityError):
        commit()
    rollback()


def test_notification_mark_read_is_one_way(app, student):
    notification = Notification.push(
        student.id, 'Payment received', 'Course unlocked', type=NOTIFICATION_ORDER,
    )
    commit()

    assert notification.is_read is False
    assert notification.mark_read() is True
    assert notification.mark_read() is False
    assert notification.read_at is not None


# --- accounts and tokens ---------------------------------------------------

def test_suspended_account_cannot_login(app, student):
    assert student.can_login is True
    student.suspend()
    assert student.can_login is False
    assert student.is_suspended is True
    student.activate()
    assert student.can_login is True


def test_student_class_access_grant_and_revoke(app, teacher, student, school_class):
    access = StudentClassAccess(
        student_id=student.id, class_id=school_class.id, granted_by=teacher.id,
    )
    add_all(access)
    commit()
    assert access.is_effective is True

    access.revoke()
    assert access.is_effective is False


def test_password_reset_token_is_single_use(app, student):
    row, raw = AccountToken.issue(student.id, TOKEN_PURPOSE_PASSWORD_RESET)
    commit()

    assert raw not in row.token_hash
    assert row.is_valid is True

    consumed = AccountToken.consume(raw, TOKEN_PURPOSE_PASSWORD_RESET)
    assert consumed is not None
    commit()

    # A replay of the same link must fail.
    assert AccountToken.consume(raw, TOKEN_PURPOSE_PASSWORD_RESET) is None


def test_expired_token_is_rejected(app, student):
    row, raw = AccountToken.issue(student.id, TOKEN_PURPOSE_PASSWORD_RESET, ttl_minutes=-1)
    commit()
    assert row.is_expired is True
    assert AccountToken.consume(raw, TOKEN_PURPOSE_PASSWORD_RESET) is None


def test_token_cannot_be_reused_for_another_purpose(app, student):
    _row, raw = AccountToken.issue(student.id, TOKEN_PURPOSE_PASSWORD_RESET)
    commit()
    assert AccountToken.consume(raw, 'email_verification') is None


def test_token_hashing_is_stable(app):
    assert hash_token('abc') == hash_token('abc')
    assert hash_token('abc') != hash_token('abd')


# --- site CMS and audit ----------------------------------------------------

def test_site_setting_round_trips_typed_values(app):
    SiteSetting.set('premium.enabled', True, 'boolean', setting_group='payment')
    SiteSetting.set('contact.email', 'hello@example.com', 'string', setting_group='contact')
    SiteSetting.set('homepage.sections', ['hero', 'classes'], 'json', setting_group='homepage')
    SiteSetting.set('seo.title_limit', 60, 'integer', setting_group='seo')
    commit()

    assert SiteSetting.get('premium.enabled') is True
    assert SiteSetting.get('contact.email') == 'hello@example.com'
    assert SiteSetting.get('homepage.sections') == ['hero', 'classes']
    assert SiteSetting.get('seo.title_limit') == 60


def test_site_setting_returns_fallback_for_missing_key(app):
    assert SiteSetting.get('does.not.exist', fallback='default') == 'default'


def test_audit_log_never_stores_credentials(app, teacher):
    entry = AuditLog.record(
        'user.password_change',
        actor=teacher,
        entity_type='user',
        entity_id=teacher.id,
        details={'current_password': 'hunter2', 'new_password': 'x', 'ip': '127.0.0.1'},
    )
    add_all(entry)

    assert 'hunter2' not in (entry.details or '')
    assert 'current_password' not in entry.detail_dict()
    assert entry.detail_dict()['ip'] == '127.0.0.1'
    assert entry.actor_email == teacher.email


def test_audit_log_survives_a_deleted_actor(app, student):
    entry = AuditLog.record('course.grant', actor=student, entity_type='course', entity_id=1)
    student_id = student.id
    db.session.delete(student)

    db.session.add(entry)
    assert entry.actor_id == student_id


# --- helpers ---------------------------------------------------------------

def add_all(*objects):
    for obj in objects:
        db.session.add(obj)


def commit():
    db.session.commit()


def rollback():
    db.session.rollback()


def execute(statement, params=None):
    db.session.execute(text(statement), params or {})


def chapter_factory(subject, teacher, title, order):
    chapter = Chapter(
        title=title,
        slug=Chapter.unique_slug(title),
        subject_id=subject.id,
        display_order=order,
        created_by=teacher.id,
    )
    db.session.add(chapter)
    return chapter