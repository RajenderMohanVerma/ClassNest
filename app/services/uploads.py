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
    # Some browsers and OS pickers send this generic type; the file bytes are
    # still validated strictly below.
    'application/octet-stream': 'unknown',
}

IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

OFFICE_EXTENSIONS = {'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'}

TEXT_EXTENSIONS = {'txt', 'md', 'csv', 'rtf'}

# Magic-byte signatures required per extension. A file whose real content does
# not match its extension is rejected even when the browser sent a valid
# Content-Type header.
EXTENSION_SIGNATURES = {
    'pdf': {'application/pdf'},
    'png': {'image/png'},
    'jpg': {'image/jpeg'},
    'jpeg': {'image/jpeg'},
    'gif': {'image/gif'},
    'webp': {'image/webp'},
    'doc': {'application/ole-container'},
    'docx': {'application/zip-container'},
    'ppt': {'application/ole-container'},
    'pptx': {'application/zip-container'},
    'xls': {'application/ole-container'},
    'xlsx': {'application/zip-container'},
}

MAGIC_SIGNATURES = (
    (b'%PDF-', 'application/pdf'),
    (b'\x89PNG\r\n\x1a\n', 'image/png'),
    (b'\xff\xd8\xff', 'image/jpeg'),
    (b'GIF87a', 'image/gif'),
    (b'GIF89a', 'image/gif'),
)


LEGACY_UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')


def upload_root():
    """Absolute, existing upload directory for the current environment."""
    folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.isabs(folder):
        folder = os.path.join(current_app.root_path, '..', folder)
    folder = os.path.abspath(folder)
    os.makedirs(folder, exist_ok=True)
    return folder


def legacy_upload_root():
    """Old upload location that shipped inside the public ``static`` folder.

    Files stored before uploads moved out of the static surface are still
    resolved from here so existing links keep working. ``init_db.py`` moves them
    into the current root the next time it runs.
    """
    legacy = current_app.config.get('LEGACY_UPLOAD_FOLDER', LEGACY_UPLOAD_FOLDER)
    if not os.path.isabs(legacy):
        legacy = os.path.join(current_app.root_path, '..', legacy)
    return os.path.abspath(legacy)


def stored_path(stored_name):
    """Absolute path of a stored file, falling back to the legacy folder."""
    primary = os.path.join(upload_root(), stored_name)
    if os.path.exists(primary):
        return primary
    legacy = os.path.join(legacy_upload_root(), stored_name)
    if os.path.exists(legacy):
        return legacy
    return primary


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


def validate_content(file_storage, path, extension):
    """Validate a saved file against its extension, MIME type and real bytes."""
    client_mime = (file_storage.content_type or '').split(';')[0].strip().lower()
    kind = ALLOWED_MIME_TYPES.get(client_mime)
    if kind is None:
        return 'Unsupported file type.'

    expected = EXTENSION_SIGNATURES.get(extension)
    if expected is not None:
        detected = sniff_mime(path)
        if detected not in expected:
            return 'File content does not match its file extension.'
        if extension in IMAGE_EXTENSIONS and kind != 'image':
            return 'File content does not match its file extension.'
        if extension in OFFICE_EXTENSIONS and kind != 'document':
            return 'File content does not match its file extension.'
        return None

    if extension in TEXT_EXTENSIONS:
        if kind not in ('text', 'unknown'):
            return 'File content does not match its file extension.'
        try:
            with open(path, 'rb') as handle:
                head = handle.read(4096)
        except OSError:
            return 'The file could not be read.'
        if b'\x00' in head:
            return 'File content does not match its file extension.'
        try:
            head.decode('utf-8')
        except UnicodeDecodeError:
            return 'File content does not match its file extension.'
        return None

    return 'File type not allowed.'


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
    filepath = os.path.join(upload_root(), stored)

    try:
        file_storage.save(filepath)
    except OSError:
        return None, 'The file could not be saved.'

    if os.path.getsize(filepath) == 0:
        os.remove(filepath)
        return None, 'The uploaded file is empty.'

    error = validate_content(file_storage, filepath, ext)
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
    """Remove a file from disk (current and legacy locations); missing is fine."""
    if not stored_name:
        return False
    removed = False
    for root in (upload_root(), legacy_upload_root()):
        path = os.path.join(root, stored_name)
        try:
            os.remove(path)
            removed = True
        except OSError:
            continue
    return removed