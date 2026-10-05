"""Commerce: orders and enrollments.

Access is never granted from a browser callback. A payment provider webhook
calls :meth:`Order.mark_paid`, which only flips state after the signature has
been verified by the caller; enrollment is created from the server-side order
record, never from request data.
"""

import secrets

from app.extensions import db
from app.models.enums import (
    ENROLLMENT_ACTIVE,
    ENROLLMENT_REVOKED,
    ENROLLMENT_SOURCE_MANUAL,
    ENROLLMENT_SOURCE_PAYMENT,
    ENROLLMENT_STATUSES,
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_FAILED,
    ORDER_STATUS_PAID,
    ORDER_STATUS_PENDING,
    ORDER_STATUS_REFUNDED,
    ORDER_STATUSES,
    ORDER_STATUS_LABELS,
    SETTLED_ORDER_STATUSES,
    label_for,
)
from app.models.mixins import as_utc, utcnow


def new_order_number():
    """Human-quotable order reference, e.g. ``CN-7F3K92QD``."""
    return f'CN-{secrets.token_hex(4).upper()}'


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(32), unique=True, nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)

    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    currency = db.Column(db.String(3), nullable=False, default='INR')
    status = db.Column(db.String(20), nullable=False, default=ORDER_STATUS_PENDING, index=True)

    gateway = db.Column(db.String(30), nullable=True)
    gateway_order_id = db.Column(db.String(120), nullable=True, index=True)
    payment_reference = db.Column(db.String(160), nullable=True, index=True)
    gateway_signature = db.Column(db.String(256), nullable=True)
    failure_reason = db.Column(db.String(400), nullable=True)

    paid_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        db.CheckConstraint(status.in_(ORDER_STATUSES), name='ck_orders_status'),
        db.CheckConstraint(amount >= 0, name='ck_orders_amount_non_negative'),
    )

    enrollment = db.relationship(
        'Enrollment',
        backref=db.backref('order', uselist=False),
        lazy='select',
        passive_deletes=True,
    )
    student = db.relationship('User', backref=db.backref('orders', lazy='dynamic'))

    # -- state ------------------------------------------------------------

    @property
    def is_settled(self):
        return self.status in SETTLED_ORDER_STATUSES

    @property
    def status_label(self):
        return label_for(ORDER_STATUS_LABELS, self.status)

    @property
    def payment_status(self):
        """Alias kept for purchase-history templates."""
        return self.status

    @property
    def payment_status_label(self):
        return self.status_label

    @property
    def amount_value(self):
        return float(self.amount or 0)

    @property
    def is_cancellable(self):
        return self.status in (ORDER_STATUS_PENDING, ORDER_STATUS_FAILED)

    def mark_paid(self, payment_reference=None, gateway_order_id=None, signature=None):
        """Settle the order. Safe to call twice with the same reference."""
        if self.status == ORDER_STATUS_PAID:
            return False
        if payment_reference:
            self.payment_reference = payment_reference
        if gateway_order_id:
            self.gateway_order_id = gateway_order_id
        if signature:
            self.gateway_signature = signature
        self.status = ORDER_STATUS_PAID
        self.paid_at = utcnow()
        self.failure_reason = None
        return True

    def mark_failed(self, reason=None):
        if self.status == ORDER_STATUS_PAID:
            return False
        self.status = ORDER_STATUS_FAILED
        self.failure_reason = (reason or '')[:400] or None
        return True

    def cancel(self):
        if self.status not in (ORDER_STATUS_PENDING, ORDER_STATUS_FAILED):
            return False
        self.status = ORDER_STATUS_CANCELLED
        return True

    def refund(self, reference=None):
        if self.status != ORDER_STATUS_PAID:
            return False
        self.status = ORDER_STATUS_REFUNDED
        if reference:
            self.payment_reference = reference
        return True

    @staticmethod
    def generate_order_number():
        while True:
            candidate = new_order_number()
            if not Order.query.filter_by(order_number=candidate).first():
                return candidate

    def __repr__(self):
        return f'<Order {self.order_number} {self.status}>'


class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='SET NULL'), nullable=True, index=True)

    source = db.Column(db.String(20), nullable=False, default=ENROLLMENT_SOURCE_PAYMENT)
    status = db.Column(db.String(20), nullable=False, default=ENROLLMENT_ACTIVE, index=True)

    granted_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    revoked_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reason = db.Column(db.String(400), nullable=True)

    purchased_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        # One enrollment row per student/course. A retried payment callback
        # therefore updates the existing row instead of creating a second one.
        db.UniqueConstraint('student_id', 'course_id', name='uq_enrollments_student_course'),
        # A settled order can only ever create one enrollment.
        db.UniqueConstraint('order_id', name='uq_enrollments_order'),
        db.CheckConstraint(status.in_(ENROLLMENT_STATUSES), name='ck_enrollments_status'),
        db.CheckConstraint(
            source.in_((ENROLLMENT_SOURCE_PAYMENT, ENROLLMENT_SOURCE_MANUAL)),
            name='ck_enrollments_source',
        ),
    )

    student = db.relationship(
        'User',
        backref=db.backref('enrollments', lazy='dynamic'),
        foreign_keys='Enrollment.student_id',
    )

    @property
    def is_active(self):
        if self.status != ENROLLMENT_ACTIVE:
            return False
        if self.expires_at is None:
            return True
        return as_utc(self.expires_at) > utcnow()

    @property
    def is_revoked(self):
        return self.status == ENROLLMENT_REVOKED

    @property
    def is_manual(self):
        return self.source == ENROLLMENT_SOURCE_MANUAL

    @property
    def status_label(self):
        return 'Active' if self.is_active else 'Inactive'

    def revoke(self, admin_id=None, reason=None):
        self.status = ENROLLMENT_REVOKED
        self.revoked_at = utcnow()
        self.revoked_by = admin_id
        if reason:
            self.reason = reason[:400]

    def reactivate(self):
        self.status = ENROLLMENT_ACTIVE
        self.revoked_at = None
        self.revoked_by = None

    def __repr__(self):
        return f'<Enrollment student={self.student_id} course={self.course_id} {self.status}>'


def settled_order_for(student_id, course_id):
    """Return an already-paid order for this pair, if one exists."""
    return (
        Order.query.filter_by(
            student_id=student_id,
            course_id=course_id,
            status=ORDER_STATUS_PAID,
        )
        .order_by(Order.paid_at.desc())
        .first()
    )


def open_order_for(student_id, course_id):
    """Return a reusable pending/failed order so retries do not spam rows."""
    return (
        Order.query.filter(
            Order.student_id == student_id,
            Order.course_id == course_id,
            Order.status.in_([ORDER_STATUS_PENDING, ORDER_STATUS_FAILED]),
        )
        .order_by(Order.created_at.desc())
        .first()
    )


def active_enrollment_for(student_id, course_id):
    return (
        Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    )