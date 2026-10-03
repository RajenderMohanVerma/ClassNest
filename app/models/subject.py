import re
from datetime import datetime, timezone

from app.extensions import db


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(100), default='bi-book')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    content = db.relationship(
        'Content',
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

    def __repr__(self):
        return f'<Subject {self.name}>'