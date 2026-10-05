"""Reusable model behaviour for ClassNext."""

import re
from datetime import datetime, timezone


def utcnow():
    """Timezone-aware ``now`` used as the default for every timestamp column."""
    return datetime.now(timezone.utc)


def as_utc(value):
    """Return ``value`` as a timezone-aware UTC datetime.

    SQLite (used by the test-suite) drops the offset on ``TIMESTAMPTZ`` columns
    and hands back naive datetimes, which would make every ``value > utcnow()``
    comparison raise ``TypeError``. Normalising here keeps expiry and
    "is it due yet" logic identical on SQLite and PostgreSQL.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def slugify(value, fallback='item'):
    """Lowercase, dash-separated, URL-safe slug."""
    slug = re.sub(r'[^\w\s-]', '', (value or '').lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')
    return slug or fallback


class SlugMixin:
    """Adds ``slug`` generation with collision avoidance.

    ``unique_slug`` is a classmethod that relies on the concrete model exposing a
    ``query`` and an integer ``id``; both are true for every ClassNext model that
    mixes this in.
    """

    slug_fallback = 'item'

    @classmethod
    def generate_slug(cls, value):
        return slugify(value, cls.slug_fallback)

    @classmethod
    def unique_slug(cls, value, exclude_id=None):
        base = cls.generate_slug(value)
        slug = base
        counter = 2
        while True:
            query = cls.query.filter_by(slug=slug)
            if exclude_id is not None:
                query = query.filter(cls.id != exclude_id)
            if not query.first():
                return slug
            slug = f'{base}-{counter}'
            counter += 1