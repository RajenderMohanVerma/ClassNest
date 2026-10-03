import os
import uuid
import mimetypes

from flask import current_app
from werkzeug.utils import secure_filename


ALLOWED_MIME_PREFIXES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain',
    'image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/svg+xml',
}


def allowed_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def validate_mime(file_storage):
    mime = file_storage.content_type or ''
    return mime in ALLOWED_MIME_PREFIXES


def save_upload(file_storage):
    if not file_storage or not file_storage.filename:
        return None, 'No file selected.'

    if not allowed_file(file_storage.filename):
        return None, 'File type not allowed.'

    if not validate_mime(file_storage):
        return None, 'Invalid file type detected.'

    original = secure_filename(file_storage.filename)
    ext = original.rsplit('.', 1)[1].lower() if '.' in original else ''
    stored = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_dir, stored)
    file_storage.save(filepath)

    size = os.path.getsize(filepath)
    mime = file_storage.content_type or mimetypes.guess_type(original)[0] or 'application/octet-stream'

    return {
        'original_name': original,
        'stored_name': stored,
        'mime_type': mime,
        'size_bytes': size,
    }, None
