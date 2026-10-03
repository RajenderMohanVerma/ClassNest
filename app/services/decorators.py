from functools import wraps
from urllib.parse import urlparse

from flask import abort, flash, redirect, request, session, url_for


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login', next=request.full_path))
        return f(*args, **kwargs)
    return decorated


def teacher_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login', next=request.full_path))
        if session.get('user_role') != 'teacher':
            abort(403)
        return f(*args, **kwargs)
    return decorated


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login', next=request.full_path))
        if session.get('user_role') != 'student':
            abort(403)
        return f(*args, **kwargs)
    return decorated


def safe_next_url(target, fallback):
    """Only allow same-site relative redirects, to avoid open redirects."""
    if not target:
        return None
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc:
        return None
    if not target.startswith('/') or target.startswith('//'):
        return None
    if target.startswith('/auth/'):
        return None
    return target or fallback