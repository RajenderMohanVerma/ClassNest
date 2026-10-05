"""Academic catalog: classes, chapters and playlists.

These are the missing links in the required hierarchy::

    Class -> Subject -> Chapter -> Content

The table is named ``classes`` and the model ``SchoolClass`` because ``Class``
is confusing to read next to ``db.Model`` and to Python's own keyword.
"""

from app.extensions import db
from app.models.enums import (
    ACCESS_PUBLIC,
    ACCESS_LEVELS,
    CONTENT_STATUS_DRAFT,
    CONTENT_STATUSES,
    CONTENT_STATUS_LABELS,
    label_for,
)
from app.models.mixins import SlugMixin, utcnow


class SchoolClass(SlugMixin, db.Model):
    __tablename__ = 'classes'

    slug_fallback = 'class'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.String(255), nullable=True)
    display_order = db.Column(db.Integer, nullable=False, default=0, index=True)
    is_enabled = db.Column(db.Boolean, nullable=False, default=True, index=True)
    status = db.Column(db.String(20), nullable=False, default='active', index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        db.CheckConstraint(status.in_(('active', 'archived')), name='ck_classes_status'),
    )

    subjects = db.relationship(
        'Subject',
        backref='school_class',
        lazy='dynamic',
        passive_deletes=True,
    )
    chapters = db.relationship('Chapter', backref='school_class', lazy='dynamic', passive_deletes=True)
    content = db.relationship(
        'Content',
        backref='school_class',
        lazy='dynamic',
        foreign_keys='Content.class_id',
        passive_deletes=True,
    )
    courses = db.relationship('Course', backref='school_class', lazy='dynamic', passive_deletes=True)
    students = db.relationship(
        'User',
        backref='school_class',
        lazy='dynamic',
        foreign_keys='User.class_id',
        passive_deletes=True,
    )

    @property
    def is_archived(self):
        return self.status == 'archived'

    @property
    def is_available(self):
        """Visible on the public site: enabled and not archived."""
        return bool(self.is_enabled) and not self.is_archived

    @property
    def subject_count(self):
        return self.subjects.count()

    def archive(self):
        self.status = 'archived'
        self.is_enabled = False

    def restore(self):
        self.status = 'active'

    def __repr__(self):
        return f'<SchoolClass {self.name}>'


class Chapter(SlugMixin, db.Model):
    __tablename__ = 'chapters'

    slug_fallback = 'chapter'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, index=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=True, index=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.String(255), nullable=True)
    display_order = db.Column(db.Integer, nullable=False, default=0, index=True)
    status = db.Column(db.String(20), nullable=False, default=CONTENT_STATUS_DRAFT, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        db.CheckConstraint(status.in_(CONTENT_STATUSES), name='ck_chapters_status'),
    )

    content = db.relationship(
        'Content',
        backref='chapter',
        lazy='dynamic',
        passive_deletes=True,
    )
    assignments = db.relationship('Assignment', backref='chapter', lazy='dynamic', passive_deletes=True)

    @property
    def status_label(self):
        return label_for(CONTENT_STATUS_LABELS, self.status)

    @property
    def is_published(self):
        return self.status == 'published'

    def __repr__(self):
        return f'<Chapter {self.title}>'


class Playlist(SlugMixin, db.Model):
    __tablename__ = 'playlists'

    slug_fallback = 'playlist'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.String(255), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='SET NULL'), nullable=True, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True, index=True)
    access_level = db.Column(db.String(30), nullable=False, default=ACCESS_PUBLIC, index=True)
    status = db.Column(db.String(20), nullable=False, default=CONTENT_STATUS_DRAFT, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        db.CheckConstraint(status.in_(CONTENT_STATUSES), name='ck_playlists_status'),
        db.CheckConstraint(access_level.in_(ACCESS_LEVELS), name='ck_playlists_access_level'),
    )

    items = db.relationship(
        'PlaylistItem',
        backref='playlist',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    @property
    def is_premium(self):
        return self.access_level in ('premium', 'course_specific')

    @property
    def status_label(self):
        return label_for(CONTENT_STATUS_LABELS, self.status)

    def __repr__(self):
        return f'<Playlist {self.title}>'


class PlaylistItem(db.Model):
    """Ordered membership of a :class:`Playlist`."""

    __tablename__ = 'playlist_items'

    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(
        db.Integer,
        db.ForeignKey('playlists.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    content_id = db.Column(db.Integer, db.ForeignKey('content.id', ondelete='CASCADE'), nullable=False, index=True)
    display_order = db.Column(db.Integer, nullable=False, default=0, index=True)
    added_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    __table_args__ = (
        db.UniqueConstraint('playlist_id', 'content_id', name='uq_playlist_items_member'),
    )

    content = db.relationship('Content', backref=db.backref('playlist_items', lazy='dynamic'))

    @property
    def position(self):
        return self.display_order + 1

    def __repr__(self):
        return f'<PlaylistItem playlist={self.playlist_id} content={self.content_id}>'