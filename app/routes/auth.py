from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)
from email_validator import EmailNotValidError, validate_email

from app.extensions import db, limiter
from app.models.account import AccountToken
from app.models.catalog import SchoolClass
from app.models.user import User
from app.services.decorators import safe_next_url
from app.services.mailer import (is_configured as mail_is_configured,
                                 send_password_reset_email,
                                 send_verification_email)

auth_bp = Blueprint('auth', __name__)

MIN_PASSWORD_LENGTH = 6
TEACHER_CONTACT = 'the teacher'


def _now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)


def _enabled_classes():
    """Classes a new student may pick from, in display order."""
    return SchoolClass.query.filter_by(is_enabled=True).order_by(
        SchoolClass.display_order, SchoolClass.name,
    ).all()


def _home_for_role(role):
    return url_for('teacher.dashboard') if role == 'teacher' else url_for('student.dashboard')


def _dashboard_for(user):
    return _home_for_role(user.role)


def _valid_email(value):
    try:
        validate_email(value, check_deliverability=False)
    except EmailNotValidError:
        return False
    return True


def _absolute(endpoint, **values):
    """Absolute URL for an email link, using the configured public host."""
    from flask import current_app, url_for
    path = url_for(endpoint, **values)
    base = current_app.config.get('SITE_URL') or ''
    return f'{base}{path}' if base else path


def _mail_unavailable_flash():
    flash(
        'Email delivery is not switched on yet, so no link could be sent. '
        'Please contact the teacher for help.',
        'error',
    )


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if 'user_id' in session and request.method == 'GET':
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

        # A suspended or disabled account must not get a session, even with the
        # correct password.
        if not user.can_login:
            flash(
                f'Your account is {user.account_status_label.lower()}. '
                f'Please contact {TEACHER_CONTACT}.',
                'error',
            )
            return render_template('public/login.html', email=email), 403

        session.clear()
        session.permanent = bool(remember)
        session['user_id'] = user.id
        session['user_role'] = user.role
        session['user_name'] = user.name

        user.mark_login()
        db.session.commit()

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
    class_id = None
    phone = ''
    classes = _enabled_classes()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        class_id = request.form.get('class_id', type=int)

        school_class = None
        if class_id:
            school_class = db.session.get(SchoolClass, class_id)
            if school_class is None or not school_class.is_enabled:
                class_id = None

        errors = []
        if len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        if not email:
            errors.append('Email is required.')
        elif not _valid_email(email):
            errors.append('Please enter a valid email address.')
        if len(password) < MIN_PASSWORD_LENGTH:
            errors.append(f'Password must be at least {MIN_PASSWORD_LENGTH} characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if phone and not (7 <= len(phone) <= 15):
            errors.append('Phone number looks too short or too long.')
        if email and User.query.filter_by(email=email).first():
            errors.append('An account with this email already exists.')

        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template(
                'public/register.html', name=name, email=email,
                class_id=class_id, phone=phone, classes=classes,
            ), 400

        # The role is never read from the form: registration can only create
        # student accounts.
        user = User(
            name=name,
            email=email,
            role='student',
            phone=phone or None,
            class_id=class_id,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # Verification is enforced only when mail can actually deliver a link,
        # otherwise nobody could ever confirm their address.
        require_verification = mail_is_configured()
        if require_verification:
            _, raw_token = AccountToken.issue(
                user.id, AccountToken.verification_purpose(),
            )
        db.session.commit()

        if require_verification:
            sent = send_verification_email(
                user.email, user.name,
                _absolute('auth.verify_email', token=raw_token),
            )
            if sent:
                flash('Account created. Check your inbox to verify your email.', 'success')
                return redirect(url_for('auth.login'))
            db.session.rollback()
            # The link never reached the user, so do not leave a permanently
            # unusable account behind: remove it and ask them to try again.
            db.session.delete(user)
            db.session.commit()
            _mail_unavailable_flash()
            return render_template(
                'public/register.html', name=name, email=email,
                class_id=class_id, phone=phone, classes=classes,
            ), 503

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template(
        'public/register.html', name=name, email=email,
        class_id=class_id, phone=phone, classes=classes,
    )


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def forgot_password():
    """Always shows the same confirmation, so accounts cannot be enumerated."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        if email and _valid_email(email):
            user = User.query.filter_by(email=email).first()
            if user is not None and user.can_login:
                _, raw_token = AccountToken.issue(
                    user.id, AccountToken.reset_purpose(),
                )
                db.session.commit()
                send_password_reset_email(
                    user.email, user.name,
                    _absolute('auth.reset_password', token=raw_token),
                )

        flash(
            'If that email has an active account, a reset link is on its way. '
            'Check your inbox and your spam folder.',
            'info',
        )
        return redirect(url_for('auth.forgot_password'))

    return render_template('public/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def reset_password(token):
    record = AccountToken.consume(token, AccountToken.reset_purpose())
    if record is None:
        flash('This reset link is invalid or has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.forgot_password'))

    user = db.session.get(User, record.user_id)
    if user is None:
        flash('This reset link is invalid or has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        errors = []
        if len(password) < MIN_PASSWORD_LENGTH:
            errors.append(f'Password must be at least {MIN_PASSWORD_LENGTH} characters.')
        if password != confirm:
            errors.append('Passwords do not match.')

        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template(
                'public/reset_password.html', token=token,
            ), 400

        user.set_password(password)
        # Any other outstanding reset link is now stale.
        AccountToken.query.filter(
            AccountToken.user_id == user.id,
            AccountToken.purpose == AccountToken.reset_purpose(),
            AccountToken.used_at.is_(None),
        ).update({'used_at': _now()}, synchronize_session=False)

        # The reset proves control of the mailbox, so confirm the address too.
        if not user.is_email_verified:
            user.verify_email()
        db.session.commit()

        session.clear()
        flash('Your password has been changed. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('public/reset_password.html', token=token)


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    record = AccountToken.consume(token, AccountToken.verification_purpose())
    if record is None:
        flash('This verification link is invalid or has expired. Request a new one below.', 'error')
        return redirect(url_for('auth.login'))

    user = db.session.get(User, record.user_id)
    if user is None:
        flash('This verification link is invalid or has expired. Request a new one below.', 'error')
        return redirect(url_for('auth.login'))

    user.verify_email()
    db.session.commit()
    flash('Your email address is verified. You have full access to your account.', 'success')
    return redirect(_dashboard_for(user))


@auth_bp.route('/resend-verification', methods=['POST'])
@limiter.limit("3 per minute")
def resend_verification():
    """Re-send the verification link for the signed-in account."""
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    user = db.session.get(User, user_id)
    if user is None:
        session.clear()
        flash('Please log in again.', 'warning')
        return redirect(url_for('auth.login'))

    if user.is_email_verified:
        flash('Your email address is already verified.', 'info')
        return redirect(_dashboard_for(user))

    _, raw_token = AccountToken.issue(
        user.id, AccountToken.verification_purpose(),
    )
    db.session.commit()

    sent = send_verification_email(
        user.email, user.name,
        _absolute('auth.verify_email', token=raw_token),
    )
    if sent:
        flash('A new verification link is on its way.', 'success')
    else:
        _mail_unavailable_flash()
    return redirect(_dashboard_for(user))