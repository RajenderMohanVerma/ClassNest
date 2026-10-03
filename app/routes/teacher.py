import os
from datetime import datetime, timezone

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session, current_app, send_from_directory, abort)

from app.extensions import db
from app.models.user import User
from app.models.subject import Subject
from app.models.content import Content
from app.models.announcement import Announcement
from app.models.uploaded_file import UploadedFile
from app.services.decorators import teacher_required
from app.services.uploads import save_upload
from app.services.sanitizer import sanitize_html

teacher_bp = Blueprint('teacher', __name__)


# ── Dashboard ──────────────────────────────────────────────
@teacher_bp.route('/dashboard')
@teacher_required
def dashboard():
    total_content = Content.query.count()
    published = Content.query.filter_by(status='published').count()
    drafts = Content.query.filter_by(status='draft').count()
    total_subjects = Subject.query.count()
    total_students = User.query.filter_by(role='student').count()

    recent_content = Content.query.order_by(Content.updated_at.desc()).limit(5).all()
    recent_drafts = Content.query.filter_by(status='draft').order_by(Content.updated_at.desc()).limit(5).all()
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(3).all()

    return render_template('teacher/dashboard.html',
                           total_content=total_content, published=published,
                           drafts=drafts, total_subjects=total_subjects,
                           total_students=total_students,
                           recent_content=recent_content, recent_drafts=recent_drafts,
                           announcements=announcements)


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
        icon = request.form.get('icon', 'bi-book').strip()

        if not name:
            flash('Subject name is required.', 'error')
            return render_template('teacher/subject_form.html')

        slug = Subject.generate_slug(name)
        if Subject.query.filter_by(slug=slug).first():
            flash('A subject with this name already exists.', 'error')
            return render_template('teacher/subject_form.html', name=name, description=description)

        subj = Subject(name=name, slug=slug, description=description, icon=icon,
                       created_by=session['user_id'])
        db.session.add(subj)
        db.session.commit()
        flash('Subject created successfully!', 'success')
        return redirect(url_for('teacher.subjects'))

    return render_template('teacher/subject_form.html')


