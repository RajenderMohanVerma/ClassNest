from datetime import datetime, timezone

from app.extensions import db


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=False, nullable=False, index=True)
    published_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def publish(self):
        self.is_published = True
        self.published_at = self.published_at or datetime.now(timezone.utc)

    def unpublish(self):
        self.is_published = False
        self.published_at = None

    @property
    def summary(self, length=150):
        import re
        text = re.sub(r'<[^>]+>', ' ', self.body or '')
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > length:
            text = f'{text[:length].rstrip()}...'
        return text

    def __repr__(self):
        return f'<Announcement {self.title}>'