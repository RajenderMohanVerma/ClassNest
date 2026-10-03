from datetime import datetime, timezone

from app.extensions import db


class UploadedFile(db.Model):
    __tablename__ = 'uploaded_files'

    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.String(300), nullable=False)
    stored_name = db.Column(db.String(300), nullable=False, unique=True)
    mime_type = db.Column(db.String(100), nullable=False)
    size_bytes = db.Column(db.BigInteger, nullable=False, index=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id', ondelete='SET NULL'), nullable=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    uploader = db.relationship('User', backref='uploaded_files')

    @property
    def is_image(self):
        return (self.mime_type or '').startswith('image/')

    @property
    def size_display(self):
        size = float(self.size_bytes or 0)
        for unit in ('B', 'KB', 'MB', 'GB'):
            if size < 1024 or unit == 'GB':
                return f'{size:.0f} {unit}' if unit == 'B' else f'{size:.2f} {unit}'
            size /= 1024
        return f'{size:.2f} GB'

    def __repr__(self):
        return f'<UploadedFile {self.original_name}>'