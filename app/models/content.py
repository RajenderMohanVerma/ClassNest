import re
from datetime import datetime, timezone

from app.extensions import db


class Content(db.Model):
    __tablename__ = 'content'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='RESTRICT'), nullable=False, index=True)
    topic = db.Column(db.String(200), nullable=True)
    content_type = db.Column(db.String(50), nullable=False, default='notes')
    body_html = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.String(255), nullable=True)
    attachment = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(500), nullable=True)
    resource_url = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='draft', index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint(status.in_(['draft', 'published']), name='ck_content_status'),
        db.CheckConstraint(content_type.in_([
            'notes', 'study_material', 'pdf_resource', 'video_lesson',
            'announcement', 'reference_link'
        ]), name='ck_content_type'),
    )

    files = db.relationship('UploadedFile', backref='content', lazy='dynamic')

    @staticmethod
    def generate_slug(title):
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[\s_]+', '-', slug).strip('-')
        return slug

    @property
    def tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def __repr__(self):
        return f'<Content {self.title}>'
