"""Initialize and migrate the ClassNext PostgreSQL schema.

``db.create_all()`` only creates tables that do not exist yet, so this script
also runs an additive sync for databases created by an earlier version:

* new columns on ``users`` / ``subjects`` / ``content``
* foreign keys for those columns
* widened CHECK constraints for the new content states and content types
* new indexes

Everything here is additive. No table is dropped, no column is renamed, and no
existing row is rewritten beyond backfilling defaults for new columns.

Usage:
    python init_db.py             # create tables + run the additive sync
    python init_db.py --check     # report pending changes, change nothing
"""

import os
import shutil
import sys

from sqlalchemy import inspect, text

from app import create_app, db
from app.models import (  # noqa: F401  (imported so create_all sees them)
    AccountToken,
    Announcement,
    Assignment,
    AssignmentSubmission,
    AuditLog,
    Bookmark,
    Chapter,
    ContactEnquiry,
    Content,
    Course,
    CourseLesson,
    CourseSection,
    Enrollment,
    Faq,
    LearningProgress,
    Notification,
    Order,
    Playlist,
    PlaylistItem,
    RecentlyViewed,
    SchoolClass,
    SiteSetting,
    StudentClassAccess,
    Subject,
    TeacherProfile,
    UploadedFile,
    User,
)
from app.services.uploads import legacy_upload_root, upload_root

#: Columns added after the first release, applied to existing installations.
#: NOT NULL additions carry a database-level DEFAULT so the ALTER succeeds on a
#: table that already holds rows.
ADDITIVE_COLUMNS = {
    'users': [
        'phone VARCHAR(40)',
        'bio TEXT',
        'class_id INTEGER',
        "account_status VARCHAR(20) NOT NULL DEFAULT 'active'",
        'is_email_verified BOOLEAN NOT NULL DEFAULT FALSE',
        'email_verified_at TIMESTAMPTZ',
        'last_login_at TIMESTAMPTZ',
    ],
    'subjects': [
        'class_id INTEGER',
        'thumbnail VARCHAR(255)',
        # Subjects that already exist are live, so they backfill as published.
        "status VARCHAR(20) NOT NULL DEFAULT 'published'",
        'display_order INTEGER NOT NULL DEFAULT 0',
        'is_enabled BOOLEAN NOT NULL DEFAULT TRUE',
    ],
    'content': [
        'class_id INTEGER',
        'chapter_id INTEGER',
        # 'public' keeps already-published notes and videos visible exactly as
        # they are today; new records default to 'logged_in' in the model.
        "access_level VARCHAR(30) NOT NULL DEFAULT 'public'",
        'is_featured BOOLEAN NOT NULL DEFAULT FALSE',
        'is_preview BOOLEAN NOT NULL DEFAULT FALSE',
        'duration_seconds INTEGER',
        'view_count INTEGER NOT NULL DEFAULT 0',
        'scheduled_at TIMESTAMPTZ',
    ],
    'announcements': [],
    'uploaded_files': [],
}

#: ``(table, constraint_name, column, reference_clause)``
ADDITIVE_FOREIGN_KEYS = [
    ('users', 'fk_users_class_id', 'class_id', 'REFERENCES classes(id) ON DELETE SET NULL'),
    ('subjects', 'fk_subjects_class_id', 'class_id', 'REFERENCES classes(id) ON DELETE SET NULL'),
    ('content', 'fk_content_class_id', 'class_id', 'REFERENCES classes(id) ON DELETE SET NULL'),
    ('content', 'fk_content_chapter_id', 'chapter_id', 'REFERENCES chapters(id) ON DELETE SET NULL'),
]

ADDITIVE_INDEXES = [
    'CREATE INDEX IF NOT EXISTS ix_content_topic ON content (topic)',
    'CREATE INDEX IF NOT EXISTS ix_content_published_at ON content (published_at)',
    'CREATE INDEX IF NOT EXISTS ix_content_class_id ON content (class_id)',
    'CREATE INDEX IF NOT EXISTS ix_content_chapter_id ON content (chapter_id)',
    'CREATE INDEX IF NOT EXISTS ix_content_access_level ON content (access_level)',
    'CREATE INDEX IF NOT EXISTS ix_content_is_featured ON content (is_featured)',
    'CREATE INDEX IF NOT EXISTS ix_subjects_class_id ON subjects (class_id)',
    'CREATE INDEX IF NOT EXISTS ix_announcements_is_published ON announcements (is_published)',
    'CREATE INDEX IF NOT EXISTS ix_announcements_published_at ON announcements (published_at)',
    'CREATE INDEX IF NOT EXISTS ix_uploaded_files_content_id ON uploaded_files (content_id)',
    'CREATE INDEX IF NOT EXISTS ix_uploaded_files_size_bytes ON uploaded_files (size_bytes)',
    'CREATE INDEX IF NOT EXISTS ix_orders_payment_reference ON orders (payment_reference)',
    'CREATE INDEX IF NOT EXISTS ix_enrollments_student_status ON enrollments (student_id, status)',
    'CREATE INDEX IF NOT EXISTS ix_learning_progress_user_completed ON learning_progress (user_id, is_completed)',
    'CREATE INDEX IF NOT EXISTS ix_notifications_user_read ON notifications (user_id, is_read)',
    'CREATE INDEX IF NOT EXISTS ix_audit_logs_action ON audit_logs (action)',
]

