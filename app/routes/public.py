from flask import Blueprint, render_template

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    from flask import session, redirect, url_for
    if 'user_id' in session:
        if session.get('user_role') == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))


@public_bp.route('/offline')
def offline():
    """Offline fallback page used by the service worker."""
    return render_template('public/offline.html')