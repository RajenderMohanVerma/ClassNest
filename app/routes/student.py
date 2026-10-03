from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, session, url_for)

from app.extensions import db
from app.models.announcement import Announcement
from app.models.content import CONTENT_TYPE_LABELS, Content
from app.models.subject import Subject
from app.models.user import User
from app.services.accounts import change_password, update_profile
from app.services.decorators import student_required

student_bp = Blueprint('student', __name__)

CONTENT_PER_PAGE = 12
ANNOUNCEMENTS_PER_PAGE = 10


def _published_content_query():
    return Content.query.filter(Content.status == 'published')


def _published_type_counts():
    rows = (
        db.session.query(Content.content_type, db.func.count(Content.id))
        .filter(Content.status == 'published')
        .group_by(Content.content_type)
        .all()
    )
    return {content_type: count for content_type, count in rows}


@student_bp.route('/dashboard')
@student_required
def dashboard():
    recent_content = _published_content_query().order_by(
        Content.published_at.desc().nullslast(), Content.created_at.desc()
    ).limit(6).all()

    subjects = Subject.query.order_by(Subject.name).all()

    announcements = Announcement.query.filter_by(is_published=True).order_by(
        Announcement.published_at.desc().nullslast()
    ).limit(3).all()

    return render_template(
        'student/dashboard.html',
        recent_content=recent_content,
        subjects=subjects,
        announcements=announcements,
    )


@student_bp.route('/subjects')
@student_required
def subjects():
    all_subjects = Subject.query.order_by(Subject.name).all()
    return render_template('student/subjects.html', subjects=all_subjects)


@student_bp.route('/subjects/<slug>')
@student_required
def subject_detail(slug):
    subj = Subject.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = _published_content_query().filter_by(subject_id=subj.id).order_by(
        Content.published_at.desc().nullslast(), Content.created_at.desc()
    ).paginate(page=page, per_page=CONTENT_PER_PAGE, error_out=False)

    return render_template(
        'student/subject_detail.html', subject=subj, pagination=pagination
    )


@student_bp.route('/content')
@student_required
def content_library():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    subject_filter = request.args.get('subject', '', type=int)
    type_filter = request.args.get('type', '').strip()
    sort = request.args.get('sort', 'newest')

    query = _published_content_query()

    if search:
        pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Content.title.ilike(pattern),
                Content.description.ilike(pattern),
                Content.tags.ilike(pattern),
                Content.topic.ilike(pattern),
            )
        )
    if subject_filter:
        query = query.filter_by(subject_id=subject_filter)
    if type_filter in CONTENT_TYPE_LABELS:
        query = query.filter_by(content_type=type_filter)

    query = query.order_by(
        Content.created_at.asc() if sort == 'oldest' else Content.created_at.desc()
    )

    pagination = query.paginate(page=page, per_page=CONTENT_PER_PAGE, error_out=False)
    subjects = Subject.query.order_by(Subject.name).all()

    return render_template(
        'student/content_library.html',
        pagination=pagination,
        subjects=subjects,
        search=search,
        subject_filter=subject_filter,
        type_filter=type_filter,
        sort=sort,
        type_counts=_published_type_counts(),
    )


@student_bp.route('/content/<slug>')
@student_required
def content_detail(slug):
    item = _published_content_query().filter_by(slug=slug).first_or_404()
    related = _published_content_query().filter(
        Content.subject_id == item.subject_id,
        Content.id != item.id,
    ).order_by(Content.created_at.desc()).limit(4).all()

    return render_template(
        'student/content_detail.html', content=item, related=related
    )


@student_bp.route('/content/<slug>/download')
@student_required
def download_attachment(slug):
    item = _published_content_query().filter_by(slug=slug).first_or_404()
    if not item.attachment:
        abort(404)
    return redirect(url_for('files.serve_file', stored_name=item.attachment))


@student_bp.route('/announcements')
@student_required
def announcements():
    page = request.args.get('page', 1, type=int)
    pagination = Announcement.query.filter_by(is_published=True).order_by(
        Announcement.published_at.desc().nullslast()
    ).paginate(page=page, per_page=ANNOUNCEMENTS_PER_PAGE, error_out=False)
    return render_template(
        'student/announcements.html', pagination=pagination
    )


@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    user = db.session.get(User, session['user_id'])
    if user is None:
        abort(403)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            ok, message = update_profile(user, request.form)
            flash(message, 'success' if ok else 'error')
            if ok:
                db.session.commit()
                session['user_name'] = user.name
        elif action == 'change_password':
            ok, message = change_password(user, request.form)
            flash(message, 'success' if ok else 'error')
            if ok:
                db.session.commit()
        else:
            flash('Unknown profile action.', 'error')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', user=user)


@student_bp.route('/search')
@student_required
def search():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    pagination = None
    if q:
        pattern = f'%{q}%'
        pagination = _published_content_query().filter(
            db.or_(
                Content.title.ilike(pattern),
                Content.description.ilike(pattern),
                Content.tags.ilike(pattern),
                Content.topic.ilike(pattern),
                Content.body_html.ilike(pattern),
            )
        ).order_by(Content.created_at.desc()).paginate(
            page=page, per_page=CONTENT_PER_PAGE, error_out=False
        )

    return render_template('student/search.html', query=q, pagination=pagination)