"""Public ClassNext website.

Every page here renders real database rows through
:mod:`app.services.access`; no statistic, count or listing on this blueprint is
hard-coded. Visibility is always decided on the server, never in a template.
"""

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.extensions import db, limiter
from app.models import (
    ACCESS_PREMIUM,
    CONTENT_STATUS_PUBLISHED,
    Announcement,
    Chapter,
    ContactEnquiry,
    Content,
    Course,
    CourseLesson,
    Faq,
    SchoolClass,
    Subject,
    TeacherProfile,
)
from app.services import access
from app.services.sanitizer import plain_text
from app.services.seo import absolute_url, build_meta, iter_public_urls, xml_escape

public_bp = Blueprint('public', __name__)

CONTENT_PER_PAGE = 12
COURSE_PER_PAGE = 9

#: Content types grouped into the public library filters.
NOTE_TYPES = ('notes', 'study_material', 'pdf_resource', 'reference_link')
VIDEO_TYPES = ('video_lesson',)
AUDIO_TYPES = ('audio',)
IMAGE_TYPES = ('image',)


def current_user():
    """Session user, or ``None`` for anonymous visitors."""
    if 'user_id' not in session:
        return None
    from app.models import User

    return db.session.get(User, session['user_id'])


def _slug_param(value):
    return (value or '').strip().lower()


# ── Home ────────────────────────────────────────────────────────────────

@public_bp.route('/')
def index():
    """Marketing home for visitors, dashboard redirect for signed-in users."""
    user = current_user()
    if user is not None:
        if user.is_teacher:
            return redirect(url_for('teacher.dashboard'))
        return redirect(url_for('student.dashboard'))

    classes = access.published_classes().all()
    featured_classes = [item for item in classes if item.is_enabled][:6]

    latest = access.visible_contents(None) \
        .order_by(Content.published_at.desc().nullslast(), Content.id.desc()) \
        .limit(6).all()

    courses = Course.query.filter(
        Course.status == CONTENT_STATUS_PUBLISHED,
        Course.is_featured.is_(True),
    ).order_by(Course.published_at.desc().nullslast()).limit(3).all()

    if not courses:
        courses = Course.query.filter(
            Course.status == CONTENT_STATUS_PUBLISHED,
        ).order_by(Course.published_at.desc().nullslast()).limit(3).all()

    notices = Announcement.query.filter_by(is_published=True) \
        .order_by(Announcement.published_at.desc().nullslast()) \
        .limit(3).all()

    profile = TeacherProfile.query.first()

    return render_template(
        'public/home.html',
        meta=build_meta(
            description=current_app.config['APP_DESCRIPTION'],
            path='/',
        ),
        classes=featured_classes,
        total_classes=len(classes),
        latest=latest,
        courses=courses,
        notices=notices,
        profile=profile,
        total_subjects=Subject.query.filter_by(is_enabled=True).count(),
    )


# ── Catalogue ───────────────────────────────────────────────────────────

@public_bp.route('/classes')
def classes():
    items = access.published_classes().all()
    return render_template(
        'public/classes.html',
        meta=build_meta(title='Classes', path='/classes',
                        description='Browse every class available on ClassNext.'),
        classes=items,
    )


@public_bp.route('/classes/<slug>')
def class_detail(slug):
    item = SchoolClass.query.filter_by(slug=_slug_param(slug)).first()
    if item is None or not item.is_available:
        abort(404)

    subjects = access.published_subjects(class_id=item.id).all()
    chapters = Chapter.query.filter_by(
        class_id=item.id,
        status=CONTENT_STATUS_PUBLISHED,
    ).order_by(Chapter.display_order, Chapter.title).all()

    content_counts = {}
    if chapters:
        rows = (
            db.session.query(
                Content.chapter_id.label('chapter_id'),
                db.func.count(Content.id).label('total'),
            )
            .filter(
                Content.chapter_id.in_([chapter.id for chapter in chapters]),
                Content.status == CONTENT_STATUS_PUBLISHED,
            )
            .group_by(Content.chapter_id)
            .all()
        )
        content_counts = {row.chapter_id: row.total for row in rows}

    courses = Course.query.filter(
        Course.status == CONTENT_STATUS_PUBLISHED,
        Course.class_id == item.id,
    ).order_by(Course.published_at.desc().nullslast()).all()

    return render_template(
        'public/class_detail.html',
        meta=build_meta(title=item.name, path=f'/classes/{item.slug}',
                        description=item.description or f'Subjects and chapters for {item.name}.'),
        item=item,
        subjects=subjects,
        chapters=chapters,
        content_counts=content_counts,
        courses=courses,
    )


