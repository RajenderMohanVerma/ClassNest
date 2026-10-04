import re
from datetime import datetime, timezone

from app.extensions import db


CONTENT_TYPE_LABELS = {
    'notes': 'Notes',
    'study_material': 'Study Material',
    'pdf_resource': 'PDF Resource',
    'video_lesson': 'Video Lesson',
    'announcement': 'Announcement',
    'reference_link': 'Reference Link',
}


class Content(db.Model):
    __tablename__ = 'content'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='RESTRICT'), nullable=False, index=True)
    topic = db.Column(db.String(200), nullable=True, index=True)
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
    published_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint(status.in_(['draft', 'published']), name='ck_content_status'),
        db.CheckConstraint(content_type.in_(list(CONTENT_TYPE_LABELS)), name='ck_content_type'),
    )

    files = db.relationship(
        'UploadedFile',
        backref='content',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    @staticmethod
    def generate_slug(title):
        slug = re.sub(r'[^\w\s-]', '', (title or '').lower())
        slug = re.sub(r'[\s_]+', '-', slug).strip('-')
        return slug or 'content'

    @classmethod
    def unique_slug(cls, title, exclude_id=None):
        """Return a slug that is not used by another content record."""
        base = cls.generate_slug(title)
        slug = base
        counter = 2
        while True:
            query = cls.query.filter_by(slug=slug)
            if exclude_id is not None:
                query = query.filter(cls.id != exclude_id)
            if not query.first():
                return slug
            slug = f'{base}-{counter}'
            counter += 1

    @property
    def tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def is_published(self):
        return self.status == 'published'

    @property
    def content_type_label(self):
        return CONTENT_TYPE_LABELS.get(self.content_type, self.content_type.replace('_', ' ').title())

    def summary(self, length=90):
        """Plain-text preview that is safe for card listings.

        Templates call ``content.summary(90)``; this must stay a method, not a
        property, because the caller supplies the length. Templates previously
        sliced ``body_html`` directly, which raised a TypeError for content
        without a body.
        """
        if self.description:
            text = self.description.strip()
        elif self.body_html:
            text = re.sub(r'<[^>]+>', ' ', self.body_html)
            text = re.sub(r'\s+', ' ', text).strip()
        else:
            text = ''
        if len(text) > length:
            text = f'{text[:length].rstrip()}...'
        return text

    def publish(self):
        self.status = 'published'
        self.published_at = self.published_at or datetime.now(timezone.utc)

    def unpublish(self):
        self.status = 'draft'
        self.published_at = None

    def toggle_published(self):
        if self.is_published:
            self.unpublish()
        else:
            self.publish()
        return self.is_published

    def __repr__(self):
        return f'<Content {self.title}>'