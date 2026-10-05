"""Server-side visibility and access decisions.

Every rule the master prompt repeats lives here so no route can accidentally
implement its own weaker version:

* authentication
* account status
* publication state
* class permission
* enrollment
* payment status
* content visibility

Two entry points matter. :func:`visible_contents` builds a *filtered query* so a
listing can never leak a locked row, and :func:`can_view_content` answers the
same question for a single record on a detail page.
"""

from datetime import timedelta

from sqlalchemy import or_

from app.extensions import db
from app.models import (
    ACCESS_COURSE_SPECIFIC,
    ACCESS_CLASS_SPECIFIC,
    ACCESS_LOGGED_IN,
    ACCESS_PREMIUM,
    ACCESS_PUBLIC,
    ACCESS_STUDENT_SPECIFIC,
    CONTENT_STATUS_PUBLISHED,
    ENROLLMENT_ACTIVE,
    HIDDEN_CONTENT_STATUSES,
    Content,
    Enrollment,
    RecentlyViewed,
    SchoolClass,
    Subject,
    utcnow,
)

#: Access levels an ordinary signed-in student may read without a purchase.
FREE_ACCESS_LEVELS = (ACCESS_PUBLIC, ACCESS_LOGGED_IN)

#: Access levels that require a verified enrollment or manual grant.
PAID_ACCESS_LEVELS = (ACCESS_PREMIUM, ACCESS_COURSE_SPECIFIC)


def is_active(user):
    """``None`` counts as an anonymous visitor."""
    return bool(user) and getattr(user, 'is_active', True)


def is_privileged(user):
    """Teachers and admins may preview draft / scheduled / archived work."""
    return bool(user) and getattr(user, 'role', None) == 'teacher'


def class_ids_for(user):
    """Every class id the user may browse, from their profile and grants."""
    if not is_active(user):
        return set()
    ids = set()
    if user.class_id:
        ids.add(user.class_id)
    for access in user.class_access:
        if access.is_effective:
            ids.add(access.class_id)
    return ids


def enrolled_course_ids(user):
    """Course ids the user has a live enrollment for."""
    if not is_active(user):
        return set()
    rows = Enrollment.query.filter(
        Enrollment.student_id == user.id,
        Enrollment.status == ENROLLMENT_ACTIVE,
    ).all()
    return {row.course_id for row in rows if row.is_active}


def has_active_enrollment(user, course_id):
    """Single-row check used on detail pages."""
    if not is_active(user):
        return False
    row = Enrollment.query.filter_by(student_id=user.id, course_id=course_id).first()
    return bool(row and row.is_active)


def paid_content_visible_to(user, content):
    """Does ``user`` hold the entitlement this premium record requires?"""
    if not is_active(user):
        return False
    if content.access_level == ACCESS_PREMIUM:
        # Premium items are granted per-course; without a course link the item
        # is only visible to staff.
        course_ids = {lesson.course_id for lesson in content.course_lessons}
        if not course_ids:
            return False
        granted = enrolled_course_ids(user)
        return bool(course_ids & granted)
    if content.access_level == ACCESS_COURSE_SPECIFIC:
        return any(has_active_enrollment(user, cid) for cid in
                   {lesson.course_id for lesson in content.course_lessons})
    if content.access_level == ACCESS_CLASS_SPECIFIC:
        return bool(class_ids_for(user))
    return False


def can_view_content(user, content):
    """Full access decision for one content record."""
    if content is None:
        return False
    if is_privileged(user):
        return True

    # Draft, scheduled and archived records never reach a viewer.
    if content.status in HIDDEN_CONTENT_STATUSES:
        return False
    if content.status != CONTENT_STATUS_PUBLISHED:
        return False

    level = content.access_level

    if level == ACCESS_PUBLIC:
        return True

    if not is_active(user):
        return False

    if level == ACCESS_LOGGED_IN:
        return True

    if level == ACCESS_CLASS_SPECIFIC:
        allowed = class_ids_for(user)
        if not allowed:
            return False
        record_classes = {content.class_id}
        if content.subject is not None and content.subject.class_id:
            record_classes.add(content.subject.class_id)
        return bool(record_classes & allowed)

    if level == ACCESS_STUDENT_SPECIFIC:
        return False

    if level in PAID_ACCESS_LEVELS:
        # A free preview is watchable before purchase.
        return content.is_preview or paid_content_visible_to(user, content)

    return False


