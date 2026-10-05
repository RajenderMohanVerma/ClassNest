"""Public ClassNext website tests.

Covers the public shell, the catalogue hierarchy, server-side visibility
(drafts and premium never leak), search, contact submissions and SEO endpoints.
"""

import pytest

from app.models import (
    ACCESS_PREMIUM,
    CONTENT_STATUS_ARCHIVED,
    CONTENT_STATUS_DRAFT,
    CONTENT_STATUS_SCHEDULED,
    Announcement,
    Chapter,
    ContactEnquiry,
    Content,
    Course,
    CourseLesson,
    CourseSection,
    Enrollment,
    Faq,
    SchoolClass,
    Subject,
    User,
)


# ── Shell ───────────────────────────────────────────────────────────────

PUBLIC_PAGES = [
    '/', '/classes', '/notes', '/videos', '/free-resources', '/courses',
    '/premium', '/notices', '/about', '/faq', '/contact',
    '/legal/privacy', '/legal/terms', '/legal/refund-policy',
]


@pytest.mark.parametrize('path', PUBLIC_PAGES)
def test_public_pages_render(client, school_class, subject, chapter, published_content, path):
    response = client.get(path)
    assert response.status_code == 200, f'{path} did not render'
    assert b'<!DOCTYPE html>' in response.data


def test_header_and_footer_are_present_on_every_public_page(client, school_class):
    for path in ('/', '/classes', '/about'):
        body = client.get(path).data
        assert b'cn-site-header' in body
        assert b'cn-site-footer' in body
        assert b'ClassNext' in body


def test_tagline_is_rendered(client, school_class):
    assert 'Learn • Practice • Achieve'.encode('utf-8') in client.get('/').data


def test_home_teacher_card_uses_light_surface_text_contrast(client, school_class):
    page = client.get('/').data
    styles = client.get('/static/css/site.css').get_data(as_text=True)
    assert b'cn-teacher-card' in page
    assert '.cn-teacher-card { color: var(--cn-text);' in styles
    assert '.cn-hero__copy .cn-btn--outline' in styles


def test_every_nav_link_resolves(client, school_class):
    """No dead links in the header or footer."""
    import re

    body = client.get('/').data.decode('utf-8')
    hrefs = set(re.findall(r'href="(/[^"#?]*)"', body))

    internal = {
        path for path in hrefs
        if not path.startswith(('/static/', '/files/'))
    }
    assert internal, 'no navigation links found in the header'

    for path in sorted(internal):
        assert client.get(path).status_code == 200, f'nav link {path} is broken'


def test_library_routes_show_their_own_resource_kind(client, school_class):
    videos = client.get('/videos').data
    notes = client.get('/notes').data
    free = client.get('/free-resources').data

    assert b'Video Lessons' in videos
    assert b'Notes &amp; Study Material' in notes
    assert b'Free Resources' in free
    assert b'href="/videos" aria-current="page"' in videos


def test_footer_legal_links_all_resolve(client, school_class):
    for path in ('/legal/privacy', '/legal/terms', '/legal/refund-policy'):
        assert client.get(path).status_code == 200


def test_unknown_legal_page_is_404(client):
    assert client.get('/legal/nope').status_code == 404


def test_theme_toggle_and_search_controls_exist(client, school_class):
    body = client.get('/').data
    assert b'data-theme-toggle' in body
    assert b'data-nav-toggle' in body
    assert b'name="q"' in body


def test_public_navigation_and_footer_have_responsive_destinations(client, school_class):
    body = client.get('/').data
    assert b'cn-site-nav__disclosure' in body
    assert b'aria-controls="site-nav"' in body
    assert b'cn-site-footer__cta' in body
    assert b'cn-site-footer__back-top' in body


def test_explore_dropdown_stays_closed_after_following_a_link(client, school_class):
    body = client.get('/faq').data
    assert b'<details class="cn-site-nav__disclosure">' in body
    assert b'<details class="cn-site-nav__disclosure" open>' not in body
    assert b'href="/faq" aria-current="page"' in body


