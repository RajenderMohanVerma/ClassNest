"""Student engagement: bookmarks, history, progress and notifications."""

from app.extensions import db
from app.models.enums import NOTIFICATION_TYPES, NOTIFICATION_INFO
from app.models.mixins import utcnow


class BookmarkTarget:
    """Polymorphic target kinds used by bookmarks and viewing history."""

    CONTENT = 'content'
    COURSE = 'course'
    LESSON = 'lesson'

    ALL = (CONTENT, COURSE, LESSON)


#: Shared SQL for the ``target_type`` CHECK constraints.
TARGET_TYPE_CHECK_SQL = "target_type IN ('content', 'course', 'lesson')"


class _TargetMixin:
    """Shared lookup for the small polymorphic target columns."""

    target_type = db.Column(db.String(20), nullable=False, index=True)
    target_id = db.Column(db.Integer, nullable=False, index=True)

    @property
    def target(self):
        """Return the referenced ORM object, or ``None`` if it was removed."""
        if self.target_type == BookmarkTarget.CONTENT:
            from app.models.content import Content

            return db.session.get(Content, self.target_id)
        if self.target_type == BookmarkTarget.COURSE:
            from app.models.course import Course

            return db.session.get(Course, self.target_id)
        if self.target_type == BookmarkTarget.LESSON:
            from app.models.course import CourseLesson

            return db.session.get(CourseLesson, self.target_id)
        return None


class Bookmark(_TargetMixin, db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    note = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'target_type', 'target_id', name='uq_bookmarks_user_target'),
        db.CheckConstraint(TARGET_TYPE_CHECK_SQL, name='ck_bookmarks_target_type'),
    )

    def __repr__(self):
        return f'<Bookmark user={self.user_id} {self.target_type}:{self.target_id}>'


class RecentlyViewed(_TargetMixin, db.Model):
    __tablename__ = 'recently_viewed'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    viewed_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'target_type', 'target_id', name='uq_recently_viewed_user_target'),
        db.CheckConstraint(TARGET_TYPE_CHECK_SQL, name='ck_recently_viewed_target_type'),
    )

    @staticmethod
    def record(user_id, target_type, target_id):
        """Create or refresh one history row; returns the row."""
        row = RecentlyViewed.query.filter_by(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
        ).first()
        if row is None:
            row = RecentlyViewed(
                user_id=user_id,
                target_type=target_type,
                target_id=target_id,
            )
            db.session.add(row)
        row.viewed_at = utcnow()
        return row


class LearningProgress(db.Model):
    """Per-student completion state for a single content item / lesson."""

    __tablename__ = 'learning_progress'

    COMPLETE_THRESHOLD = 90  # percent watched/ read considered finished

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id', ondelete='CASCADE'), nullable=False, index=True)
    progress_percent = db.Column(db.Integer, nullable=False, default=0)
    position_seconds = db.Column(db.Integer, nullable=False, default=0)
    is_completed = db.Column(db.Boolean, nullable=False, default=False, index=True)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    last_viewed_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'content_id', name='uq_learning_progress_user_content'),
        db.CheckConstraint(
            'progress_percent >= 0 AND progress_percent <= 100',
            name='ck_learning_progress_percent',
        ),
    )

    content = db.relationship('Content', backref=db.backref('progress_records', lazy='dynamic'))

    @property
    def percent(self):
        return max(0, min(100, int(self.progress_percent or 0)))

    def update_from(self, percent=None, position_seconds=None):
        """Apply a reported watch/read position, clamped and idempotent."""
        changed = False
        if percent is not None:
            value = max(0, min(100, int(percent)))
            if value != self.progress_percent:
                self.progress_percent = value
                changed = True
            if not self.is_completed and value >= self.COMPLETE_THRESHOLD:
                self.is_completed = True
                self.completed_at = utcnow()
            elif self.is_completed and value < self.COMPLETE_THRESHOLD:
                self.is_completed = False
                self.completed_at = None
        if position_seconds is not None:
            value = max(0, int(position_seconds))
            if value != self.position_seconds:
                self.position_seconds = value
                changed = True
        self.last_viewed_at = utcnow()
        return changed

    def __repr__(self):
        return f'<LearningProgress user={self.user_id} content={self.content_id} {self.percent}%>'


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    type = db.Column(db.String(30), nullable=False, default=NOTIFICATION_INFO, index=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=True)
    link_url = db.Column(db.String(500), nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)
    read_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    __table_args__ = (
        db.CheckConstraint(type.in_(NOTIFICATION_TYPES), name='ck_notifications_type'),
    )

    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = utcnow()
            return True
        return False

    @staticmethod
    def push(user_id, title, body=None, link_url=None, type=NOTIFICATION_INFO):
        notification = Notification(
            user_id=user_id,
            title=title,
            body=body,
            link_url=link_url,
            type=type,
        )
        db.session.add(notification)
        return notification

    def __repr__(self):
        return f'<Notification user={self.user_id} {self.title}>'