@teacher_bp.route('/subjects/<int:id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_subject(id):
    subj = db.session.get(Subject, id)
    if not subj:
        abort(404)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        icon = request.form.get('icon', 'bi-book').strip()

        if not name:
            flash('Subject name is required.', 'error')
            return render_template('teacher/subject_form.html', subject=subj)

        new_slug = Subject.generate_slug(name)
        existing = Subject.query.filter(Subject.slug == new_slug, Subject.id != id).first()
        if existing:
            flash('A subject with this name already exists.', 'error')
            return render_template('teacher/subject_form.html', subject=subj)

        subj.name = name
        subj.slug = new_slug
        subj.description = description
        subj.icon = icon
        db.session.commit()
        flash('Subject updated!', 'success')
        return redirect(url_for('teacher.subjects'))

    return render_template('teacher/subject_form.html', subject=subj)


@teacher_bp.route('/subjects/<int:id>/delete', methods=['POST'])
@teacher_required
def delete_subject(id):
    subj = db.session.get(Subject, id)
    if not subj:
        abort(404)
    if subj.content.count() > 0:
        flash('Cannot delete subject with existing content. Remove content first.', 'error')
        return redirect(url_for('teacher.subjects'))
    db.session.delete(subj)
    db.session.commit()
    flash('Subject deleted.', 'success')
    return redirect(url_for('teacher.subjects'))


# ── Content ────────────────────────────────────────────────
@teacher_bp.route('/content')
@teacher_required
def content_list():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    subject_filter = request.args.get('subject', '', type=str)
    search = request.args.get('q', '').strip()
    sort = request.args.get('sort', 'newest')

    query = Content.query

    if status_filter in ('draft', 'published'):
        query = query.filter_by(status=status_filter)
    if subject_filter:
        query = query.filter_by(subject_id=int(subject_filter))
    if search:
        query = query.filter(
            db.or_(
                Content.title.ilike(f'%{search}%'),
                Content.description.ilike(f'%{search}%'),
                Content.tags.ilike(f'%{search}%'),
            )
        )

    if sort == 'oldest':
        query = query.order_by(Content.created_at.asc())
    else:
        query = query.order_by(Content.created_at.desc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    subjects = Subject.query.order_by(Subject.name).all()

    return render_template('teacher/content_list.html',
                           pagination=pagination, subjects=subjects,
                           status_filter=status_filter, subject_filter=subject_filter,
                           search=search, sort=sort)


@teacher_bp.route('/content/create', methods=['GET', 'POST'])
@teacher_required
def create_content():
    subjects = Subject.query.order_by(Subject.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        subject_id = request.form.get('subject_id', type=int)
        topic = request.form.get('topic', '').strip()
        content_type = request.form.get('content_type', 'notes')
        body_html = sanitize_html(request.form.get('body_html', ''))
        video_url = request.form.get('video_url', '').strip()
        resource_url = request.form.get('resource_url', '').strip()
        tags = request.form.get('tags', '').strip()
        status = request.form.get('status', 'draft')

        if not title:
            flash('Title is required.', 'error')
            return render_template('teacher/content_form.html', subjects=subjects)
        if not subject_id:
            flash('Please select a subject.', 'error')
            return render_template('teacher/content_form.html', subjects=subjects)

        slug = Content.generate_slug(title)
        existing = Content.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{Content.query.count() + 1}"

        item = Content(
            title=title, slug=slug, description=description,
            subject_id=subject_id, topic=topic, content_type=content_type,
            body_html=body_html, video_url=video_url, resource_url=resource_url,
            tags=tags, status=status, created_by=session['user_id']
        )

        # Handle thumbnail
        thumb = request.files.get('thumbnail')
        if thumb and thumb.filename:
            result, err = save_upload(thumb)
            if err:
                flash(f'Thumbnail: {err}', 'error')
            else:
                item.thumbnail = result['stored_name']

        # Handle attachment
        attach = request.files.get('attachment')
        if attach and attach.filename:
            result, err = save_upload(attach)
            if err:
                flash(f'Attachment: {err}', 'error')
            else:
                item.attachment = result['stored_name']
                db.session.add(item)
                db.session.flush()
                uf = UploadedFile(
                    original_name=result['original_name'],
                    stored_name=result['stored_name'],
                    mime_type=result['mime_type'],
                    size_bytes=result['size_bytes'],
                    uploaded_by=session['user_id'],
                    content_id=item.id,
                )
                db.session.add(uf)

        if not item.id:
            db.session.add(item)
        db.session.commit()
        flash('Content created successfully!', 'success')
        return redirect(url_for('teacher.content_list'))

    return render_template('teacher/content_form.html', subjects=subjects)


@teacher_bp.route('/content/<int:id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_content(id):
    item = db.session.get(Content, id)
    if not item:
        abort(404)
    subjects = Subject.query.order_by(Subject.name).all()

    if request.method == 'POST':
        item.title = request.form.get('title', '').strip()
        item.description = request.form.get('description', '').strip()
        item.subject_id = request.form.get('subject_id', type=int)
        item.topic = request.form.get('topic', '').strip()
        item.content_type = request.form.get('content_type', 'notes')
        item.body_html = sanitize_html(request.form.get('body_html', ''))
        item.video_url = request.form.get('video_url', '').strip()
        item.resource_url = request.form.get('resource_url', '').strip()
        item.tags = request.form.get('tags', '').strip()
        item.status = request.form.get('status', 'draft')

        if not item.title:
            flash('Title is required.', 'error')
            return render_template('teacher/content_form.html', content=item, subjects=subjects)

        thumb = request.files.get('thumbnail')
        if thumb and thumb.filename:
            result, err = save_upload(thumb)
            if err:
                flash(f'Thumbnail: {err}', 'error')
            else:
                item.thumbnail = result['stored_name']

        attach = request.files.get('attachment')
        if attach and attach.filename:
            result, err = save_upload(attach)
            if err:
                flash(f'Attachment: {err}', 'error')
            else:
                item.attachment = result['stored_name']
                uf = UploadedFile(
                    original_name=result['original_name'],
                    stored_name=result['stored_name'],
                    mime_type=result['mime_type'],
                    size_bytes=result['size_bytes'],
                    uploaded_by=session['user_id'],
                    content_id=item.id,
                )
                db.session.add(uf)

        db.session.commit()
        flash('Content updated!', 'success')
        return redirect(url_for('teacher.content_list'))

    return render_template('teacher/content_form.html', content=item, subjects=subjects)


@teacher_bp.route('/content/<int:id>/preview')
@teacher_required
def preview_content(id):
    item = db.session.get(Content, id)
    if not item:
        abort(404)
    return render_template('teacher/content_preview.html', content=item)


@teacher_bp.route('/content/<int:id>/toggle', methods=['POST'])
@teacher_required
def toggle_content(id):
    item = db.session.get(Content, id)
    if not item:
        abort(404)
    item.status = 'draft' if item.status == 'published' else 'published'
    db.session.commit()
    flash(f'Content {"published" if item.status == "published" else "unpublished"}.', 'success')
    return redirect(url_for('teacher.content_list'))


@teacher_bp.route('/content/<int:id>/delete', methods=['POST'])
@teacher_required
def delete_content(id):
    item = db.session.get(Content, id)
    if not item:
        abort(404)
    db.session.delete(item)
    db.session.commit()
    flash('Content deleted.', 'success')
    return redirect(url_for('teacher.content_list'))


# ── Announcements ─────────────────────────────────────────
@teacher_bp.route('/announcements')
@teacher_required
def announcements():
    items = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('teacher/announcements.html', announcements=items)


@teacher_bp.route('/announcements/create', methods=['GET', 'POST'])
@teacher_required
def create_announcement():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()
        is_published = request.form.get('is_published') == 'on'

        if not title or not body:
            flash('Title and body are required.', 'error')
            return render_template('teacher/announcement_form.html')

        ann = Announcement(
            title=title, body=sanitize_html(body),
            is_published=is_published, created_by=session['user_id'],
            published_at=datetime.now(timezone.utc) if is_published else None
        )
        db.session.add(ann)
        db.session.commit()
        flash('Announcement created!', 'success')
        return redirect(url_for('teacher.announcements'))

    return render_template('teacher/announcement_form.html')


@teacher_bp.route('/announcements/<int:id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_announcement(id):
    ann = db.session.get(Announcement, id)
    if not ann:
        abort(404)

    if request.method == 'POST':
        ann.title = request.form.get('title', '').strip()
        ann.body = sanitize_html(request.form.get('body', '').strip())
        was_published = ann.is_published
        ann.is_published = request.form.get('is_published') == 'on'
        if ann.is_published and not was_published:
            ann.published_at = datetime.now(timezone.utc)

        db.session.commit()
        flash('Announcement updated!', 'success')
        return redirect(url_for('teacher.announcements'))

    return render_template('teacher/announcement_form.html', announcement=ann)


@teacher_bp.route('/announcements/<int:id>/delete', methods=['POST'])
@teacher_required
def delete_announcement(id):
    ann = db.session.get(Announcement, id)
    if not ann:
        abort(404)
    db.session.delete(ann)
    db.session.commit()
    flash('Announcement deleted.', 'success')
    return redirect(url_for('teacher.announcements'))


# ── Students overview ──────────────────────────────────────
@teacher_bp.route('/students')
@teacher_required
def students():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.filter_by(role='student').order_by(
        User.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    return render_template('teacher/students.html', pagination=pagination)


# ── Profile ────────────────────────────────────────────────
@teacher_bp.route('/profile', methods=['GET', 'POST'])
@teacher_required
def profile():
    user = db.session.get(User, session['user_id'])

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            user.name = request.form.get('name', '').strip() or user.name
            new_email = request.form.get('email', '').strip().lower()
            if new_email and new_email != user.email:
                if User.query.filter_by(email=new_email).first():
                    flash('Email already in use.', 'error')
                    return render_template('teacher/profile.html', user=user)
                user.email = new_email
            db.session.commit()
            session['user_name'] = user.name
            flash('Profile updated!', 'success')

        elif action == 'change_password':
            current = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            confirm = request.form.get('confirm_password', '')

            if not user.check_password(current):
                flash('Current password is incorrect.', 'error')
            elif len(new_pw) < 6:
                flash('New password must be at least 6 characters.', 'error')
            elif new_pw != confirm:
                flash('New passwords do not match.', 'error')
            else:
                user.set_password(new_pw)
                db.session.commit()
                flash('Password changed successfully!', 'success')

        return redirect(url_for('teacher.profile'))

    return render_template('teacher/profile.html', user=user)


# ── Files ──────────────────────────────────────────────────
@teacher_bp.route('/files')
@teacher_required
def files():
    page = request.args.get('page', 1, type=int)
    pagination = UploadedFile.query.order_by(
        UploadedFile.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    return render_template('teacher/files.html', pagination=pagination)


@teacher_bp.route('/files/<int:id>/delete', methods=['POST'])
@teacher_required
def delete_file(id):
    f = db.session.get(UploadedFile, id)
    if not f:
        abort(404)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], f.stored_name)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(f)
    db.session.commit()
    flash('File deleted.', 'success')
    return redirect(url_for('teacher.files'))
