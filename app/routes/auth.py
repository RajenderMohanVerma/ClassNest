from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)
from email_validator import EmailNotValidError, validate_email

from app.extensions import db, limiter
from app.models.user import User
from app.services.decorators import safe_next_url

auth_bp = Blueprint('auth', __name__)

MIN_PASSWORD_LENGTH = 6


def _home_for_role(role):
    return url_for('teacher.dashboard') if role == 'teacher' else url_for('student.dashboard')


def _dashboard_for(user):
    return _home_for_role(user.role)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if 'user_id' in session:
        return redirect(_home_for_role(session.get('user_role')))

    email = ''
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('public/login.html', email=email), 400

        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return render_template('public/login.html', email=email), 401

        session.clear()
        session.permanent = bool(remember)
        session['user_id'] = user.id
        session['user_role'] = user.role
        session['user_name'] = user.name

        target = safe_next_url(request.args.get('next'), None)
        if target:
            return redirect(target)
        return redirect(_dashboard_for(user))

    return render_template('public/login.html', email=email)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if 'user_id' in session:
        return redirect(_home_for_role(session.get('user_role')))

    name = ''
    email = ''
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        errors = []
        if len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        if not email:
            errors.append('Email is required.')
        else:
            try:
                validate_email(email, check_deliverability=False)
            except EmailNotValidError:
                errors.append('Please enter a valid email address.')
        if len(password) < MIN_PASSWORD_LENGTH:
            errors.append(f'Password must be at least {MIN_PASSWORD_LENGTH} characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if email and User.query.filter_by(email=email).first():
            errors.append('An account with this email already exists.')

        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template('public/register.html', name=name, email=email), 400

        user = User(name=name, email=email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('public/register.html', name=name, email=email)


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))