"""Website CMS, teacher profile, FAQ, contact enquiries and the audit log."""

import json

from app.extensions import db
from app.models.enums import CONTENT_STATUS_DRAFT, CONTENT_STATUSES, label_for
from app.models.mixins import utcnow

SETTING_GROUPS = ('general', 'branding', 'header', 'footer', 'homepage', 'seo', 'contact', 'payment', 'email', 'media')

ENQUIRY_NEW = 'new'
ENQUIRY_IN_PROGRESS = 'in_progress'
ENQUIRY_RESOLVED = 'resolved'
ENQUIRY_SPAM = 'spam'

ENQUIRY_STATUSES = (ENQUIRY_NEW, ENQUIRY_IN_PROGRESS, ENQUIRY_RESOLVED, ENQUIRY_SPAM)

ENQUIRY_STATUS_LABELS = {
    ENQUIRY_NEW: 'New',
    ENQUIRY_IN_PROGRESS: 'In Progress',
    ENQUIRY_RESOLVED: 'Resolved',
    ENQUIRY_SPAM: 'Spam',
}


class SiteSetting(db.Model):
    """Key/value store backing /admin/settings.

    Values are stored as text and cast on read according to ``value_type`` so a
    setting can hold a boolean, a number or a JSON list without extra tables.
    """

    __tablename__ = 'site_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    value_type = db.Column(db.String(20), nullable=False, default='string')
    setting_group = db.Column(db.String(30), nullable=False, default='general', index=True)
    label = db.Column(db.String(200), nullable=True)
    is_public = db.Column(db.Boolean, nullable=False, default=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        db.CheckConstraint(
            value_type.in_(('string', 'text', 'boolean', 'integer', 'json')),
            name='ck_site_settings_value_type',
        ),
    )

    def typed_value(self, fallback=None):
        raw = self.value
        if raw is None or raw == '':
            return fallback
        try:
            if self.value_type == 'boolean':
                return str(raw).strip().lower() in ('1', 'true', 'yes', 'on')
            if self.value_type == 'integer':
                return int(raw)
            if self.value_type == 'json':
                return json.loads(raw)
        except (TypeError, ValueError):
            return fallback
        return raw

    @classmethod
    def get(cls, key, fallback=None):
        row = cls.query.filter_by(key=key).first()
        if row is None:
            return fallback
        return row.typed_value(fallback)

    @classmethod
    def set(cls, key, value, value_type='string', setting_group='general',
            label=None, is_public=True, actor_id=None):
        row = cls.query.filter_by(key=key).first()
        if row is None:
            row = cls(key=key, setting_group=setting_group)
            db.session.add(row)
        if isinstance(value, (dict, list)):
            value_type = 'json'
            value = json.dumps(value)
        elif isinstance(value, bool):
            value_type = 'boolean'
            value = 'true' if value else 'false'
        elif isinstance(value, int):
            value_type = 'integer'
        row.value = None if value is None else str(value)
        row.value_type = value_type
        row.setting_group = setting_group
        row.is_public = is_public
        if label:
            row.label = label
        if actor_id:
            row.updated_by = actor_id
        return row

    def __repr__(self):
        return f'<SiteSetting {self.key}>'


class TeacherProfile(db.Model):
    """Single-row editable profile rendered on /about and the homepage."""

    __tablename__ = 'teacher_profile'

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(120), nullable=False, default='Er. Amit Sir')
    designation = db.Column(db.String(160), nullable=True)
    headline = db.Column(db.String(250), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(40), nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    classes_taught = db.Column(db.String(200), nullable=True)
    social_links = db.Column(db.Text, nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    @property
    def social(self):
        if not self.social_links:
            return {}
        try:
            return json.loads(self.social_links)
        except (TypeError, ValueError):
            return {}

    @classmethod
    def current(cls):
        """Return the profile row, creating a seeded-but-editable one."""
        profile = cls.query.first()
        if profile is None:
            profile = cls(display_name='Er. Amit Sir')
            db.session.add(profile)
            db.session.flush()
        return profile

    def __repr__(self):
        return f'<TeacherProfile {self.display_name}>'


class Faq(db.Model):
    __tablename__ = 'faqs'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=True, index=True)
    display_order = db.Column(db.Integer, nullable=False, default=0, index=True)
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(20), nullable=False, default=CONTENT_STATUS_DRAFT, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        db.CheckConstraint(status.in_(CONTENT_STATUSES), name='ck_faqs_status'),
    )

    @property
    def is_published(self):
        return self.status == 'published'


class ContactEnquiry(db.Model):
    __tablename__ = 'contact_enquiries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    phone = db.Column(db.String(40), nullable=True)
    subject = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=ENQUIRY_NEW, index=True)
    admin_note = db.Column(db.Text, nullable=True)
    responded_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    responded_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    __table_args__ = (
        db.CheckConstraint(status.in_(ENQUIRY_STATUSES), name='ck_contact_enquiries_status'),
    )

    responded_by_user = db.relationship('User', foreign_keys=[responded_by])

    @property
    def status_label(self):
        return label_for(ENQUIRY_STATUS_LABELS, self.status)

    @property
    def is_open(self):
        return self.status in (ENQUIRY_NEW, ENQUIRY_IN_PROGRESS)


class AuditLog(db.Model):
    """Append-only trail of admin actions. Never stores credentials."""

    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    actor_email = db.Column(db.String(255), nullable=True)
    action = db.Column(db.String(80), nullable=False, index=True)
    entity_type = db.Column(db.String(60), nullable=True, index=True)
    entity_id = db.Column(db.String(60), nullable=True)
    summary = db.Column(db.String(400), nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    actor = db.relationship('User', backref=db.backref('audit_entries', lazy='dynamic'))

    SECRET_KEYS = {'password', 'new_password', 'current_password', 'token', 'secret', 'signature', 'api_key'}

    @classmethod
    def record(cls, action, actor=None, entity_type=None, entity_id=None,
               summary=None, details=None, ip_address=None):
        """Write an audit row, stripping anything that looks like a credential."""
        safe_details = None
        if details:
            if isinstance(details, dict):
                safe_details = {
                    key: value for key, value in details.items()
                    if str(key).lower() not in cls.SECRET_KEYS
                }
            else:
                safe_details = details
        return cls(
            actor_id=getattr(actor, 'id', None) if actor else None,
            actor_email=getattr(actor, 'email', None) if actor else None,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            summary=(summary or '')[:400] or None,
            details=json.dumps(safe_details) if isinstance(safe_details, dict) else safe_details,
            ip_address=ip_address,
        )

    def detail_dict(self):
        if not self.details:
            return {}
        try:
            return json.loads(self.details)
        except (TypeError, ValueError):
            return {}