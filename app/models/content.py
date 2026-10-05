import re
from datetime import datetime, timezone

from app.extensions import db
from app.models.enums import (
    ACCESS_LOGGED_IN,
    ACCESS_LEVELS,
    CONTENT_STATUS_ARCHIVED,
    CONTENT_STATUS_DRAFT,
    CONTENT_STATUS_LABELS,
    CONTENT_STATUS_PUBLISHED,
    CONTENT_STATUS_SCHEDULED,
    CONTENT_STATUS_UNPUBLISHED,
    CONTENT_STATUSES,
    HIDDEN_CONTENT_STATUSES,
    label_for,
)


CONTENT_TYPE_LABELS = {
    'notes': 'Notes',
    'study_material': 'Study Material',
    'pdf_resource': 'PDF Resource',
    'video_lesson': 'Video Lesson',
    'announcement': 'Announcement',
    'reference_link': 'Reference Link',
    'audio': 'Audio',
    'image': 'Image',
    'notice': 'Notice',
    'playlist': 'Playlist',
    'course': 'Course',
    'assignment': 'Assignment',
}

#: Types that carry a playable / viewable media asset.
MEDIA_CONTENT_TYPES = ('video_lesson', 'audio', 'image')


class Content(db.Model):
    __tablename__ = 'content'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='RESTRICT'), nullable=False, index=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='SET NULL'), nullable=True, index=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id', ondelete='SET NULL'), nullable=True, index=True)
    topic = db.Column(db.String(200), nullable=True, index=True)
    content_type = db.Column(db.String(50), nullable=False, default='notes')
    body_html = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.String(255), nullable=True)
    attachment = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(500), nullable=True)
    resource_url = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), nullable=False, default=CONTENT_STATUS_DRAFT, index=True)
    access_level = db.Column(db.String(30), nullable=False, default=ACCESS_LOGGED_IN, index=True)
    is_featured = db.Column(db.Boolean, nullable=False, default=False, index=True)
    is_preview = db.Column(db.Boolean, nullable=False, default=False)
    duration_seconds = db.Column(db.Integer, nullable=True)
    view_count = db.Column(db.Integer, nullable=False, default=0, index=True)
    scheduled_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    published_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint(status.in_(CONTENT_STATUSES), name='ck_content_status'),
        db.CheckConstraint(content_type.in_(list(CONTENT_TYPE_LABELS)), name='ck_content_type'),
        db.CheckConstraint(access_level.in_(ACCESS_LEVELS), name='ck_content_access_level'),
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
        return self.status == CONTENT_STATUS_PUBLISHED

    @property
    def status_label(self):
        return label_for(CONTENT_STATUS_LABELS, self.status)

    @property
    def is_scheduled(self):
        return self.status == CONTENT_STATUS_SCHEDULED

    @property
    def is_archived(self):
        return self.status == CONTENT_STATUS_ARCHIVED

    @property
    def is_unpublished(self):
        return self.status == CONTENT_STATUS_UNPUBLISHED

    @property
    def is_premium(self):
        return self.access_level in ('premium', 'course_specific')

    @property
    def is_publicly_visible(self):
        """Only published, publicly-scoped records reach anonymous visitors."""
        return self.is_published and self.access_level == 'public'

    @property
    def requires_purchase(self):
        return self.is_premium and not self.is_preview

    @property
    def is_hidden_from_viewers(self):
        """Draft, scheduled and archived records never reach a viewer."""
        return self.status in HIDDEN_CONTENT_STATUSES

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
        self.status = CONTENT_STATUS_PUBLISHED
        self.scheduled_at = None
        self.published_at = self.published_at or datetime.now(timezone.utc)

    def unpublish(self):
        self.status = CONTENT_STATUS_DRAFT
        self.published_at = None

    def take_offline(self):
        """Take a published item offline without losing it as a draft."""
        self.status = CONTENT_STATUS_UNPUBLISHED
        self.published_at = None

    def schedule(self, publish_at):
        """Hide the item until ``publish_at``.

        It stays invisible to every non-admin viewer, including once the time
        passes, until an admin explicitly publishes it.
        """
        self.status = CONTENT_STATUS_SCHEDULED
        self.scheduled_at = publish_at
        self.published_at = None

    def archive(self):
        self.status = CONTENT_STATUS_ARCHIVED

    def restore_to_draft(self):
        self.status = CONTENT_STATUS_DRAFT

    def toggle_published(self):
        if self.is_published:
            self.unpublish()
        else:
            self.publish()
        return self.is_published

    def __repr__(self):
        return f'<Content {self.title}>'