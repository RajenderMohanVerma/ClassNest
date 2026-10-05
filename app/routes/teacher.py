from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, session, url_for)

from app.extensions import db
from app.models.announcement import Announcement
from app.models.catalog import Chapter, SchoolClass
from app.models.content import CONTENT_TYPE_LABELS, Content
from app.models.enums import CONTENT_STATUS_DRAFT, CONTENT_STATUS_PUBLISHED
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
        'class_id': request.form.get('class_id', type=int),
        'subject_id': request.form.get('subject_id', type=int),
        'chapter_id': request.form.get('chapter_id', type=int),
        'topic': request.form.get('topic', '').strip(),
        'content_type': request.form.get('content_type', 'notes').strip(),
        'body_html': sanitize_html(request.form.get('body_html', '')),
        'video_url': request.form.get('video_url', '').strip(),
        'resource_url': request.form.get('resource_url', '').strip(),
        'tags': request.form.get('tags', '').strip(),
        'status': 'published' if request.form.get('status') == 'published' else 'draft',
    }


def _validate_content_payload(payload, existing=None):
    """Return a list of human-readable validation errors."""
    errors = []
    if not payload['title']:
        errors.append('Title is required.')
    elif len(payload['title']) > 300:
        errors.append('Title must be 300 characters or fewer.')
    subject = None
    if not payload['subject_id']:
        errors.append('Please select a subject.')
    else:
        subject = db.session.get(Subject, payload['subject_id'])
    if payload['subject_id'] and subject is None:
        errors.append('The selected subject no longer exists.')

    school_class = None
    if not payload['class_id']:
        errors.append('Please select a class.')
    else:
        school_class = db.session.get(SchoolClass, payload['class_id'])
        if school_class is None:
            errors.append('The selected class no longer exists.')
        elif not school_class.is_available and (
            existing is None or existing.class_id != school_class.id
        ):
            errors.append('Please select an active class.')

    if subject is not None and school_class is not None:
        if subject.class_id != school_class.id:
            errors.append('The selected subject does not belong to this class.')

    chapter = None
    if not payload['chapter_id']:
        errors.append('Please select a chapter for this content.')
    else:
        chapter = db.session.get(Chapter, payload['chapter_id'])
        if chapter is None:
            errors.append('The selected chapter no longer exists.')
        elif subject is not None and chapter.subject_id != subject.id:
            errors.append('The selected chapter does not belong to this subject.')
        elif school_class is not None and chapter.class_id != school_class.id:
            errors.append('The selected chapter does not belong to this class.')
        elif payload['status'] == 'published' and not chapter.is_published:
            errors.append('Publish the chapter before publishing its content.')
    if payload['content_type'] not in CONTENT_TYPE_LABELS:
        errors.append('Please choose a valid content type.')
    for field, label in (('video_url', 'Video URL'), ('resource_url', 'Resource URL')):
        value = payload[field]
        if value and not value.startswith(('http://', 'https://')):
            errors.append(f'{label} must start with http:// or https://')
    return errors


def _catalog_form_options():
    return {
        'classes': SchoolClass.query.order_by(
            SchoolClass.display_order, SchoolClass.name,
        ).all(),
        'subjects': Subject.query.filter(Subject.class_id.isnot(None)).order_by(
            Subject.name,
        ).all(),
        'chapters': Chapter.query.order_by(
            Chapter.display_order, Chapter.title,
        ).all(),
    }


def _display_order_value():
    raw_value = request.form.get('display_order', '').strip()
    if not raw_value:
        return 0
    try:
        return int(raw_value)
    except ValueError:
        return None


# ── Dashboard ──────────────────────────────────────────────
@teacher_bp.route('/dashboard')
@teacher_required
def dashboard():
    total_content = Content.query.count()
    published = Content.query.filter_by(status='published').count()
    drafts = Content.query.filter_by(status='draft').count()
    total_classes = SchoolClass.query.count()
    total_subjects = Subject.query.count()
    total_chapters = Chapter.query.count()
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
        total_classes=total_classes,
        total_subjects=total_subjects,
        total_chapters=total_chapters,
        total_students=total_students,
        total_files=total_files,
        recent_content=recent_content,
        recent_drafts=recent_drafts,
        announcements=announcements,
    )


