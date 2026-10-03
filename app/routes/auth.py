from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from email_validator import validate_email, EmailNotValidError

from app.extensions import db, limiter
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if 'user_id' in session:
        if session.get('user_role') == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('public/login.html')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session.clear()
            session.permanent = True
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['user_name'] = user.name

            if user.is_teacher:
                return redirect(url_for('teacher.dashboard'))
            return redirect(url_for('student.dashboard'))

        flash('Invalid email or password.', 'error')

    return render_template('public/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if 'user_id' in session:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        errors = []
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        if not email:
            errors.append('Email is required.')
        else:
            try:
                validate_email(email)
            except EmailNotValidError:
                errors.append('Please enter a valid email address.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')

        if User.query.filter_by(email=email).first():
            errors.append('An account with this email already exists.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('public/register.html', name=name, email=email)

        user = User(name=name, email=email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('public/register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
