"""Assignments and student submissions."""

from app.extensions import db
from app.models.enums import (
    CONTENT_STATUS_DRAFT,
    CONTENT_STATUSES,
    CONTENT_STATUS_LABELS,
    label_for,
)
from app.models.mixins import SlugMixin, as_utc, utcnow


SUBMISSION_SUBMITTED = 'submitted'
SUBMISSION_UNDER_REVIEW = 'under_review'
SUBMISSION_GRADED = 'graded'
SUBMISSION_RETURNED = 'returned'

SUBMISSION_STATUSES = (
    SUBMISSION_SUBMITTED,
    SUBMISSION_UNDER_REVIEW,
    SUBMISSION_GRADED,
    SUBMISSION_RETURNED,
)

SUBMISSION_STATUS_LABELS = {
    SUBMISSION_SUBMITTED: 'Submitted',
    SUBMISSION_UNDER_REVIEW: 'Under Review',
    SUBMISSION_GRADED: 'Graded',
    SUBMISSION_RETURNED: 'Returned',
}


class Assignment(SlugMixin, db.Model):
    __tablename__ = 'assignments'

    slug_fallback = 'assignment'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    instructions = db.Column(db.Text, nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='SET NULL'), nullable=True, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True, index=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id', ondelete='SET NULL'), nullable=True, index=True)
    max_marks = db.Column(db.Integer, nullable=True)
    due_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    status = db.Column(db.String(20), nullable=False, default=CONTENT_STATUS_DRAFT, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        db.CheckConstraint(status.in_(CONTENT_STATUSES), name='ck_assignments_status'),
    )

    submissions = db.relationship(
        'AssignmentSubmission',
        backref='assignment',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    @property
    def is_published(self):
        return self.status == 'published'

    @property
    def status_label(self):
        return label_for(CONTENT_STATUS_LABELS, self.status)

    @property
    def is_overdue(self):
        return bool(self.due_at) and as_utc(self.due_at) < utcnow()

    def summary(self, length=120):
        text = (self.instructions or '').strip()
        if len(text) > length:
            text = f'{text[:length].rstrip()}...'
        return text

    def __repr__(self):
        return f'<Assignment {self.title}>'


class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(
        db.Integer,
        db.ForeignKey('assignments.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    file_id = db.Column(db.Integer, db.ForeignKey('uploaded_files.id', ondelete='SET NULL'), nullable=True, index=True)
    note = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default=SUBMISSION_SUBMITTED, index=True)
    marks_awarded = db.Column(db.Integer, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    graded_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    graded_at = db.Column(db.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'student_id', name='uq_assignment_submissions_member'),
        db.CheckConstraint(status.in_(SUBMISSION_STATUSES), name='ck_assignment_submissions_status'),
    )

    student = db.relationship(
        'User',
        backref=db.backref('assignment_submissions', lazy='dynamic'),
        foreign_keys='AssignmentSubmission.student_id',
    )
    file = db.relationship('UploadedFile', backref=db.backref('assignment_submissions', lazy='dynamic'))

    @property
    def status_label(self):
        return label_for(SUBMISSION_STATUS_LABELS, self.status)

    @property
    def is_graded(self):
        return self.status == SUBMISSION_GRADED

    def grade(self, marks, feedback=None, admin_id=None):
        self.marks_awarded = marks
        self.feedback = feedback
        self.graded_by = admin_id
        self.graded_at = utcnow()
        self.status = SUBMISSION_GRADED

    def __repr__(self):
        return f'<AssignmentSubmission assignment={self.assignment_id} student={self.student_id}>'