# ── Academic classes ───────────────────────────────────────
@teacher_bp.route('/classes')
@teacher_required
def classes():
    all_classes = SchoolClass.query.order_by(
        SchoolClass.display_order, SchoolClass.name,
    ).all()
    return render_template('teacher/classes.html', classes=all_classes)


@teacher_bp.route('/classes/create', methods=['GET', 'POST'])
@teacher_required
def create_class():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        display_order = _display_order_value()
        errors = []
        if len(name) < 2:
            errors.append('Class name must be at least 2 characters.')
        if len(name) > 120:
            errors.append('Class name must be 120 characters or fewer.')
        if display_order is None or display_order < 0:
            errors.append('Display order must be zero or greater.')

        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template(
                'teacher/class_form.html', form_data=request.form,
            ), 400

        school_class = SchoolClass(
            name=name,
            slug=SchoolClass.unique_slug(name),
            description=description,
            display_order=display_order,
            created_by=session['user_id'],
        )
        db.session.add(school_class)
        db.session.commit()
        flash(f'{school_class.name} created. Add its subjects to organize learning material.', 'success')
        return redirect(url_for('teacher.classes'))

    return render_template('teacher/class_form.html', form_data=request.form)


@teacher_bp.route('/classes/<int:id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_class(id):
    school_class = db.session.get(SchoolClass, id)
    if school_class is None:
        abort(404)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        display_order = _display_order_value()
        errors = []
        if len(name) < 2:
            errors.append('Class name must be at least 2 characters.')
        if len(name) > 120:
            errors.append('Class name must be 120 characters or fewer.')
        if display_order is None or display_order < 0:
            errors.append('Display order must be zero or greater.')

        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template(
                'teacher/class_form.html', school_class=school_class,
                form_data=request.form,
            ), 400

        school_class.name = name
        school_class.slug = SchoolClass.unique_slug(name, exclude_id=school_class.id)
        school_class.description = description
        school_class.display_order = display_order
        db.session.commit()
        flash('Class details updated.', 'success')
        return redirect(url_for('teacher.classes'))

    return render_template(
        'teacher/class_form.html', school_class=school_class,
        form_data=request.form,
    )


# ── Subjects ───────────────────────────────────────────────
@teacher_bp.route('/subjects')
@teacher_required
def subjects():
    class_filter = request.args.get('class_id', type=int)
    query = Subject.query.order_by(Subject.class_id, Subject.name)
    if class_filter:
        query = query.filter_by(class_id=class_filter)
    all_subjects = query.all()
    all_classes = SchoolClass.query.order_by(
        SchoolClass.display_order, SchoolClass.name,
    ).all()
    return render_template(
        'teacher/subjects.html', subjects=all_subjects, classes=all_classes,
        class_filter=class_filter,
    )


@teacher_bp.route('/subjects/create', methods=['GET', 'POST'])
@teacher_required
def create_subject():
    classes = SchoolClass.query.filter_by(is_enabled=True).order_by(
        SchoolClass.display_order, SchoolClass.name,
    ).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        icon = request.form.get('icon', 'bi-book').strip() or 'bi-book'
        class_id = request.form.get('class_id', type=int)
        school_class = db.session.get(SchoolClass, class_id) if class_id else None

        errors = []
        if len(name) < 2:
            errors.append('Subject name must be at least 2 characters.')
        if school_class is None or not school_class.is_available:
            errors.append('Choose an active class for this subject.')
        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template(
                'teacher/subject_form.html', form_data=request.form, classes=classes,
            ), 400

        slug = Subject.unique_slug(name)
        subject = Subject(
            name=name,
            slug=slug,
            description=description,
            icon=icon,
            class_id=school_class.id,
            created_by=session['user_id'],
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject created successfully!', 'success')
        return redirect(url_for('teacher.subjects'))

    return render_template(
        'teacher/subject_form.html', form_data=request.args, classes=classes,
    )


@teacher_bp.route('/subjects/<int:id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_subject(id):
    subject = db.session.get(Subject, id)
    if subject is None:
        abort(404)

    classes = SchoolClass.query.order_by(
        SchoolClass.display_order, SchoolClass.name,
    ).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        icon = request.form.get('icon', 'bi-book').strip() or 'bi-book'
        class_id = request.form.get('class_id', type=int)
        school_class = db.session.get(SchoolClass, class_id) if class_id else None

        if len(name) < 2:
            flash('Subject name must be at least 2 characters.', 'error')
            return render_template(
                'teacher/subject_form.html', subject=subject, form_data=request.form,
                classes=classes,
            ), 400
        if school_class is None or (
            not school_class.is_available and school_class.id != subject.class_id
        ):
            flash('Choose an active class for this subject.', 'error')
            return render_template(
                'teacher/subject_form.html', subject=subject, form_data=request.form,
                classes=classes,
            ), 400

        previous_class_id = subject.class_id
        subject.name = name
        subject.slug = Subject.unique_slug(name, exclude_id=subject.id)
        subject.description = description
        subject.icon = icon
        subject.class_id = school_class.id
        if previous_class_id != school_class.id:
            for chapter in subject.chapters.all():
                chapter.class_id = school_class.id
                for content in chapter.content.all():
                    content.class_id = school_class.id
            for content in subject.content.all():
                content.class_id = school_class.id
        db.session.commit()
        flash('Subject updated!', 'success')
        return redirect(url_for('teacher.subjects'))

    return render_template(
        'teacher/subject_form.html', subject=subject, form_data=request.form,
        classes=classes,
    )


@teacher_bp.route('/subjects/<int:id>/delete', methods=['POST'])
@teacher_required
def delete_subject(id):
    subject = db.session.get(Subject, id)
    if subject is None:
        abort(404)
    if subject.total_count or subject.chapter_count:
        flash(
            f'Cannot delete "{subject.name}" while it has chapters or content. '
            'Remove or move those records first.',
            'error',
        )
        return redirect(url_for('teacher.subjects'))
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted.', 'success')
    return redirect(url_for('teacher.subjects'))


# ── Chapters ───────────────────────────────────────────────
def _chapter_form_options():
    return {
        'classes': SchoolClass.query.order_by(
            SchoolClass.display_order, SchoolClass.name,
        ).all(),
        'subjects': Subject.query.filter(Subject.class_id.isnot(None)).order_by(
            Subject.name,
        ).all(),
    }


def _validate_chapter_payload(payload, existing=None):
    errors = []
    if len(payload['title']) < 2:
        errors.append('Chapter title must be at least 2 characters.')
    elif len(payload['title']) > 200:
        errors.append('Chapter title must be 200 characters or fewer.')
    if payload['display_order'] is None or payload['display_order'] < 0:
        errors.append('Display order must be zero or greater.')

    school_class = db.session.get(SchoolClass, payload['class_id']) if payload['class_id'] else None
    if school_class is None:
        errors.append('Choose a class for this chapter.')
    elif not school_class.is_available and (
        existing is None or existing.class_id != school_class.id
    ):
        errors.append('Choose an active class for this chapter.')

    subject = db.session.get(Subject, payload['subject_id']) if payload['subject_id'] else None
    if subject is None:
        errors.append('Choose a subject for this chapter.')
    elif school_class is not None and subject.class_id != school_class.id:
        errors.append('The selected subject does not belong to this class.')
    return errors, subject


def _chapter_payload():
    return {
        'title': request.form.get('title', '').strip(),
        'class_id': request.form.get('class_id', type=int),
        'subject_id': request.form.get('subject_id', type=int),
        'description': request.form.get('description', '').strip(),
        'display_order': _display_order_value(),
        'status': CONTENT_STATUS_PUBLISHED if request.form.get('status') == 'published'
                  else CONTENT_STATUS_DRAFT,
    }


@teacher_bp.route('/chapters')
@teacher_required
def chapters():
    class_filter = request.args.get('class_id', type=int)
    query = Chapter.query.join(Subject).order_by(
        Chapter.class_id, Chapter.subject_id, Chapter.display_order, Chapter.title,
    )
    if class_filter:
        query = query.filter(Chapter.class_id == class_filter)
    return render_template(
        'teacher/chapters.html', chapters=query.all(),
        classes=SchoolClass.query.order_by(SchoolClass.display_order, SchoolClass.name).all(),
        class_filter=class_filter,
    )


@teacher_bp.route('/chapters/create', methods=['GET', 'POST'])
@teacher_required
def create_chapter():
    options = _chapter_form_options()
    if request.method == 'POST':
        payload = _chapter_payload()
        errors, subject = _validate_chapter_payload(payload)
        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template(
                'teacher/chapter_form.html', form_data=request.form, **options,
            ), 400

        chapter = Chapter(
            title=payload['title'],
            slug=Chapter.unique_slug(payload['title']),
            class_id=subject.class_id,
            subject_id=subject.id,
            description=payload['description'],
            display_order=payload['display_order'],
            status=payload['status'],
            created_by=session['user_id'],
        )
        db.session.add(chapter)
        db.session.commit()
        flash(f'Chapter "{chapter.title}" added to {subject.name}.', 'success')
        return redirect(url_for('teacher.chapters', class_id=subject.class_id))

    return render_template(
        'teacher/chapter_form.html', form_data=request.args, **options,
    )


@teacher_bp.route('/chapters/<int:id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_chapter(id):
    chapter = db.session.get(Chapter, id)
    if chapter is None:
        abort(404)
    options = _chapter_form_options()

    if request.method == 'POST':
        payload = _chapter_payload()
        errors, subject = _validate_chapter_payload(payload, existing=chapter)
        if subject is not None and chapter.content.count() and (
            subject.id != chapter.subject_id or subject.class_id != chapter.class_id
        ):
            errors.append('Move this chapter’s content before changing its class or subject.')
        if (
            payload['status'] != CONTENT_STATUS_PUBLISHED
            and chapter.content.filter_by(status='published').count()
        ):
            errors.append('Unpublish or move this chapter’s published content before hiding the chapter.')
        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template(
                'teacher/chapter_form.html', chapter=chapter,
                form_data=request.form, **options,
            ), 400

        chapter.title = payload['title']
        chapter.slug = Chapter.unique_slug(payload['title'], exclude_id=chapter.id)
        chapter.class_id = subject.class_id
        chapter.subject_id = subject.id
        chapter.description = payload['description']
        chapter.display_order = payload['display_order']
        chapter.status = payload['status']
        db.session.commit()
        flash('Chapter updated.', 'success')
        return redirect(url_for('teacher.chapters', class_id=subject.class_id))

    return render_template(
        'teacher/chapter_form.html', chapter=chapter,
        form_data=request.form, **options,
    )


@teacher_bp.route('/chapters/<int:id>/delete', methods=['POST'])
@teacher_required
def delete_chapter(id):
    chapter = db.session.get(Chapter, id)
    if chapter is None:
        abort(404)
    if chapter.content.count() or chapter.assignments.count():
        flash('This chapter still has content or assignments. Remove those first.', 'error')
        return redirect(url_for('teacher.chapters', class_id=chapter.class_id))
    class_id = chapter.class_id
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted.', 'success')
    return redirect(url_for('teacher.chapters', class_id=class_id))


# ── Content ────────────────────────────────────────────────
@teacher_bp.route('/content')
@teacher_required
def content_list():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '').strip()
    subject_filter = request.args.get('subject', '', type=int)
    class_filter = request.args.get('class_id', '', type=int)
    search = request.args.get('q', '').strip()
    type_filter = request.args.get('type', '').strip()
    sort = request.args.get('sort', 'newest')

    query = Content.query

    if class_filter:
        query = query.filter_by(class_id=class_filter)
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
    subjects = Subject.query.filter(Subject.class_id.isnot(None)).order_by(Subject.name).all()
    classes = SchoolClass.query.order_by(SchoolClass.display_order, SchoolClass.name).all()

    return render_template(
        'teacher/content_list.html',
        pagination=pagination,
        classes=classes,
        subjects=subjects,
        class_filter=class_filter,
        status_filter=status_filter,
        subject_filter=subject_filter,
        type_filter=type_filter,
        search=search,
        sort=sort,
    )


@teacher_bp.route('/content/create', methods=['GET', 'POST'])
@teacher_required
def create_content():
    options = _catalog_form_options()

    if request.method == 'POST':
        payload = _content_form_payload()
        errors = _validate_content_payload(payload)
        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template(
                'teacher/content_form.html',
                **options,
                content=None,
                form_data=request.form,
            ), 400

        item = Content(
            title=payload['title'],
            slug=Content.unique_slug(payload['title']),
            description=payload['description'],
            class_id=payload['class_id'],
            subject_id=payload['subject_id'],
            chapter_id=payload['chapter_id'],
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
        'teacher/content_form.html', **options, content=None, form_data=request.args
    )


@teacher_bp.route('/content/<int:id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_content(id):
    item = db.session.get(Content, id)
    if item is None:
        abort(404)
    options = _catalog_form_options()

    if request.method == 'POST':
        payload = _content_form_payload()
        errors = _validate_content_payload(payload, existing=item)
        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template(
                'teacher/content_form.html',
                content=item,
                **options,
                form_data=request.form,
            ), 400

        was_published = item.is_published
        item.title = payload['title']
        item.slug = Content.unique_slug(payload['title'], exclude_id=item.id)
        item.description = payload['description']
        item.class_id = payload['class_id']
        item.subject_id = payload['subject_id']
        item.chapter_id = payload['chapter_id']
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
        **options,
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
    if not item.is_published and (
        item.chapter is None or not item.chapter.is_published
    ):
        flash('Assign this content to a published chapter before publishing it.', 'error')
        return redirect(url_for('teacher.content_list'))
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
    search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    query = Announcement.query
    if search:
        pattern = f'%{search}%'
        query = query.filter(db.or_(
            Announcement.title.ilike(pattern), Announcement.body.ilike(pattern),
        ))
    if status_filter == 'published':
        query = query.filter_by(is_published=True)
    elif status_filter == 'draft':
        query = query.filter_by(is_published=False)
    pagination = query.order_by(Announcement.created_at.desc()).paginate(
        page=page, per_page=FILE_PER_PAGE, error_out=False
    )
    return render_template(
        'teacher/announcements.html', pagination=pagination,
        search=search, status_filter=status_filter,
    )


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
    class_filter = request.args.get('class_id', type=int)
    query = User.query.filter_by(role='student')
    if search:
        pattern = f'%{search}%'
        query = query.filter(
            db.or_(User.name.ilike(pattern), User.email.ilike(pattern))
        )
    if class_filter:
        query = query.filter(User.class_id == class_filter)
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=STUDENT_PER_PAGE, error_out=False
    )
    classes = SchoolClass.query.order_by(SchoolClass.display_order, SchoolClass.name).all()
    return render_template(
        'teacher/students.html', pagination=pagination, search=search,
        class_filter=class_filter,
        classes=classes,
        class_names={school_class.id: school_class.name for school_class in classes},
    )


# ── Files ──────────────────────────────────────────────────
@teacher_bp.route('/files')
@teacher_required
def files():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    query = UploadedFile.query
    if search:
        pattern = f'%{search}%'
        query = query.filter(db.or_(
            UploadedFile.original_name.ilike(pattern),
            UploadedFile.mime_type.ilike(pattern),
            UploadedFile.stored_name.ilike(pattern),
        ))
    pagination = query.order_by(UploadedFile.created_at.desc()).paginate(
        page=page, per_page=FILE_PER_PAGE, error_out=False
    )
    return render_template('teacher/files.html', pagination=pagination, search=search)


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