UNIQUE_INDEXES = [
    ('content.slug', 'CREATE UNIQUE INDEX IF NOT EXISTS ux_content_slug ON content (slug)'),
    ('subjects.slug', 'CREATE UNIQUE INDEX IF NOT EXISTS ux_subjects_slug ON subjects (slug)'),
    ('classes.slug', 'CREATE UNIQUE INDEX IF NOT EXISTS ux_classes_slug ON classes (slug)'),
    ('courses.slug', 'CREATE UNIQUE INDEX IF NOT EXISTS ux_courses_slug ON courses (slug)'),
    ('chapters.slug', 'CREATE UNIQUE INDEX IF NOT EXISTS ux_chapters_slug ON chapters (slug)'),
    ('playlists.slug', 'CREATE UNIQUE INDEX IF NOT EXISTS ux_playlists_slug ON playlists (slug)'),
    ('assignments.slug', 'CREATE UNIQUE INDEX IF NOT EXISTS ux_assignments_slug ON assignments (slug)'),
]

#: CHECK constraints that must be widened because ClassNext added states and
#: content types. Dropping a constraint is safe: it is recreated immediately.
CONSTRAINT_UPDATES = [
    (
        'content',
        'ck_content_status',
        "CHECK (status IN ('draft', 'scheduled', 'published', 'unpublished', 'archived'))",
    ),
    (
        'content',
        'ck_content_type',
        "CHECK (content_type IN ('notes', 'study_material', 'pdf_resource', "
        "'video_lesson', 'announcement', 'reference_link', 'audio', 'image', "
        "'notice', 'playlist', 'course', 'assignment'))",
    ),
]

#: Structural seed rows the master prompt expects to exist from day one.
#: Skipped entirely when the table already has rows, so admin edits survive.
INITIAL_CLASSES = (
    'Class 8',
    'Class 9',
    'Class 10',
    'Class 11',
    'Class 12',
)


def _warn(message):
    print(f'[WARN] {message}')


def _has_foreign_key(table, constraint):
    """Targeted existence check for one named foreign-key constraint."""
    try:
        result = db.session.execute(
            text(
                "SELECT 1 FROM pg_constraint c "
                "JOIN pg_class t ON t.oid = c.conrelid "
                "WHERE t.relname = :table AND c.conname = :name "
                "AND c.contype = 'f'"
            ),
            {'table': table, 'name': constraint},
        )
        return result.first() is not None
    except Exception:
        db.session.rollback()
        return False


def add_missing_columns(inspector, existing_tables):
    changes = []
    for table, columns in ADDITIVE_COLUMNS.items():
        if table not in existing_tables:
            continue
        present = {column['name'] for column in inspector.get_columns(table)}
        for column in columns:
            name = column.split()[0]
            if name in present:
                continue
            try:
                db.session.execute(text(f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column}'))
                changes.append(f'{table}.{name}')
            except Exception as error:  # pragma: no cover - depends on live schema
                db.session.rollback()
                _warn(f'Could not add {table}.{name}: {error}')
    return changes


def add_missing_foreign_keys(existing_tables):
    changes = []
    for table, constraint, column, reference in ADDITIVE_FOREIGN_KEYS:
        if table not in existing_tables:
            continue
        if _has_foreign_key(table, constraint):
            continue
        try:
            db.session.execute(
                text(f'ALTER TABLE {table} ADD CONSTRAINT {constraint} '
                     f'FOREIGN KEY ({column}) {reference}')
            )
            changes.append(f'fk {table}.{column}')
        except Exception as error:  # pragma: no cover - depends on live schema
            db.session.rollback()
            _warn(f'Could not add foreign key {constraint}: {error}')
    return changes


def _relax_statement_timeout():
    """Give DDL room on hosts that set an aggressive ``statement_timeout``.

    Managed Postgres providers such as Supabase cap each statement at a few
    seconds, which is plenty for the tiny ALTERs below but not for the catalog
    introspection queries SQLAlchemy issues. This only affects this session.
    """
    try:
        db.session.execute(text("SET statement_timeout = '60s'"))
        db.session.commit()
    except Exception as error:  # pragma: no cover - depends on host policy
        db.session.rollback()
        _warn(f'Could not relax statement_timeout: {error}')


def _has_check_constraint(table, constraint):
    """Targeted existence check.

    ``Inspector.get_check_constraints`` scans the whole catalog and times out on
    managed Postgres, so ask for exactly one constraint name instead.
    """
    try:
        result = db.session.execute(
            text(
                "SELECT 1 FROM pg_constraint c "
                "JOIN pg_class t ON t.oid = c.conrelid "
                "WHERE t.relname = :table AND c.conname = :name "
                "AND c.contype = 'c'"
            ),
            {'table': table, 'name': constraint},
        )
        return result.first() is not None
    except Exception:
        db.session.rollback()
        return False


def widen_constraints(existing_tables):
    """Replace CHECK constraints that no longer cover the new state set."""
    changes = []
    for table, constraint, definition in CONSTRAINT_UPDATES:
        if table not in existing_tables:
            continue
        if not _has_check_constraint(table, constraint):
            continue
        try:
            db.session.execute(text(f'ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint}'))
            db.session.execute(text(f'ALTER TABLE {table} ADD CONSTRAINT {constraint} {definition}'))
            changes.append(f'constraint {constraint}')
        except Exception as error:  # pragma: no cover - depends on live schema
            db.session.rollback()
            _warn(f'Could not widen {constraint}: {error}')
    return changes


def add_indexes(existing_tables):
    for statement in ADDITIVE_INDEXES:
        target = statement.split(' ON ')[1].split(' ')[0]
        if target not in existing_tables:
            continue
        try:
            db.session.execute(text(statement))
        except Exception as error:  # pragma: no cover - depends on live schema
            db.session.rollback()
            _warn(f'Index failed: {statement} ({error})')

    for _label, statement in UNIQUE_INDEXES:
        table = statement.split(' ON ')[1].split(' ')[0]
        if table not in existing_tables:
            continue
        try:
            db.session.execute(text(statement))
        except Exception as error:  # pragma: no cover - depends on live schema
            db.session.rollback()
            _warn(f'Unique index not created (duplicates?): {statement} ({error})')


def sync_schema():
    """Best-effort additive migration for pre-existing databases."""
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())

    _relax_statement_timeout()

    changes = add_missing_columns(inspector, existing_tables)
    db.session.commit()
    changes += add_missing_foreign_keys(existing_tables)
    db.session.commit()
    changes += widen_constraints(existing_tables)
    add_indexes(existing_tables)

    db.session.commit()
    return changes


