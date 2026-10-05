"""Student class access and single-use account tokens."""

import hashlib
import secrets
from datetime import timedelta

from app.extensions import db
from app.models.enums import (
    TOKEN_PURPOSE_EMAIL_VERIFICATION,
    TOKEN_PURPOSE_PASSWORD_RESET,
    TOKEN_PURPOSES,
)
from app.models.mixins import as_utc, utcnow

TOKEN_TTL_MINUTES = 60


def hash_token(raw_token):
    """Store only a digest of a reset / verification token.

    A leaked database dump then cannot be replayed against live accounts.
    """
    return hashlib.sha256((raw_token or '').encode('utf-8')).hexdigest()


def new_token():
    return secrets.token_urlsafe(32)


class StudentClassAccess(db.Model):
    """Explicit grant of one class to one student.

    Students may also see their profile class; this table records manual
    overrides so access stays auditable and reversible.
    """

    __tablename__ = 'student_class_access'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False, index=True)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reason = db.Column(db.String(300), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    granted_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'class_id', name='uq_student_class_access'),
    )

    student = db.relationship(
        'User',
        backref=db.backref('class_access', lazy='dynamic'),
        foreign_keys='StudentClassAccess.student_id',
    )
    school_class = db.relationship('SchoolClass', backref=db.backref('student_access', lazy='dynamic'))

    @property
    def is_effective(self):
        if not self.is_active:
            return False
        if self.expires_at is None:
            return True
        return as_utc(self.expires_at) > utcnow()

    def revoke(self):
        self.is_active = False
        self.revoked_at = utcnow()

    def __repr__(self):
        return f'<StudentClassAccess student={self.student_id} class={self.class_id}>'


class AccountToken(db.Model):
    """Password reset and email verification tokens (hashed, single use)."""

    __tablename__ = 'account_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token_hash = db.Column(db.String(64), nullable=False, index=True)
    purpose = db.Column(db.String(30), nullable=False, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    used_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    __table_args__ = (
        db.CheckConstraint(purpose.in_(TOKEN_PURPOSES), name='ck_account_tokens_purpose'),
    )

    @property
    def is_used(self):
        return self.used_at is not None

    @property
    def is_expired(self):
        return as_utc(self.expires_at) <= utcnow()

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired

    @classmethod
    def issue(cls, user_id, purpose, ttl_minutes=TOKEN_TTL_MINUTES):
        """Create a token row and return ``(row, raw_token)``.

        The raw value is returned once and never stored.
        """
        raw = new_token()
        row = cls(
            user_id=user_id,
            token_hash=hash_token(raw),
            purpose=purpose,
            expires_at=utcnow() + timedelta(minutes=ttl_minutes),
        )
        db.session.add(row)
        return row, raw

    @classmethod
    def consume(cls, raw_token, purpose):
        """Atomically mark a matching token used; ``None`` when invalid."""
        row = cls.query.filter_by(
            token_hash=hash_token(raw_token),
            purpose=purpose,
        ).first()
        if row is None or not row.is_valid:
            return None
        row.used_at = utcnow()
        return row

    @staticmethod
    def reset_purpose():
        return TOKEN_PURPOSE_PASSWORD_RESET

    @staticmethod
    def verification_purpose():
        return TOKEN_PURPOSE_EMAIL_VERIFICATION

    def __repr__(self):
        return f'<AccountToken user={self.user_id} {self.purpose} valid={self.is_valid}>'