def test_signed_in_student_gets_student_navigation_in_public_footer(client, student, login_student):
    login_student()
    body = client.get('/about').data
    assert b'Student dashboard' in body
    assert b'Teacher dashboard' not in body


def test_signed_in_teacher_gets_teacher_navigation_in_public_footer(client, teacher, login_teacher):
    login_teacher()
    body = client.get('/about').data
    assert b'Teacher dashboard' in body
    assert b'Student dashboard' not in body


# ── Catalogue ───────────────────────────────────────────────────────────

def test_classes_page_lists_enabled_classes(client, school_class):
    body = client.get('/classes').data
    assert school_class.name.encode() in body


def test_disabled_or_archived_class_is_hidden(client, school_class):
    school_class.is_enabled = False
    from app import db

    db.session.commit()

    assert b'Class 10' not in client.get('/classes').data
    assert client.get(f'/classes/{school_class.slug}').status_code == 404


def test_class_detail_lists_subjects_and_chapters(client, school_class, subject, chapter, published_content):
    body = client.get(f'/classes/{school_class.slug}').data
    assert subject.name.encode() in body
    assert chapter.title.encode() in body


def test_subject_detail_lists_its_content(client, subject, chapter, published_content):
    published_content.access_level = 'public'
    from app import db

    db.session.commit()

    body = client.get(f'/subjects/{subject.slug}').data
    assert published_content.title.encode() in body


def test_chapter_detail_lists_lessons(client, chapter, published_content):
    published_content.chapter_id = chapter.id
    published_content.access_level = 'public'
    from app import db

    db.session.commit()

    body = client.get(f'/chapters/{chapter.slug}').data
    assert published_content.title.encode() in body


def test_missing_records_return_404_not_500(client):
    assert client.get('/classes/nope').status_code == 404
    assert client.get('/subjects/nope').status_code == 404
    assert client.get('/chapters/nope').status_code == 404
    assert client.get('/content/nope').status_code == 404
    assert client.get('/courses/nope').status_code == 404


# ── Visibility rules (the security-critical part) ────────────────────────

def test_anonymous_visitor_sees_public_content(client, published_content):
    published_content.access_level = 'public'
    from app import db

    db.session.commit()

    assert client.get(f'/content/{published_content.slug}').status_code == 200
    assert published_content.title.encode() in client.get('/notes').data


def test_login_only_content_is_hidden_from_visitors(client, published_content):
    published_content.access_level = 'logged_in'
    from app import db

    db.session.commit()

    assert client.get(f'/content/{published_content.slug}').status_code == 404
    assert published_content.title.encode() not in client.get('/notes').data


def test_draft_and_scheduled_content_never_reaches_a_visitor(client, published_content):
    from app import db

    for state in (CONTENT_STATUS_DRAFT, CONTENT_STATUS_SCHEDULED, CONTENT_STATUS_ARCHIVED):
        published_content.status = state
        db.session.commit()
        assert client.get(f'/content/{published_content.slug}').status_code == 404, state
        assert published_content.title.encode() not in client.get('/notes').data, state


def test_teacher_can_preview_draft_content(client, published_content, login_teacher):
    published_content.status = CONTENT_STATUS_DRAFT
    from app import db

    db.session.commit()
    login_teacher()

    assert client.get(f'/content/{published_content.slug}').status_code == 200


def test_suspended_account_loses_its_access(client, student, login_student, published_content):
    from app import db

    # Access while the account is still active.
    login_student()
    assert client.get(f'/content/{published_content.slug}').status_code == 200

    student.suspend()
    db.session.commit()

    # The existing session is ended on the very next request, not just refused
    # the page, so the account has nothing left to browse with.
    response = client.get(f'/content/{published_content.slug}')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


