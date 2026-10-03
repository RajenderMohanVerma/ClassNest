from datetime import datetime, timezone

from app.extensions import db


class UploadedFile(db.Model):
    __tablename__ = 'uploaded_files'

    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.String(300), nullable=False)
    stored_name = db.Column(db.String(300), nullable=False, unique=True)
    mime_type = db.Column(db.String(100), nullable=False)
    size_bytes = db.Column(db.BigInteger, nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    uploader = db.relationship('User', backref='uploaded_files')

    def __repr__(self):
        return f'<UploadedFile {self.original_name}>'
