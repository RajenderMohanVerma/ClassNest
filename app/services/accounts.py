"""Shared account-management logic for the teacher and student profiles."""

from email_validator import EmailNotValidError, validate_email

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

    user.name = name
    if email:
        user.email = email
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