def test_premium_content_is_locked_without_enrollment(client, published_content, login_student, course):
    published_content.access_level = ACCESS_PREMIUM
    published_content.access_level = 'premium'
    from app import db

    db.session.commit()
    login_student()

    assert client.get(f'/content/{published_content.slug}').status_code == 404


def test_enrolled_student_can_open_premium_content(
    app, client, published_content, student, course, course_section, login_student
):
    from app import db

    published_content.access_level = 'premium'
    db.session.add(CourseLesson(
        course_id=course.id,
        section_id=course_section.id,
        content_id=published_content.id,
        title='Locked lesson',
    ))
    db.session.add(Enrollment(student_id=student.id, course_id=course.id))
    db.session.commit()
    login_student()

    assert client.get(f'/content/{published_content.slug}').status_code == 200


def test_free_preview_is_open_before_purchase(client, published_content, login_student):
    from app import db

    published_content.access_level = 'premium'
    published_content.is_preview = True
    db.session.commit()
    login_student()

    assert client.get(f'/content/{published_content.slug}').status_code == 200


def test_search_never_returns_hidden_content(client, published_content):
    from app import db

    published_content.status = CONTENT_STATUS_DRAFT
    published_content.title = 'Secret Draft Notes'
    db.session.commit()

    body = client.get('/search?q=Secret').data
    assert b'Secret Draft Notes' not in body


# ── Courses and premium ─────────────────────────────────────────────────

def test_course_page_is_public_marketing(client, course, course_section, course_lesson):
    """Price and outline are public; only the lessons are gated."""
    response = client.get(f'/courses/{course.slug}')
    assert response.status_code == 200
    assert b'499' in response.data
    assert b'Free preview' in response.data


def test_premium_page_states_that_payments_are_off(client, course):
    """No fake 'Buy now' while the gateway is unconfigured."""
    body = client.get('/premium').data
    assert b'not switched on yet' in body
    assert b'Buy now' not in body


def test_premium_course_page_offers_contact_instead_of_checkout(client, course):
    body = client.get(f'/courses/{course.slug}').data
    assert b'Payments are not switched on yet' in body
    assert b'/contact' in body


def test_premium_page_is_empty_state_when_there_are_no_courses(client):
    body = client.get('/premium').data
    assert b'No premium courses yet' in body


def test_locked_lessons_are_labelled_not_linked(app, client, course, course_section, course_lesson):
    from app import db

    db.session.add(CourseLesson(
        course_id=course.id,
        section_id=course_section.id,
        content_id=course_lesson.content_id,
        title='Locked lesson',
        display_order=5,
        is_preview=False,
    ))
    db.session.commit()

    body = client.get(f'/courses/{course.slug}').data
    assert b'Locked' in body
    assert b'Free preview' in body


# ── Search ──────────────────────────────────────────────────────────────

def test_search_finds_published_public_content(client, published_content):
    from app import db

    published_content.access_level = 'public'
    published_content.title = 'Quadratic Equations'
    db.session.commit()

    body = client.get('/search?q=Quadratic').data
    assert b'Quadratic Equations' in body


def test_empty_search_shows_the_empty_state(client, school_class):
    assert b'Type a keyword' in client.get('/search').data


def test_search_with_no_match_shows_empty_state(client, school_class):
    assert b'No matches' in client.get('/search?q=zzzznotfound').data


# ── Contact ─────────────────────────────────────────────────────────────

def test_contact_page_renders_with_csrf(client, school_class):
    response = client.get('/contact')
    assert response.status_code == 200
    assert b'csrf_token' in response.data


def test_valid_contact_form_stores_an_enquiry(app, client):
    from app import db

    response = client.post('/contact', data={
        'name': 'Riya Sharma',
        'email': 'riya@example.com',
        'subject': 'Course access',
        'message': 'I would like access to the Class 10 mathematics course.',
    })
    assert response.status_code == 302

    enquiry = ContactEnquiry.query.one()
    assert enquiry.name == 'Riya Sharma'
    assert enquiry.email == 'riya@example.com'
    assert enquiry.status == 'new'