@public_bp.route('/subjects/<slug>')
def subject_detail(slug):
    item = Subject.query.filter_by(slug=_slug_param(slug)).first()
    if item is None or not item.is_enabled:
        abort(404)
    if item.status != CONTENT_STATUS_PUBLISHED and not access.is_privileged(current_user()):
        abort(404)

    user = current_user()
    chapters = item.chapters.filter_by(status=CONTENT_STATUS_PUBLISHED) \
        .order_by(Chapter.display_order, Chapter.title).all()

    page = request.args.get('page', 1, type=int)
    pagination = access.visible_contents(user, item.content).order_by(
        Content.content_type, Content.title
    ).paginate(page=page, per_page=CONTENT_PER_PAGE, error_out=False)

    return render_template(
        'public/subject_detail.html',
        meta=build_meta(title=item.name, path=f'/subjects/{item.slug}',
                        description=item.description or f'{item.name} notes and videos.'),
        item=item,
        chapters=chapters,
        pagination=pagination,
    )


@public_bp.route('/chapters/<slug>')
def chapter_detail(slug):
    item = Chapter.query.filter_by(slug=_slug_param(slug)).first()
    if item is None:
        abort(404)
    if item.status != CONTENT_STATUS_PUBLISHED and not access.is_privileged(current_user()):
        abort(404)

    user = current_user()
    pagination = access.visible_contents(user, item.content).order_by(
        Content.content_type, Content.title
    ).paginate(page=request.args.get('page', 1, type=int),
               per_page=CONTENT_PER_PAGE, error_out=False)

    return render_template(
        'public/chapter_detail.html',
        meta=build_meta(title=item.title, path=f'/chapters/{item.slug}',
                        description=item.description or f'Lessons in {item.title}.'),
        item=item,
        pagination=pagination,
    )


@public_bp.route('/content/<slug>')
def content_detail(slug):
    item = Content.query.filter_by(slug=_slug_param(slug)).first()
    if item is None:
        abort(404)

    user = current_user()
    if not access.can_view_content(user, item):
        # 404 rather than 403 so a premium URL cannot be probed for existence.
        abort(404)

    access.record_view(user, item)

    related = access.visible_contents(user).filter(
        Content.subject_id == item.subject_id,
        Content.id != item.id,
    ).order_by(Content.published_at.desc().nullslast()).limit(4).all()

    return render_template(
        'public/content_detail.html',
        meta=build_meta(title=item.title, path=f'/content/{item.slug}',
                        description=item.description or item.summary(155),
                        og_type='article',
                        noindex=item.access_level == ACCESS_PREMIUM),
        item=item,
        related=related,
        chapters=_sibling_chapters(item),
    )


def _sibling_chapters(content):
    if content.subject_id is None:
        return []
    return (
        Subject.query.get(content.subject_id).chapters
        .filter_by(status=CONTENT_STATUS_PUBLISHED)
        .order_by(Chapter.display_order, Chapter.title)
        .all()
    )


# ── Library listings ────────────────────────────────────────────────────

@public_bp.route('/notes')
@public_bp.route('/videos')
@public_bp.route('/free-resources')
def library(kind='notes'):
    """Notes / videos / free resources share one filtered listing."""
    user = current_user()
    types = _types_for_kind(kind)

    query = access.visible_contents(user).filter(Content.content_type.in_(types))
    query = _apply_library_filters(query, user)

    pagination = query.paginate(
        page=request.args.get('page', 1, type=int),
        per_page=CONTENT_PER_PAGE, error_out=False,
    )

    return render_template(
        'public/library.html',
        meta=build_meta(title=_title_for_kind(kind), path=f'/{kind}',
                        description=_description_for_kind(kind)),
        kind=kind,
        types=types,
        pagination=pagination,
        classes=access.published_classes().all(),
        selected_class=request.args.get('class', type=int),
        selected_subject=request.args.get('subject', type=int),
        subjects=Subject.query.filter_by(is_enabled=True).order_by(Subject.name).all(),
    )


def _types_for_kind(kind):
    if kind == 'videos':
        return VIDEO_TYPES
    if kind == 'free-resources':
        return NOTE_TYPES + AUDIO_TYPES + IMAGE_TYPES + VIDEO_TYPES
    return NOTE_TYPES


def _title_for_kind(kind):
    return {
        'notes': 'Notes & Study Material',
        'videos': 'Video Lessons',
        'free-resources': 'Free Resources',
    }.get(kind, 'Library')


