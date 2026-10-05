"""Snapshot live row counts before/after the ClassNext additive migration.

Run with:  python tools/snapshot_counts.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app import create_app, db

TABLES = ('users', 'subjects', 'content', 'announcements', 'uploaded_files')


def main():
    app = create_app()
    with app.app_context():
        for table in TABLES:
            count = db.session.execute(
                text('SELECT count(*) FROM ' + table)
            ).scalar()
            print(f'{table}={count}')
        print('content_status=' + repr(
            db.session.execute(
                text('SELECT status, count(*) FROM content GROUP BY status')
            ).fetchall()
        ))
        print('users_by_role=' + repr(
            db.session.execute(
                text('SELECT role, count(*) FROM users GROUP BY role')
            ).fetchall()
        ))
    return 0


if __name__ == '__main__':
    sys.exit(main())