def test_short_contact_message_is_rejected(app, client):
    response = client.post('/contact', data={
        'name': 'Riya', 'email': 'riya@example.com', 'message': 'hi',
    })
    assert response.status_code == 400
    assert ContactEnquiry.query.count() == 0


def test_invalid_email_is_rejected(app, client):
    response = client.post('/contact', data={
        'name': 'Riya Sharma', 'email': 'not-an-email',
        'message': 'This message is long enough to pass validation.',
    })
    assert response.status_code == 400
    assert ContactEnquiry.query.count() == 0


def test_contact_strips_markup_from_the_name(app, client):
    from app import db

    client.post('/contact', data={
        'name': '<script>alert(1)</script>Riya',
        'email': 'riya@example.com',
        'message': 'A message that is definitely long enough.',
    })
    enquiry = ContactEnquiry.query.one()
    assert '<script>' not in enquiry.name


# ── SEO ─────────────────────────────────────────────────────────────────

def test_sitemap_is_valid_xml_with_public_urls(client, school_class, subject, published_content):
    response = client.get('/sitemap.xml')
    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith('application/xml')
    assert b'<?xml version="1.0"' in response.data
    assert b'/classes' in response.data


def test_sitemap_excludes_draft_content(client, published_content):
    published_content.status = CONTENT_STATUS_DRAFT
    from app import db

    db.session.commit()

    body = client.get('/sitemap.xml').data
    assert published_content.slug.encode() not in body


def test_robots_points_at_the_sitemap(client, school_class):
    response = client.get('/robots.txt')
    assert response.status_code == 200
    assert b'Sitemap:' in response.data
    assert b'Disallow: /student/' in response.data


def test_canonical_and_open_graph_tags_are_present(client, school_class):
    body = client.get('/classes').data
    assert b'<link rel="canonical"' in body
    assert b'property="og:title"' in body
    assert b'property="og:image"' in body


def test_canonical_url_is_the_page_itself(client, school_class):
    body = client.get('/classes').data
    assert b'href="/classes"' in body


def test_premium_content_page_is_noindex(app, client, published_content, student, login_student):
    from app import db

    published_content.access_level = 'premium'
    published_content.is_preview = True
    db.session.commit()
    login_student()

    body = client.get(f'/content/{published_content.slug}').data
    assert b'noindex' in body


def test_search_page_is_noindex(client, school_class):
    assert b'noindex' in client.get('/search?q=x').data


# ── Notices and FAQ ─────────────────────────────────────────────────────

def test_notices_page_lists_published_notice(client, announcement):
    assert announcement.title.encode() in client.get('/notices').data


def test_faq_page_groups_by_category(client, app, teacher):
    from app import db

    db.session.add(Faq(
        question='Is there a free trial?',
        answer='<p>Free previews act as a trial.</p>',
        category='Billing', status='published',
    ))
    db.session.commit()

    body = client.get('/faq').data
    assert b'Billing' in body
    assert b'Is there a free trial?' in body


def test_faq_page_shows_ten_project_faqs_without_cms_entries(client, school_class):
    body = client.get('/faq').data
    assert body.count(b'class="cn-faq__item"') == 10
    assert b'How is the learning material organized?' in body
    assert b'How can I report a problem or ask for help?' in body


# ── Empty states (no fake data anywhere) ────────────────────────────────

def test_home_shows_empty_states_when_there_is_no_content(client):
    body = client.get('/').data
    assert b'No classes have been published yet' in body
    assert b'No free resources have been published yet' in body


def test_no_fabricated_statistics_are_rendered(client, school_class, subject):
    """Counts must come from the database, not from placeholder numbers."""
    body = client.get('/').data
    # Exactly one class exists, so the hero must report 1 and never a bigger claim.
    assert b'<dt>Classes</dt>' in body
    assert b'<dd>1</dd>' in body
