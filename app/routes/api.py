from flask import Blueprint, jsonify, session
from app.models.content import Content
from app.models.subject import Subject
from app.extensions import db

api_bp = Blueprint('api', __name__)


@api_bp.route('/stats')
def stats():
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({
        'total_content': Content.query.count(),
        'published': Content.query.filter_by(status='published').count(),
        'drafts': Content.query.filter_by(status='draft').count(),
        'subjects': Subject.query.count(),
    })
