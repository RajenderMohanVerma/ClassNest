from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models.enums import (
    ACCOUNT_ACTIVE,
    ACCOUNT_DISABLED,
    ACCOUNT_STATUSES,
    ACCOUNT_SUSPENDED,
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    avatar = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(40), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    class_id = db.Column(
        db.Integer,
        # use_alter breaks the classes <-> users reference cycle so PostgreSQL
        # can create both tables in one pass.
        db.ForeignKey('classes.id', ondelete='SET NULL', use_alter=True, name='fk_users_class_id'),
        nullable=True,
        index=True,
    )
    account_status = db.Column(db.String(20), nullable=False, default=ACCOUNT_ACTIVE, index=True)
    is_email_verified = db.Column(db.Boolean, nullable=False, default=False, index=True)
    email_verified_at = db.Column(db.DateTime(timezone=True), nullable=True)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint(role.in_(['teacher', 'student']), name='ck_users_role'),
        db.CheckConstraint(account_status.in_(ACCOUNT_STATUSES), name='ck_users_account_status'),
    )

    subjects = db.relationship('Subject', backref='creator', lazy='dynamic')
    content = db.relationship('Content', backref='author', lazy='dynamic')
    announcements = db.relationship('Announcement', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def role_label(self):
        return 'Teacher' if self.is_teacher else 'Student'

    @property
    def is_active(self):
        return self.account_status == ACCOUNT_ACTIVE

    @property
    def is_suspended(self):
        return self.account_status == ACCOUNT_SUSPENDED

    @property
    def is_disabled(self):
        return self.account_status == ACCOUNT_DISABLED

    @property
    def can_login(self):
        """Only active accounts may authenticate."""
        return self.is_active

    @property
    def account_status_label(self):
        return self.account_status.title()

    def mark_login(self):
        self.last_login_at = datetime.now(timezone.utc)

    def verify_email(self):
        self.is_email_verified = True
        self.email_verified_at = datetime.now(timezone.utc)

    def suspend(self):
        self.account_status = ACCOUNT_SUSPENDED

    def disable(self):
        self.account_status = ACCOUNT_DISABLED

    def activate(self):
        self.account_status = ACCOUNT_ACTIVE

    @property
    def initials(self):
        parts = [p for p in (self.name or '').split() if p]
        if not parts:
            return '?'
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    def __repr__(self):
        return f'<User {self.email}>'
