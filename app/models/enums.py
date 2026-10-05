"""Shared vocabulary for ClassNext states.

Values are stored lowercase because the production database already stores
``draft`` / ``published`` in ``content.status``. Uppercase labels satisfy the
DRAFT / SCHEDULED / PUBLISHED / UNPUBLISHED / ARCHIVED presentation required by
the master prompt without rewriting rows that are already live.
"""

# --- Content publication states -------------------------------------------

CONTENT_STATUS_DRAFT = 'draft'
CONTENT_STATUS_SCHEDULED = 'scheduled'
CONTENT_STATUS_PUBLISHED = 'published'
CONTENT_STATUS_UNPUBLISHED = 'unpublished'
CONTENT_STATUS_ARCHIVED = 'archived'

CONTENT_STATUSES = (
    CONTENT_STATUS_DRAFT,
    CONTENT_STATUS_SCHEDULED,
    CONTENT_STATUS_PUBLISHED,
    CONTENT_STATUS_UNPUBLISHED,
    CONTENT_STATUS_ARCHIVED,
)

CONTENT_STATUS_LABELS = {
    CONTENT_STATUS_DRAFT: 'Draft',
    CONTENT_STATUS_SCHEDULED: 'Scheduled',
    CONTENT_STATUS_PUBLISHED: 'Published',
    CONTENT_STATUS_UNPUBLISHED: 'Unpublished',
    CONTENT_STATUS_ARCHIVED: 'Archived',
}

#: States that must never be rendered for a student or public visitor.
HIDDEN_CONTENT_STATUSES = frozenset({
    CONTENT_STATUS_DRAFT,
    CONTENT_STATUS_SCHEDULED,
    CONTENT_STATUS_ARCHIVED,
})

#: States that mean "deliberately taken offline by an admin".
OFFLINE_CONTENT_STATUSES = frozenset({
    CONTENT_STATUS_UNPUBLISHED,
    CONTENT_STATUS_ARCHIVED,
})

# --- Content visibility / access levels -----------------------------------

ACCESS_PUBLIC = 'public'
ACCESS_LOGGED_IN = 'logged_in'
ACCESS_CLASS_SPECIFIC = 'class_specific'
ACCESS_COURSE_SPECIFIC = 'course_specific'
ACCESS_PREMIUM = 'premium'
ACCESS_STUDENT_SPECIFIC = 'student_specific'

ACCESS_LEVELS = (
    ACCESS_PUBLIC,
    ACCESS_LOGGED_IN,
    ACCESS_CLASS_SPECIFIC,
    ACCESS_COURSE_SPECIFIC,
    ACCESS_PREMIUM,
    ACCESS_STUDENT_SPECIFIC,
)

ACCESS_LEVEL_LABELS = {
    ACCESS_PUBLIC: 'Public',
    ACCESS_LOGGED_IN: 'Logged In',
    ACCESS_CLASS_SPECIFIC: 'Class Specific',
    ACCESS_COURSE_SPECIFIC: 'Course Specific',
    ACCESS_PREMIUM: 'Premium',
    ACCESS_STUDENT_SPECIFIC: 'Student Specific',
}

#: Access levels that require a paid enrollment or a manual grant.
PAID_ACCESS_LEVELS = frozenset({ACCESS_COURSE_SPECIFIC, ACCESS_PREMIUM})

# --- Commerce -------------------------------------------------------------

ORDER_STATUS_PENDING = 'pending'
ORDER_STATUS_PAID = 'paid'
ORDER_STATUS_FAILED = 'failed'
ORDER_STATUS_REFUNDED = 'refunded'
ORDER_STATUS_CANCELLED = 'cancelled'

ORDER_STATUSES = (
    ORDER_STATUS_PENDING,
    ORDER_STATUS_PAID,
    ORDER_STATUS_FAILED,
    ORDER_STATUS_REFUNDED,
    ORDER_STATUS_CANCELLED,
)

ORDER_STATUS_LABELS = {
    ORDER_STATUS_PENDING: 'Pending',
    ORDER_STATUS_PAID: 'Paid',
    ORDER_STATUS_FAILED: 'Failed',
    ORDER_STATUS_REFUNDED: 'Refunded',
    ORDER_STATUS_CANCELLED: 'Cancelled',
}

#: Only a server-verified order may create an enrollment.
SETTLED_ORDER_STATUSES = frozenset({ORDER_STATUS_PAID})

# --- Enrollment access ----------------------------------------------------

ENROLLMENT_ACTIVE = 'active'
ENROLLMENT_REVOKED = 'revoked'
ENROLLMENT_EXPIRED = 'expired'
ENROLLMENT_COMPLETED = 'completed'

ENROLLMENT_STATUSES = (
    ENROLLMENT_ACTIVE,
    ENROLLMENT_REVOKED,
    ENROLLMENT_EXPIRED,
    ENROLLMENT_COMPLETED,
)

ENROLLMENT_SOURCE_PAYMENT = 'payment'
ENROLLMENT_SOURCE_MANUAL = 'manual'
ENROLLMENT_SOURCES = (ENROLLMENT_SOURCE_PAYMENT, ENROLLMENT_SOURCE_MANUAL)

# --- Account state --------------------------------------------------------

ACCOUNT_ACTIVE = 'active'
ACCOUNT_SUSPENDED = 'suspended'
ACCOUNT_DISABLED = 'disabled'

ACCOUNT_STATUSES = (ACCOUNT_ACTIVE, ACCOUNT_SUSPENDED, ACCOUNT_DISABLED)

# --- Notifications --------------------------------------------------------

NOTIFICATION_INFO = 'info'
NOTIFICATION_SUCCESS = 'success'
NOTIFICATION_WARNING = 'warning'
NOTIFICATION_ENROLLMENT = 'enrollment'
NOTIFICATION_ORDER = 'order'
NOTIFICATION_ANNOUNCEMENT = 'announcement'

NOTIFICATION_TYPES = (
    NOTIFICATION_INFO,
    NOTIFICATION_SUCCESS,
    NOTIFICATION_WARNING,
    NOTIFICATION_ENROLLMENT,
    NOTIFICATION_ORDER,
    NOTIFICATION_ANNOUNCEMENT,
)

# --- Tokens ---------------------------------------------------------------

TOKEN_PURPOSE_PASSWORD_RESET = 'password_reset'
TOKEN_PURPOSE_EMAIL_VERIFICATION = 'email_verification'

TOKEN_PURPOSES = (TOKEN_PURPOSE_PASSWORD_RESET, TOKEN_PURPOSE_EMAIL_VERIFICATION)

# --- Misc -----------------------------------------------------------------

SUGGESTED_TAGS = (
    'Revision',
    'Important',
    'Exam',
    'Practice',
    'Formula',
    'Homework',
    'Board',
)


def label_for(mapping, value, fallback=None):
    """Return the human label for ``value`` or a safe fallback."""
    if not value:
        return fallback or ''
    if value in mapping:
        return mapping[value]
    return fallback or str(value).replace('_', ' ').title()


def is_publishable_status(status):
    """True when a status means the record is live for allowed viewers."""
    return status == CONTENT_STATUS_PUBLISHED