def _description_for_kind(kind):
    return {
        'notes': 'Downloadable notes, PDFs and study material organised by class and subject.',
        'videos': 'Watch free video lessons organised by class, subject and chapter.',
        'free-resources': 'Every free note, PDF, video and audio resource on ClassNext.',
    }.get(kind, 'Browse the ClassNext library.')


def _apply_library_filters(query, user):
    subject_id = request.args.get('subject', type=int)
    class_id = request.args.get('class', type=int)
    tag = (request.args.get('tag') or '').strip()

    if subject_id:
        query = query.filter(Content.subject_id == subject_id)
    if class_id:
        query = query.filter(
            Content.class_id == class_id
        ) | query.filter(Content.subject_id.in_(
            Subject.query.filter_by(class_id=class_id).with_entities(Subject.id)
        ))
    if tag:
        query = query.filter(Content.tags.ilike(f'%{tag}%'))

    if access.is_privileged(user):
        return query
    return query.order_by(Content.published_at.desc().nullslast(), Content.id.desc())


# ── Courses and premium ────────────────────────────────────────────────

@public_bp.route('/courses')
def courses():
    user = current_user()
    query = Course.query.filter(Course.status == CONTENT_STATUS_PUBLISHED)

    class_id = request.args.get('class', type=int)
    if class_id:
        query = query.filter(Course.class_id == class_id)

    pagination = query.paginate(
        page=request.args.get('page', 1, type=int),
        per_page=COURSE_PER_PAGE, error_out=False,
    )

    return render_template(
        'public/courses.html',
        meta=build_meta(title='Courses', path='/courses',
                        description='Structured courses with sections, lessons and progress tracking.'),
        pagination=pagination,
        classes=access.published_classes().all(),
        selected_class=class_id,
        enrolled=_enrolled_course_ids(user),
    )


@public_bp.route('/premium')
def premium():
    """Premium course showcase. Shows nothing until a gateway is configured."""
    items = Course.query.filter(
        Course.status == CONTENT_STATUS_PUBLISHED,
        Course.access_level == ACCESS_PREMIUM,
    ).order_by(Course.is_featured.desc(), Course.published_at.desc().nullslast()).all()

    return render_template(
        'public/premium.html',
        meta=build_meta(title='Premium Courses', path='/premium',
                        description='Premium courses with secure, server-verified enrollment.'),
        courses=items,
        premium_enabled=current_app.config['PREMIUM_ENABLED'],
    )


@public_bp.route('/courses/<slug>')
def course_detail(slug):
    item = Course.query.filter_by(slug=_slug_param(slug)).first()
    if item is None:
        abort(404)

    user = current_user()
    if item.status != CONTENT_STATUS_PUBLISHED and not access.is_privileged(user):
        abort(404)

    # The course *page* is public marketing: price, outline and free previews
    # are shown to anyone. Only the individual lessons are gated, by
    # access.can_view_lesson, so a locked lesson never leaks its media.
    sections = item.ordered_sections()
    lessons = item.lessons.order_by(CourseLesson.display_order, CourseLesson.id).all()

    related = Course.query.filter(
        Course.id != item.id,
        Course.status == CONTENT_STATUS_PUBLISHED,
        Course.subject_id == item.subject_id,
    ).limit(3).all()

    return render_template(
        'public/course_detail.html',
        meta=build_meta(title=item.title, path=f'/courses/{item.slug}',
                        description=item.summary(155), og_type='article'),
        item=item,
        sections=sections,
        lessons=lessons,
        related=related,
        owned=access.has_active_enrollment(user, item.id),
        premium_enabled=current_app.config['PREMIUM_ENABLED'],
    )


def _enrolled_course_ids(user):
    if not access.is_active(user):
        return set()
    return access.enrolled_course_ids(user)


# ── Notices ─────────────────────────────────────────────────────────────

@public_bp.route('/notices')
def notices():
    items = Announcement.query.filter_by(is_published=True) \
        .order_by(Announcement.published_at.desc().nullslast(), Announcement.id.desc()).all()
    return render_template(
        'public/notices.html',
        meta=build_meta(title='Notices', path='/notices',
                        description='Announcements and updates from the teacher.'),
        notices=items,
    )


# ── Search ──────────────────────────────────────────────────────────────

