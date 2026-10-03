from flask import Blueprint, jsonify, session

from app.extensions import db
from app.models.announcement import Announcement
from app.models.content import CONTENT_TYPE_LABELS, Content
from app.models.subject import Subject
from app.models.uploaded_file import UploadedFile
from app.models.user import User

api_bp = Blueprint('api', __name__)


def _is_teacher():
    return session.get('user_id') is not None and session.get('user_role') == 'teacher'


@api_bp.route('/stats')
def stats():
    """Dashboard statistics for teachers."""
    if not _is_teacher():
        return jsonify({'error': 'Unauthorized'}), 403

    total_bytes = db.session.query(
        db.func.coalesce(db.func.sum(UploadedFile.size_bytes), 0)
    ).scalar()

    return jsonify({
        'total_content': Content.query.count(),
        'published': Content.query.filter_by(status='published').count(),
        'drafts': Content.query.filter_by(status='draft').count(),
        'subjects': Subject.query.count(),
        'students': User.query.filter_by(role='student').count(),
        'announcements': Announcement.query.count(),
        'published_announcements': Announcement.query.filter_by(is_published=True).count(),
        'files': UploadedFile.query.count(),
        'total_file_bytes': int(total_bytes or 0),
    })


@api_bp.route('/content-types')
def content_types():
    """Published content grouped by type (available to any signed-in user)."""
    if session.get('user_id') is None:
        return jsonify({'error': 'Unauthorized'}), 403

    rows = (
        db.session.query(Content.content_type, db.func.count(Content.id))
        .filter(Content.status == 'published')
        .group_by(Content.content_type)
        .all()
    )

    return jsonify({
        'labels': CONTENT_TYPE_LABELS,
        'counts': {content_type: count for content_type, count in rows},
        'total': sum(count for _, count in rows),
    })