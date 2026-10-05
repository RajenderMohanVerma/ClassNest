"""Shared account-management logic for the teacher and student profiles."""

from email_validator import EmailNotValidError, validate_email

from app.extensions import db

MIN_PASSWORD_LENGTH = 6


def update_profile(user, form):
    """Apply the 'update_profile' action. Returns ``(ok, message)``."""
    name = (form.get('name') or '').strip()
    email = (form.get('email') or '').strip().lower()

    if not name or len(name) < 2:
        return False, 'Name must be at least 2 characters.'

    if email and email != user.email:
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            return False, 'Please enter a valid email address.'

    from app.models.user import User

    if email and email != user.email and User.query.filter_by(email=email).first():
        return False, 'Email already in use.'

    selected_class_id = None
    if user.is_student and 'class_id' in form:
        raw_class_id = (form.get('class_id') or '').strip()
        if not raw_class_id:
            return False, 'Choose your class to see the right learning material.'
        try:
            selected_class_id = int(raw_class_id)
        except (TypeError, ValueError):
            return False, 'Choose a valid class.'
        from app.models.catalog import SchoolClass

        school_class = db.session.get(SchoolClass, selected_class_id)
        if school_class is None or not school_class.is_available:
            return False, 'Choose an active class.'

    user.name = name
    if email:
        user.email = email
    if selected_class_id is not None:
        user.class_id = selected_class_id
    return True, 'Profile updated!'


def change_password(user, form):
    """Apply the 'change_password' action. Returns ``(ok, message)``."""
    current = form.get('current_password') or ''
    new_password = form.get('new_password') or ''
    confirm = form.get('confirm_password') or ''

    if not user.check_password(current):
        return False, 'Current password is incorrect.'
    if len(new_password) < MIN_PASSWORD_LENGTH:
        return False, f'New password must be at least {MIN_PASSWORD_LENGTH} characters.'
    if new_password != confirm:
        return False, 'New passwords do not match.'
    if new_password == current:
        return False, 'New password must be different from the current password.'

    user.set_password(new_password)
    return True, 'Password changed successfully!'