@public_bp.route('/search')
def search():
    """Searches only what the visitor may already see."""
    user = current_user()
    term = (request.args.get('q') or '').strip()[:120]

    results = []
    if term:
        like = f'%{term}%'
        results = access.visible_contents(user).filter(
            Content.title.ilike(like) | Content.description.ilike(like)
            | Content.tags.ilike(like) | Content.topic.ilike(like)
        ).order_by(Content.published_at.desc().nullslast()).limit(60).all()

    return render_template(
        'public/search.html',
        meta=build_meta(title=f'Search: {term}' if term else 'Search', path='/search',
                        description='Search classes, subjects, chapters, notes and videos.',
                        noindex=True),
        term=term,
        results=results,
    )


# ── Static pages ────────────────────────────────────────────────────────

@public_bp.route('/about')
def about():
    return render_template(
        'public/about.html',
        meta=build_meta(title='About', path='/about',
                        description=f'About {app_teacher()} and ClassNext.'),
        profile=TeacherProfile.query.first(),
    )


@public_bp.route('/faq')
def faq():
    items = Faq.query.filter_by(status=CONTENT_STATUS_PUBLISHED) \
        .order_by(Faq.category, Faq.display_order, Faq.id).all()
    return render_template(
        'public/faq.html',
        meta=build_meta(title='FAQ', path='/faq',
                        description='Frequently asked questions about ClassNext.'),
        faqs=items,
    )


@public_bp.route('/contact')
def contact():
    return render_template(
        'public/contact.html',
        meta=build_meta(title='Contact', path='/contact',
                        description='Send a message to the ClassNext team.'),
        sent=request.args.get('sent') == '1',
    )


@public_bp.route('/contact', methods=['POST'])
@limiter.limit('5 per hour', methods=['POST'])
def contact_submit():
    name = plain_text(request.form.get('name', ''), 120)
    email = plain_text(request.form.get('email', ''), 255)
    subject = plain_text(request.form.get('subject', ''), 200)
    message = plain_text(request.form.get('message', ''), 4000)

    errors = []
    if len(name) < 2:
        errors.append('Please enter your name.')
    if '@' not in email or '.' not in email.split('@')[-1]:
        errors.append('Please enter a valid email address.')
    if len(message) < 10:
        errors.append('Please write a message of at least 10 characters.')

    if errors:
        return render_template(
            'public/contact.html',
            meta=build_meta(title='Contact', path='/contact'),
            sent=False,
            errors=errors,
            form={'name': name, 'email': email, 'subject': subject, 'message': message},
        ), 400

    enquiry = ContactEnquiry(
        name=name, email=email, subject=subject or None, message=message
    )
    db.session.add(enquiry)
    db.session.commit()

    return redirect(url_for('public.contact', sent=1))


@public_bp.route('/legal/<page>')
def legal(page):
    pages = {
        'privacy': ('Privacy Policy', 'public/legal/privacy.html'),
        'terms': ('Terms & Conditions', 'public/legal/terms.html'),
        'refund-policy': ('Refund Policy', 'public/legal/refund.html'),
    }
    entry = pages.get(page)
    if entry is None:
        abort(404)
    heading, template = entry
    return render_template(
        template,
        meta=build_meta(title=heading, path=f'/legal/{page}'),
        heading=heading,
    )


def app_teacher():
    return current_app.config['TEACHER_NAME']


# ── SEO endpoints ───────────────────────────────────────────────────────

@public_bp.route('/sitemap.xml')
def sitemap():
    entries = list(iter_public_urls())
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path, lastmod, changefreq, priority in entries:
        parts.append('  <url>')
        parts.append(f'    <loc>{xml_escape(absolute_url(path))}</loc>')
        if lastmod is not None:
            parts.append(f'    <lastmod>{lastmod.strftime("%Y-%m-%d")}</lastmod>')
        if changefreq:
            parts.append(f'    <changefreq>{xml_escape(changefreq)}</changefreq>')
        if priority:
            parts.append(f'    <priority>{xml_escape(priority)}</priority>')
        parts.append('  </url>')
    parts.append('</urlset>')
    return '\n'.join(parts), 200, {'Content-Type': 'application/xml; charset=utf-8'}


@public_bp.route('/robots.txt')
def robots():
    base = absolute_url('')
    lines = [
        'User-agent: *',
        'Disallow: /student/',
        'Disallow: /teacher/',
        'Disallow: /auth/',
        'Disallow: /files/',
        'Disallow: /api/',
        'Allow: /',
        f'Sitemap: {base}/sitemap.xml',
    ]
    return '\n'.join(lines), 200, {'Content-Type': 'text/plain; charset=utf-8'}


# ── Offline ─────────────────────────────────────────────────────────────

@public_bp.route('/offline')
def offline():
    """Offline fallback page used by the service worker."""
    return render_template('public/offline.html')