def seed_initial_classes():
    """Create Class 8-12 once, so the hierarchy is usable on a fresh install."""
    if SchoolClass.query.count() > 0:
        return 0
    for order, name in enumerate(INITIAL_CLASSES, start=1):
        db.session.add(
            SchoolClass(
                name=name,
                slug=SchoolClass.generate_slug(name),
                display_order=order,
                is_enabled=True,
                status='active',
            )
        )
    db.session.commit()
    return len(INITIAL_CLASSES)


def migrate_legacy_uploads():
    """Move files out of the old public ``app/static/uploads`` folder."""
    legacy = legacy_upload_root()
    target = upload_root()
    if not os.path.isdir(legacy) or os.path.abspath(legacy) == os.path.abspath(target):
        return 0

    moved = 0
    for name in os.listdir(legacy):
        source = os.path.join(legacy, name)
        if not os.path.isfile(source):
            continue
        destination = os.path.join(target, name)
        if os.path.exists(destination):
            continue
        try:
            shutil.move(source, destination)
            moved += 1
        except OSError as error:  # pragma: no cover - depends on filesystem
            _warn(f'Could not move {name}: {error}')

    if moved:
        print(f'[OK] Moved {moved} upload(s) out of app/static/uploads into {target}')
        print('[..] Run "git rm -r app/static/uploads" once the folder is empty.')
    return moved


def main(check_only=False):
    app = create_app()
    with app.app_context():
        if check_only:
            inspector = inspect(db.engine)
            existing_tables = set(inspector.get_table_names())
            missing_tables = sorted(set(db.metadata.tables) - existing_tables)
            missing_columns = []
            for table, columns in ADDITIVE_COLUMNS.items():
                if table not in existing_tables:
                    continue
                present = {c['name'] for c in inspector.get_columns(table)}
                missing_columns += [
                    f'{table}.{c.split()[0]}'
                    for c in columns if c.split()[0] not in present
                ]
            print(f'[CHECK] Missing tables: {missing_tables or "none"}')
            print(f'[CHECK] Missing columns: {missing_columns or "none"}')
            return 0

        db.create_all()
        print(f'[OK] Tables verified: {len(db.metadata.tables)} total')

        changes = sync_schema()
        if changes:
            print(f'[OK] Applied {len(changes)} schema change(s): {", ".join(changes)}')
        else:
            print('[OK] Schema already up to date')

        seeded = seed_initial_classes()
        if seeded:
            print(f'[OK] Seeded {seeded} classes: {", ".join(INITIAL_CLASSES)}')

        migrate_legacy_uploads()

        counts = {}
        for model in (User, SchoolClass, Subject, Chapter, Content, Course,
                      Enrollment, Order, Announcement, UploadedFile, Faq):
            try:
                counts[model.__tablename__] = db.session.query(model).count()
            except Exception:  # pragma: no cover - depends on live schema
                counts[model.__tablename__] = 'n/a'
        print('[OK] Current rows: ' + ', '.join(f'{k}={v}' for k, v in counts.items()))
        print("\nNext: run 'python create_teacher.py' to create the first teacher account.")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(check_only='--check' in sys.argv))
    except RuntimeError as error:
        print(f'[ERROR] {error}')
        sys.exit(1)