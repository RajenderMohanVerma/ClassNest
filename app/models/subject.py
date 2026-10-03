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

    content = db.relationship('Content', backref='subject', lazy='dynamic')

    @staticmethod
    def generate_slug(name):
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[\s_]+', '-', slug).strip('-')
        return slug

    def __repr__(self):
        return f'<Subject {self.name}>'
