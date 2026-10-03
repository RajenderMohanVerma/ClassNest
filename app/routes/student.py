import os

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session, current_app, send_from_directory, abort)

from app.extensions import db
from app.models.user import User
from app.models.subject import Subject
from app.models.content import Content
from app.models.announcement import Announcement
from app.services.decorators import student_required

student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@student_required
def dashboard():
    recent_content = Content.query.filter_by(status='published').order_by(
        Content.created_at.desc()
    ).limit(6).all()

    subjects = Subject.query.order_by(Subject.name).all()

    announcements = Announcement.query.filter_by(is_published=True).order_by(
        Announcement.published_at.desc()
    ).limit(3).all()

    return render_template('student/dashboard.html',
                           recent_content=recent_content,
                           subjects=subjects,
                           announcements=announcements)


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
    pagination = Content.query.filter_by(
        subject_id=subj.id, status='published'
    ).order_by(Content.created_at.desc()).paginate(page=page, per_page=12, error_out=False)

    return render_template('student/subject_detail.html', subject=subj, pagination=pagination)


@student_bp.route('/content')
@student_required
def content_library():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    subject_filter = request.args.get('subject', '')
    type_filter = request.args.get('type', '')
    sort = request.args.get('sort', 'newest')

    query = Content.query.filter_by(status='published')

    if search:
        query = query.filter(
            db.or_(
                Content.title.ilike(f'%{search}%'),
                Content.description.ilike(f'%{search}%'),
                Content.tags.ilike(f'%{search}%'),
            )
        )
    if subject_filter:
        query = query.filter_by(subject_id=int(subject_filter))
    if type_filter:
        query = query.filter_by(content_type=type_filter)

    if sort == 'oldest':
        query = query.order_by(Content.created_at.asc())
    else:
        query = query.order_by(Content.created_at.desc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    subjects = Subject.query.order_by(Subject.name).all()

    return render_template('student/content_library.html',
                           pagination=pagination, subjects=subjects,
                           search=search, subject_filter=subject_filter,
                           type_filter=type_filter, sort=sort)


@student_bp.route('/content/<slug>')
@student_required
def content_detail(slug):
    item = Content.query.filter_by(slug=slug, status='published').first_or_404()
    related = Content.query.filter(
        Content.subject_id == item.subject_id,
        Content.status == 'published',
        Content.id != item.id
    ).order_by(Content.created_at.desc()).limit(4).all()

    return render_template('student/content_detail.html', content=item, related=related)


@student_bp.route('/content/<slug>/download')
@student_required
def download_attachment(slug):
    item = Content.query.filter_by(slug=slug, status='published').first_or_404()
    if not item.attachment:
        abort(404)
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        item.attachment,
        as_attachment=True
    )


@student_bp.route('/announcements')
@student_required
def announcements():
    items = Announcement.query.filter_by(is_published=True).order_by(
        Announcement.published_at.desc()
    ).all()
    return render_template('student/announcements.html', announcements=items)


@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
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
                    return render_template('student/profile.html', user=user)
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

        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', user=user)


@student_bp.route('/search')
@student_required
def search():
    q = request.args.get('q', '').strip()
    results = []
    if q:
        results = Content.query.filter(
            Content.status == 'published',
            db.or_(
                Content.title.ilike(f'%{q}%'),
                Content.description.ilike(f'%{q}%'),
                Content.tags.ilike(f'%{q}%'),
                Content.topic.ilike(f'%{q}%'),
            )
        ).order_by(Content.created_at.desc()).limit(50).all()

    return render_template('student/search.html', query=q, results=results)
