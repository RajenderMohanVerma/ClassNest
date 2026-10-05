import re
from datetime import datetime, timezone

from app.extensions import db
from app.models.enums import (
    CONTENT_STATUS_LABELS,
    CONTENT_STATUS_PUBLISHED,
    CONTENT_STATUSES,
    label_for,
)


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(100), default='bi-book')
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='SET NULL'), nullable=True, index=True)
    thumbnail = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default=CONTENT_STATUS_PUBLISHED, index=True)
    display_order = db.Column(db.Integer, nullable=False, default=0, index=True)
    is_enabled = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint(status.in_(CONTENT_STATUSES), name='ck_subjects_status'),
    )

    content = db.relationship(
        'Content',
        backref='subject',
        lazy='dynamic',
        passive_deletes=True,
    )
    chapters = db.relationship(
        'Chapter',
        backref='subject',
        lazy='dynamic',
        passive_deletes=True,
    )

    @staticmethod
    def generate_slug(name):
        slug = re.sub(r'[^\w\s-]', '', (name or '').lower())
        slug = re.sub(r'[\s_]+', '-', slug).strip('-')
        return slug

    @classmethod
    def unique_slug(cls, name, exclude_id=None):
        base = cls.generate_slug(name) or 'subject'
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
    def published_count(self):
        return self.content.filter_by(status='published').count()

    @property
    def total_count(self):
        return self.content.count()

    @property
    def chapter_count(self):
        return self.chapters.count()

    @property
    def status_label(self):
        return label_for(CONTENT_STATUS_LABELS, self.status)

    @property
    def is_published(self):
        return self.status == CONTENT_STATUS_PUBLISHED

    def __repr__(self):
        return f'<Subject {self.name}>'