"""Initialize the ClassNest PostgreSQL schema.

`db.create_all()` only creates tables that do not exist yet, so this script also
runs a small additive sync (new columns / indexes / unique slugs) for databases
created by an earlier version, and moves uploads out of the old public
``app/static/uploads`` folder. It never drops or rewrites existing content.

Usage:
    python init_db.py
"""

import os
import shutil
import sys

from sqlalchemy import inspect, text

from app import create_app, db
from app.models.announcement import Announcement  # noqa: F401  (register tables)
from app.models.content import Content  # noqa: F401
from app.models.subject import Subject  # noqa: F401
from app.models.uploaded_file import UploadedFile  # noqa: F401
from app.models.user import User  # noqa: F401
from app.services.uploads import legacy_upload_root, upload_root

# Columns added after the first release, applied to existing installations.
ADDITIVE_COLUMNS = {
    'users': [
        "avatar VARCHAR(255)",
    ],
    'subjects': [],
    'content': [
        'published_at TIMESTAMPTZ',
    ],
    'announcements': [],
    'uploaded_files': [],
}

ADDITIVE_INDEXES = [
    'CREATE INDEX IF NOT EXISTS ix_content_topic ON content (topic)',
    'CREATE INDEX IF NOT EXISTS ix_content_published_at ON content (published_at)',
    'CREATE INDEX IF NOT EXISTS ix_announcements_is_published ON announcements (is_published)',
    'CREATE INDEX IF NOT EXISTS ix_announcements_published_at ON announcements (published_at)',
    'CREATE INDEX IF NOT EXISTS ix_uploaded_files_content_id ON uploaded_files (content_id)',
    'CREATE INDEX IF NOT EXISTS ix_uploaded_files_size_bytes ON uploaded_files (size_bytes)',
]

UNIQUE_INDEXES = [
    ('content.slug', 'CREATE UNIQUE INDEX IF NOT EXISTS ux_content_slug ON content (slug)'),
    ('subjects.slug', 'CREATE UNIQUE INDEX IF NOT EXISTS ux_subjects_slug ON subjects (slug)'),
]


def sync_schema():
    """Best-effort additive migration for pre-existing databases."""
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())
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
                print(f'[WARN] Could not add {table}.{name}: {error}')

    for statement in ADDITIVE_INDEXES:
        target = statement.split(' ON ')[1].split(' ')[0]
        if target not in existing_tables:
            continue
        try:
            db.session.execute(text(statement))
        except Exception as error:  # pragma: no cover - depends on live schema
            db.session.rollback()
            print(f'[WARN] Index failed: {statement} ({error})')

    for label, statement in UNIQUE_INDEXES:
        table = statement.split(' ON ')[1].split(' ')[0]
        if table not in existing_tables:
            continue
        try:
            db.session.execute(text(statement))
            changes.append(f'unique index {label}')
        except Exception as error:  # pragma: no cover - depends on live schema
            db.session.rollback()
            print(f'[WARN] Unique index {label} not created (duplicates?): {error}')

    db.session.commit()
    return changes


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
            print(f'[WARN] Could not move {name}: {error}')

    if moved:
        print(f'[OK] Moved {moved} upload(s) out of app/static/uploads into {target}')
        print('[..] Run "git rm -r app/static/uploads" once the folder is empty.')
    return moved


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        print('[OK] Tables verified: User, Subject, Content, Announcement, UploadedFile')

        changes = sync_schema()
        if changes:
            print(f'[OK] Added missing schema items: {", ".join(changes)}')
        else:
            print('[OK] Schema already up to date')

        migrate_legacy_uploads()

        counts = {
            'users': db.session.query(User).count(),
            'subjects': db.session.query(Subject).count(),
            'content': db.session.query(Content).count(),
            'announcements': db.session.query(Announcement).count(),
            'uploaded_files': db.session.query(UploadedFile).count(),
        }
        print('[OK] Current rows: ' + ', '.join(f'{table}={count}' for table, count in counts.items()))
        print("\nNext: run 'python create_teacher.py' to create the first teacher account.")


if __name__ == '__main__':
    try:
        main()
    except RuntimeError as error:
        print(f'[ERROR] {error}')
        sys.exit(1)