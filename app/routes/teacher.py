from datetime import datetime, timezone

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, session, url_for)

from app.extensions import db
from app.models.announcement import Announcement
from app.models.content import CONTENT_TYPE_LABELS, Content
from app.models.subject import Subject
from app.models.uploaded_file import UploadedFile
from app.models.user import User
from app.services.accounts import change_password, update_profile
from app.services.decorators import teacher_required
from app.services.sanitizer import sanitize_html
from app.services.uploads import delete_stored_file, save_upload

teacher_bp = Blueprint('teacher', __name__)

CONTENT_PER_PAGE = 12
FILE_PER_PAGE = 20
STUDENT_PER_PAGE = 20


# ── Shared helpers ─────────────────────────────────────────
def _drop_item_file(kind, item):
    """Delete the stored file and metadata row currently attached to ``kind``."""
    stored = getattr(item, kind)
    if not stored:
        return
    record = UploadedFile.query.filter_by(stored_name=stored).first()
    if record is not None:
        db.session.delete(record)
    delete_stored_file(stored)
    setattr(item, kind, None)


def _handle_upload(kind, file_storage, item, user_id):
    """Persist an uploaded file, replacing whatever was attached before."""
    if not file_storage or not file_storage.filename:
        return None

    metadata, error = save_upload(file_storage)
    if error:
        flash(f'{kind.capitalize()}: {error}', 'error')
        return None

    _drop_item_file(kind, item)
    setattr(item, kind, metadata['stored_name'])
    db.session.add(
        UploadedFile(
            original_name=metadata['original_name'],
            stored_name=metadata['stored_name'],
            mime_type=metadata['mime_type'],
            size_bytes=metadata['size_bytes'],
            uploaded_by=user_id,
            content_id=item.id,
        )
    )
    return metadata


def _purge_item_files(item):
    for stored in (item.thumbnail, item.attachment):
        if stored:
            delete_stored_file(stored)


def _content_form_payload():
    return {
        'title': request.form.get('title', '').strip(),
        'description': request.form.get('description', '').strip(),
        'subject_id': request.form.get('subject_id', type=int),
        'topic': request.form.get('topic', '').strip(),
        'content_type': request.form.get('content_type', 'notes').strip(),
        'body_html': sanitize_html(request.form.get('body_html', '')),
        'video_url': request.form.get('video_url', '').strip(),
        'resource_url': request.form.get('resource_url', '').strip(),
        'tags': request.form.get('tags', '').strip(),
        'status': 'published' if request.form.get('status') == 'published' else 'draft',
    }


def _validate_content_payload(payload):
    """Return a list of human-readable validation errors."""
    errors = []
    if not payload['title']:
        errors.append('Title is required.')
    elif len(payload['title']) > 300:
        errors.append('Title must be 300 characters or fewer.')
    if not payload['subject_id']:
        errors.append('Please select a subject.')
    elif db.session.get(Subject, payload['subject_id']) is None:
        errors.append('The selected subject no longer exists.')
    if payload['content_type'] not in CONTENT_TYPE_LABELS:
        errors.append('Please choose a valid content type.')
    for field, label in (('video_url', 'Video URL'), ('resource_url', 'Resource URL')):
        value = payload[field]
        if value and not value.startswith(('http://', 'https://')):
            errors.append(f'{label} must start with http:// or https://')
    return errors


# ── Dashboard ──────────────────────────────────────────────
@teacher_bp.route('/dashboard')
@teacher_required
def dashboard():
    total_content = Content.query.count()
    published = Content.query.filter_by(status='published').count()
    drafts = Content.query.filter_by(status='draft').count()
    total_subjects = Subject.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_files = UploadedFile.query.count()

    recent_content = Content.query.order_by(Content.updated_at.desc()).limit(5).all()
    recent_drafts = Content.query.filter_by(status='draft').order_by(
        Content.updated_at.desc()
    ).limit(5).all()
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(3).all()

    return render_template(
        'teacher/dashboard.html',
        total_content=total_content,
        published=published,
        drafts=drafts,
        total_subjects=total_subjects,
        total_students=total_students,
        total_files=total_files,
        recent_content=recent_content,
        recent_drafts=recent_drafts,
        announcements=announcements,
    )


