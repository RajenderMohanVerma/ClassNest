import mimetypes
import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

# Client-supplied MIME types that are acceptable, mapped to the file kinds they
# represent. Anything not listed here is rejected even if the extension matches.
ALLOWED_MIME_TYPES = {
    'application/pdf': 'document',
    'application/msword': 'document',
    'application/rtf': 'document',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'document',
    'application/vnd.ms-powerpoint': 'document',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'document',
    'application/vnd.ms-excel': 'document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'document',
    'text/plain': 'text',
    'text/markdown': 'text',
    'text/csv': 'text',
    'image/png': 'image',
    'image/jpeg': 'image',
    'image/gif': 'image',
    'image/webp': 'image',
}

IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

MAGIC_SIGNATURES = (
    (b'%PDF-', 'application/pdf'),
    (b'\x89PNG\r\n\x1a\n', 'image/png'),
    (b'\xff\xd8\xff', 'image/jpeg'),
    (b'GIF87a', 'image/gif'),
    (b'GIF89a', 'image/gif'),
)


def upload_root():
    """Absolute, existing upload directory for the current environment."""
    folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.isabs(folder):
        folder = os.path.join(current_app.root_path, '..', folder)
    folder = os.path.abspath(folder)
    os.makedirs(folder, exist_ok=True)
    return folder


def stored_path(stored_name):
    return os.path.join(upload_root(), stored_name)


def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def sniff_mime(path):
    """Identify well-known binary formats from their magic bytes."""
    try:
        with open(path, 'rb') as handle:
            head = handle.read(12)
    except OSError:
        return None
    for signature, mime in MAGIC_SIGNATURES:
        if head.startswith(signature):
            return mime
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'image/webp'
    if head.startswith(b'PK\x03\x04'):
        return 'application/zip-container'
    if head.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
        return 'application/ole-container'
    return None


def validate_content(file_storage, path):
    """Validate a saved file against its client MIME type and real content."""
    client_mime = (file_storage.content_type or '').split(';')[0].strip().lower()
    if client_mime not in ALLOWED_MIME_TYPES:
        return 'Unsupported file type.'

    detected = sniff_mime(path)
    if detected is None:
        # Text-based and container formats cannot be reliably sniffed; the
        # extension allowlist plus MIME allowlist already restrict them.
        return None

    if detected == 'application/zip-container':
        if ALLOWED_MIME_TYPES[client_mime] != 'document':
            return 'File content does not match the selected file type.'
        return None
    if detected == 'application/ole-container':
        if ALLOWED_MIME_TYPES[client_mime] != 'document':
            return 'File content does not match the selected file type.'
        return None

    if client_mime != detected:
        return 'File content does not match its extension.'
    return None


def save_upload(file_storage):
    """Validate and persist an uploaded file.

    Returns ``(metadata, error)``. The stored name is a UUID so user input can
    never influence the filesystem path.
    """
    if not file_storage or not file_storage.filename:
        return None, 'No file selected.'

    original = secure_filename(file_storage.filename)
    if not original:
        return None, 'Invalid file name.'
    if not allowed_file(original):
        return None, 'File type not allowed.'

    ext = original.rsplit('.', 1)[1].lower()
    stored = f'{uuid.uuid4().hex}.{ext}'
    filepath = stored_path(stored)

    try:
        file_storage.save(filepath)
    except OSError:
        return None, 'The file could not be saved.'

    if os.path.getsize(filepath) == 0:
        os.remove(filepath)
        return None, 'The uploaded file is empty.'

    error = validate_content(file_storage, filepath)
    if error:
        os.remove(filepath)
        return None, error

    if ext in IMAGE_EXTENSIONS:
        try:
            from PIL import Image  # optional, only used to reject broken images
            with Image.open(filepath) as image:
                image.verify()
        except ImportError:
            pass
        except Exception:
            os.remove(filepath)
            return None, 'The image could not be read.'

    size = os.path.getsize(filepath)
    mime = file_storage.content_type or mimetypes.guess_type(original)[0] or 'application/octet-stream'

    return {
        'original_name': original,
        'stored_name': stored,
        'mime_type': mime.split(';')[0].strip().lower(),
        'size_bytes': size,
    }, None


def delete_stored_file(stored_name):
    """Remove a file from disk; missing files are ignored."""
    if not stored_name:
        return False
    path = stored_path(stored_name)
    try:
        os.remove(path)
        return True
    except OSError:
        return False