def visible_contents(user, query=None):
    """Filter a Content query down to what ``user`` may actually see."""
    query = Content.query if query is None else query
    base = query.filter(Content.status == CONTENT_STATUS_PUBLISHED)

    if is_privileged(user):
        return query

    # An anonymous visitor only ever sees genuinely public records. Treating
    # LOGGED_IN as free here would leak sign-in-only material into listings
    # even though can_view_content() correctly hides the detail page.
    if not is_active(user):
        return base.filter(Content.access_level == ACCESS_PUBLIC)

    clauses = [Content.access_level.in_(FREE_ACCESS_LEVELS)]

    class_ids = class_ids_for(user)
    if class_ids:
        clauses.append(
            (Content.access_level == ACCESS_CLASS_SPECIFIC)
            & (
                Content.class_id.in_(class_ids)
                | Content.subject_id.in_(
                    Subject.query.filter(Subject.class_id.in_(class_ids)).with_entities(Subject.id)
                )
            )
        )

    granted = enrolled_course_ids(user)
    if granted:
        linked_content_ids = _content_ids_for_courses(granted)
        if linked_content_ids:
            clauses.append(
                (
                    Content.access_level.in_([ACCESS_PREMIUM, ACCESS_COURSE_SPECIFIC])
                    & (
                        Content.id.in_(linked_content_ids)
                        | Content.is_preview.is_(True)
                    )
                )
            )

    return base.filter(or_(*clauses))


def _content_ids_for_courses(course_ids):
    """Content reachable through lessons of the given enrolled courses."""
    from app.models import CourseLesson

    rows = (
        db.session.query(CourseLesson.content_id)
        .filter(CourseLesson.course_id.in_(list(course_ids)))
        .distinct()
        .all()
    )
    return {row[0] for row in rows}


def can_view_course(user, course):
    if course is None:
        return False
    if is_privileged(user):
        return True
    if course.status != CONTENT_STATUS_PUBLISHED:
        return False
    if course.access_level in FREE_ACCESS_LEVELS:
        return True
    if not is_active(user):
        return False
    return has_active_enrollment(user, course.id)


def can_view_lesson(user, lesson, course=None):
    """Free-preview lessons are open; the rest need an enrollment."""
    if lesson is None:
        return False
    if is_privileged(user):
        return True
    course = course or lesson.course
    if course is None or not can_view_course(user, course):
        return False
    if not is_active(user):
        # Anonymous visitors may still read free previews of a free course.
        return bool(lesson.is_preview) and course.access_level in FREE_ACCESS_LEVELS
    return bool(lesson.is_preview) or has_active_enrollment(user, course.id)


def published_classes():
    return SchoolClass.query.filter(
        SchoolClass.is_enabled.is_(True),
        SchoolClass.status == 'active',
    ).order_by(SchoolClass.display_order, SchoolClass.name)


def published_subjects(class_id=None):
    query = Subject.query.filter(
        Subject.is_enabled.is_(True),
        Subject.status == CONTENT_STATUS_PUBLISHED,
    )
    if class_id:
        query = query.filter(Subject.class_id == class_id)
    return query.order_by(Subject.display_order, Subject.name)


def visible_classes_for(user):
    """Classes the user may browse (all enabled ones, minus archived)."""
    classes = list(published_classes())
    if is_privileged(user):
        return classes
    allowed = class_ids_for(user)
    if not allowed:
        return classes
    return [item for item in classes if item.id in allowed]


def record_view(user, content):
    """Track a view for 'Recently Viewed' without breaking the page on error."""
    if not is_active(user) or content is None:
        return None
    from app.models import BookmarkTarget

    row = RecentlyViewed.record(user.id, BookmarkTarget.CONTENT, content.id)
    try:
        db.session.commit()
    except Exception:  # pragma: no cover - history is best effort
        db.session.rollback()
        return None
    return row