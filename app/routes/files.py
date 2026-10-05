import os
import re

from flask import (Blueprint, abort, request, send_from_directory, session)

from app.extensions import db
from app.models.content import Content
from app.models.user import User
from app.models.uploaded_file import UploadedFile
from app.services.decorators import login_required
from app.services.uploads import stored_path
from app.services import access

files_bp = Blueprint('files', __name__)

STORED_NAME_PATTERN = re.compile(r'^[a-f0-9]{32}\.[A-Za-z0-9]{1,10}$')

IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def _content_allows_student(stored_name):
    published = Content.query.filter(
        db.or_(Content.thumbnail == stored_name, Content.attachment == stored_name),
        Content.status == 'published',
    ).first()
    return published is not None


@files_bp.route('/<stored_name>')
@login_required
def serve_file(stored_name):
    """Serve an uploaded object to logged-in users only.

    Uploaded files live outside the public static surface, so a student cannot
    read a draft thumbnail or an unpublished attachment by guessing a URL.
    """
    if not STORED_NAME_PATTERN.match(stored_name):
        abort(404)

    record = UploadedFile.query.filter_by(stored_name=stored_name).first()
    content = None
    if record is not None and record.content_id:
        content = db.session.get(Content, record.content_id)

    if content is None:
        content = Content.query.filter(
            db.or_(Content.thumbnail == stored_name, Content.attachment == stored_name)
        ).first()

    if content is None:
        abort(404)

    if session.get('user_role') != 'teacher':
        user = db.session.get(User, session.get('user_id'))
        if user is None or not access.can_view_content(user, content):
            abort(403)

    extension = stored_name.rsplit('.', 1)[-1].lower()
    as_attachment = extension not in IMAGE_EXTENSIONS or request.args.get('download') == '1'
    resolved = stored_path(stored_name)
    response = send_from_directory(
        os.path.dirname(resolved),
        stored_name,
        as_attachment=as_attachment,
        download_name=(record.original_name if record else stored_name),
        max_age=0,
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'none'; sandbox"
    return response


@files_bp.route('/<int:id>/download')
@login_required
def download_by_id(id):
    record = db.session.get(UploadedFile, id)
    if record is None:
        abort(404)
    content = db.session.get(Content, record.content_id) if record.content_id else None
    if session.get('user_role') != 'teacher':
        user = db.session.get(User, session.get('user_id'))
        if content is None or user is None or not access.can_view_content(user, content):
            abort(403)
    resolved = stored_path(record.stored_name)
    response = send_from_directory(
        os.path.dirname(resolved),
        record.stored_name,
        as_attachment=True,
        download_name=record.original_name,
        max_age=0,
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'none'; sandbox"
    return response
