"""Course catalogue: a course owns sections, sections own lessons.

A lesson is a thin wrapper around a ``content`` row so that videos, notes, PDFs,
audio and images can be mixed inside one course without duplicating uploads.
"""

from app.extensions import db
from app.models.enums import (
    ACCESS_PREMIUM,
    ACCESS_PUBLIC,
    ACCESS_LEVELS,
    CONTENT_STATUS_DRAFT,
    CONTENT_STATUSES,
    CONTENT_STATUS_LABELS,
    label_for,
)
from app.models.mixins import SlugMixin, utcnow


class Course(SlugMixin, db.Model):
    __tablename__ = 'courses'

    slug_fallback = 'course'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(270), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.String(255), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='SET NULL'), nullable=True, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True, index=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)

    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    discount_price = db.Column(db.Numeric(10, 2), nullable=True)

    access_level = db.Column(db.String(30), nullable=False, default=ACCESS_PREMIUM, index=True)
    is_featured = db.Column(db.Boolean, nullable=False, default=False, index=True)
    status = db.Column(db.String(20), nullable=False, default=CONTENT_STATUS_DRAFT, index=True)
    scheduled_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    published_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    enrolled_count = db.Column(db.Integer, nullable=False, default=0)

    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        db.CheckConstraint(status.in_(CONTENT_STATUSES), name='ck_courses_status'),
        db.CheckConstraint(access_level.in_(ACCESS_LEVELS), name='ck_courses_access_level'),
        db.CheckConstraint(price >= 0, name='ck_courses_price_non_negative'),
    )

    sections = db.relationship(
        'CourseSection',
        backref='course',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    lessons = db.relationship('CourseLesson', backref='course', lazy='dynamic', passive_deletes=True)
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic', passive_deletes=True)
    orders = db.relationship('Order', backref='course', lazy='dynamic', passive_deletes=True)

    # -- pricing ----------------------------------------------------------

    @property
    def is_premium(self):
        return self.access_level == ACCESS_PREMIUM or (self.effective_price or 0) > 0

    @property
    def base_price(self):
        return float(self.price or 0)

    @property
    def discounted_price(self):
        """Discount price when it is a genuine reduction, else ``None``."""
        if self.discount_price is None:
            return None
        value = float(self.discount_price)
        if value < 0 or value >= self.base_price:
            return None
        return value

    @property
    def effective_price(self):
        discount = self.discounted_price
        return self.base_price if discount is None else discount

    @property
    def has_discount(self):
        return self.discounted_price is not None

    @property
    def discount_percent(self):
        discount = self.discounted_price
        if discount is None or self.base_price <= 0:
            return 0
        return int(round((1 - discount / self.base_price) * 100))

    @property
    def price_label(self):
        if not self.is_premium or self.effective_price <= 0:
            return 'Free'
        return f'{self.effective_price:,.0f}'

    @property
    def strike_price_label(self):
        if not self.has_discount:
            return ''
        return f'{self.base_price:,.0f}'

    # -- state ------------------------------------------------------------

    @property
    def status_label(self):
        return label_for(CONTENT_STATUS_LABELS, self.status)

    @property
    def is_published(self):
        return self.status == 'published'

    @property
    def lesson_count(self):
        return self.lessons.count()

    def ordered_sections(self):
        return self.sections.order_by(CourseSection.display_order).all()

    def summary(self, length=120):
        text = (self.description or '').strip()
        if len(text) > length:
            text = f'{text[:length].rstrip()}...'
        return text

    def __repr__(self):
        return f'<Course {self.title}>'


class CourseSection(SlugMixin, db.Model):
    __tablename__ = 'course_sections'

    slug_fallback = 'section'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(
        db.Integer,
        db.ForeignKey('courses.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, nullable=False, default=0, index=True)
    is_preview = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        db.UniqueConstraint('course_id', 'slug', name='uq_course_sections_slug'),
    )

    lessons = db.relationship(
        'CourseLesson',
        backref='section',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    @property
    def lesson_count(self):
        return self.lessons.count()

    def __repr__(self):
        return f'<CourseSection {self.title}>'


class CourseLesson(db.Model):
    __tablename__ = 'course_lessons'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(
        db.Integer,
        db.ForeignKey('courses.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    section_id = db.Column(
        db.Integer,
        db.ForeignKey('course_sections.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
    )
    content_id = db.Column(db.Integer, db.ForeignKey('content.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, nullable=False, default=0, index=True)
    is_preview = db.Column(db.Boolean, nullable=False, default=False)
    duration_seconds = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    content = db.relationship('Content', backref=db.backref('course_lessons', lazy='dynamic'))

    @property
    def requires_purchase(self):
        return not self.is_preview

    @property
    def duration_label(self):
        if not self.duration_seconds:
            return ''
        minutes, seconds = divmod(int(self.duration_seconds), 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f'{hours}h {minutes}m'
        if minutes:
            return f'{minutes}m {seconds}s' if seconds else f'{minutes}m'
        return f'{seconds}s'

    @property
    def position(self):
        return self.display_order + 1

    def __repr__(self):
        return f'<CourseLesson {self.title}>'