# ── Subjects ───────────────────────────────────────────────
@teacher_bp.route('/subjects')
@teacher_required
def subjects():
    all_subjects = Subject.query.order_by(Subject.name).all()
    return render_template('teacher/subjects.html', subjects=all_subjects)


@teacher_bp.route('/subjects/create', methods=['GET', 'POST'])
@teacher_required
def create_subject():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        icon = request.form.get('icon', 'bi-book').strip() or 'bi-book'

        if len(name) < 2:
            flash('Subject name must be at least 2 characters.', 'error')
            return render_template(
                'teacher/subject_form.html', form_data=request.form
            ), 400

        slug = Subject.unique_slug(name)
        if Subject.query.filter_by(slug=slug).first():
            flash('A subject with this name already exists.', 'error')
            return render_template(
                'teacher/subject_form.html', form_data=request.form
            ), 400

        subject = Subject(
            name=name,
            slug=slug,
            description=description,
            icon=icon,
            created_by=session['user_id'],
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject created successfully!', 'success')
        return redirect(url_for('teacher.subjects'))

    return render_template('teacher/subject_form.html', form_data=request.form)


@teacher_bp.route('/subjects/<int:id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_subject(id):
    subject = db.session.get(Subject, id)
    if subject is None:
        abort(404)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        icon = request.form.get('icon', 'bi-book').strip() or 'bi-book'

        if len(name) < 2:
            flash('Subject name must be at least 2 characters.', 'error')
            return render_template(
                'teacher/subject_form.html', subject=subject, form_data=request.form
            ), 400

        subject.name = name
        subject.slug = Subject.unique_slug(name, exclude_id=subject.id)
        subject.description = description
        subject.icon = icon
        db.session.commit()
        flash('Subject updated!', 'success')
        return redirect(url_for('teacher.subjects'))

    return render_template(
        'teacher/subject_form.html', subject=subject, form_data=request.form
    )


@teacher_bp.route('/subjects/<int:id>/delete', methods=['POST'])
@teacher_required
def delete_subject(id):
    subject = db.session.get(Subject, id)
    if subject is None:
        abort(404)
    if subject.total_count:
        flash(
            f'Cannot delete "{subject.name}" while it still has content. '
            'Remove or move the content first.',
            'error',
        )
        return redirect(url_for('teacher.subjects'))
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted.', 'success')
    return redirect(url_for('teacher.subjects'))


# ── Content ────────────────────────────────────────────────
@teacher_bp.route('/content')
@teacher_required
def content_list():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '').strip()
    subject_filter = request.args.get('subject', '', type=int)
    search = request.args.get('q', '').strip()
    type_filter = request.args.get('type', '').strip()
    sort = request.args.get('sort', 'newest')

    query = Content.query

    if status_filter in ('draft', 'published'):
        query = query.filter_by(status=status_filter)
    if subject_filter:
        query = query.filter_by(subject_id=subject_filter)
    if type_filter in CONTENT_TYPE_LABELS:
        query = query.filter_by(content_type=type_filter)
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

    query = query.order_by(
        Content.created_at.asc() if sort == 'oldest' else Content.created_at.desc()
    )

    pagination = query.paginate(page=page, per_page=CONTENT_PER_PAGE, error_out=False)
    subjects = Subject.query.order_by(Subject.name).all()

    return render_template(
        'teacher/content_list.html',
        pagination=pagination,
        subjects=subjects,
        status_filter=status_filter,
        subject_filter=subject_filter,
        type_filter=type_filter,
        search=search,
        sort=sort,
    )


@teacher_bp.route('/content/create', methods=['GET', 'POST'])
@teacher_required
def create_content():
    subjects = Subject.query.order_by(Subject.name).all()

    if request.method == 'POST':
        payload = _content_form_payload()
        errors = _validate_content_payload(payload)
        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template(
                'teacher/content_form.html',
                subjects=subjects,
                content=None,
                form_data=request.form,
            ), 400

        item = Content(
            title=payload['title'],
            slug=Content.unique_slug(payload['title']),
            description=payload['description'],
            subject_id=payload['subject_id'],
            topic=payload['topic'],
            content_type=payload['content_type'],
            body_html=payload['body_html'],
            video_url=payload['video_url'] or None,
            resource_url=payload['resource_url'] or None,
            tags=payload['tags'],
            status=payload['status'],
            created_by=session['user_id'],
        )
        if payload['status'] == 'published':
            item.publish()

        db.session.add(item)
        db.session.flush()

        _handle_upload('thumbnail', request.files.get('thumbnail'), item, session['user_id'])
        _handle_upload('attachment', request.files.get('attachment'), item, session['user_id'])

        db.session.commit()
        flash('Content created successfully!', 'success')
        return redirect(url_for('teacher.content_list'))

    return render_template(
        'teacher/content_form.html', subjects=subjects, content=None, form_data=request.form
    )


@teacher_bp.route('/content/<int:id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_content(id):
    item = db.session.get(Content, id)
    if item is None:
        abort(404)
    subjects = Subject.query.order_by(Subject.name).all()

    if request.method == 'POST':
        payload = _content_form_payload()
        errors = _validate_content_payload(payload)
        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template(
                'teacher/content_form.html',
                content=item,
                subjects=subjects,
                form_data=request.form,
            ), 400

        was_published = item.is_published
        item.title = payload['title']
        item.slug = Content.unique_slug(payload['title'], exclude_id=item.id)
        item.description = payload['description']
        item.subject_id = payload['subject_id']
        item.topic = payload['topic']
        item.content_type = payload['content_type']
        item.body_html = payload['body_html']
        item.video_url = payload['video_url'] or None
        item.resource_url = payload['resource_url'] or None
        item.tags = payload['tags']

        if payload['status'] == 'published':
            item.publish()
        else:
            item.unpublish()

        db.session.flush()

        _handle_upload('thumbnail', request.files.get('thumbnail'), item, session['user_id'])
        _handle_upload('attachment', request.files.get('attachment'), item, session['user_id'])

        db.session.commit()
        message = 'Content updated!'
        if was_published and not item.is_published:
            message = 'Content updated and unpublished.'
        elif not was_published and item.is_published:
            message = 'Content updated and published.'
        flash(message, 'success')
        return redirect(url_for('teacher.content_list'))

    return render_template(
        'teacher/content_form.html',
        content=item,
        subjects=subjects,
        form_data=request.form,
    )


@teacher_bp.route('/content/<int:id>/preview')
@teacher_required
def preview_content(id):
    item = db.session.get(Content, id)
    if item is None:
        abort(404)
    return render_template('teacher/content_preview.html', content=item)


@teacher_bp.route('/content/<int:id>/toggle', methods=['POST'])
@teacher_required
def toggle_content(id):
    item = db.session.get(Content, id)
    if item is None:
        abort(404)
    now_published = item.toggle_published()
    db.session.commit()
    flash(
        f'Content {"published" if now_published else "moved back to drafts"}.',
        'success',
    )
    return redirect(url_for('teacher.content_list'))


@teacher_bp.route('/content/<int:id>/delete', methods=['POST'])
@teacher_required
def delete_content(id):
    item = db.session.get(Content, id)
    if item is None:
        abort(404)
    _purge_item_files(item)
    for uploaded in list(item.files):
        delete_stored_file(uploaded.stored_name)
        db.session.delete(uploaded)
    db.session.delete(item)
    db.session.commit()
    flash('Content and its attachments were deleted.', 'success')
    return redirect(url_for('teacher.content_list'))


# ── Announcements ─────────────────────────────────────────
@teacher_bp.route('/announcements')
@teacher_required
def announcements():
    page = request.args.get('page', 1, type=int)
    pagination = Announcement.query.order_by(Announcement.created_at.desc()).paginate(
        page=page, per_page=FILE_PER_PAGE, error_out=False
    )
    return render_template('teacher/announcements.html', pagination=pagination)


@teacher_bp.route('/announcements/create', methods=['GET', 'POST'])
@teacher_required
def create_announcement():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        body = sanitize_html(request.form.get('body', '').strip())
        publish = request.form.get('is_published') == 'on'

        if not title or not body:
            flash('Title and message are both required.', 'error')
            return render_template(
                'teacher/announcement_form.html', announcement=None, form_data=request.form
            ), 400

        announcement = Announcement(
            title=title,
            body=body,
            is_published=publish,
            created_by=session['user_id'],
        )
        if publish:
            announcement.publish()
        db.session.add(announcement)
        db.session.commit()
        flash('Announcement created!', 'success')
        return redirect(url_for('teacher.announcements'))

    return render_template(
        'teacher/announcement_form.html', announcement=None, form_data=request.form
    )


@teacher_bp.route('/announcements/<int:id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_announcement(id):
    announcement = db.session.get(Announcement, id)
    if announcement is None:
        abort(404)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        body = sanitize_html(request.form.get('body', '').strip())
        publish = request.form.get('is_published') == 'on'

        if not title or not body:
            flash('Title and message are both required.', 'error')
            return render_template(
                'teacher/announcement_form.html',
                announcement=announcement,
                form_data=request.form,
            ), 400

        announcement.title = title
        announcement.body = body
        if publish:
            announcement.publish()
        else:
            announcement.unpublish()
        db.session.commit()
        flash('Announcement updated!', 'success')
        return redirect(url_for('teacher.announcements'))

    return render_template(
        'teacher/announcement_form.html', announcement=announcement, form_data=request.form
    )


@teacher_bp.route('/announcements/<int:id>/delete', methods=['POST'])
@teacher_required
def delete_announcement(id):
    announcement = db.session.get(Announcement, id)
    if announcement is None:
        abort(404)
    db.session.delete(announcement)
    db.session.commit()
    flash('Announcement deleted.', 'success')
    return redirect(url_for('teacher.announcements'))


# ── Students overview ──────────────────────────────────────
@teacher_bp.route('/students')
@teacher_required
def students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    query = User.query.filter_by(role='student')
    if search:
        pattern = f'%{search}%'
        query = query.filter(
            db.or_(User.name.ilike(pattern), User.email.ilike(pattern))
        )
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=STUDENT_PER_PAGE, error_out=False
    )
    return render_template(
        'teacher/students.html', pagination=pagination, search=search
    )


# ── Files ──────────────────────────────────────────────────
@teacher_bp.route('/files')
@teacher_required
def files():
    page = request.args.get('page', 1, type=int)
    pagination = UploadedFile.query.order_by(UploadedFile.created_at.desc()).paginate(
        page=page, per_page=FILE_PER_PAGE, error_out=False
    )
    return render_template('teacher/files.html', pagination=pagination)


@teacher_bp.route('/files/<int:id>/delete', methods=['POST'])
@teacher_required
def delete_file(id):
    uploaded = db.session.get(UploadedFile, id)
    if uploaded is None:
        abort(404)
    delete_stored_file(uploaded.stored_name)
    content = uploaded.content
    if content is not None:
        if content.thumbnail == uploaded.stored_name:
            content.thumbnail = None
        if content.attachment == uploaded.stored_name:
            content.attachment = None
    db.session.delete(uploaded)
    db.session.commit()
    flash('File deleted.', 'success')
    return redirect(url_for('teacher.files'))


# ── Profile ────────────────────────────────────────────────
@teacher_bp.route('/profile', methods=['GET', 'POST'])
@teacher_required
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
        return redirect(url_for('teacher.profile'))

    return render_template('teacher/profile.html', user=user)