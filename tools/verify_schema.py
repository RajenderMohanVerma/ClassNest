"""Verify the live schema after the ClassNext additive migration."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text  # noqa: E402

from app import create_app, db  # noqa: E402
from app.models import Chapter, Content, SchoolClass, Subject, User  # noqa: E402


def main():
    app = create_app()
    with app.app_context():
        print('ORM users   :', db.session.query(User).count())
        print('ORM subjects:', db.session.query(Subject).count())
        print('ORM content :', db.session.query(Content).count())
        print('ORM classes :', db.session.query(SchoolClass).count())

        sample = Content.query.first()
        print('sample content:', sample.title)
        print('  status      :', sample.status)
        print('  access_level:', sample.access_level)
        print('  public?     :', sample.is_publicly_visible)

        print('classes:', [row.name for row in
                          SchoolClass.query.order_by(SchoolClass.display_order)])

        # Every ClassNext content state must now satisfy the widened CHECK.
        for state in ('draft', 'scheduled', 'published', 'unpublished', 'archived'):
            db.session.execute(
                text('UPDATE content SET status = :s WHERE id = :i'),
                {'s': state, 'i': sample.id},
            )
        db.session.rollback()
        print('all 5 content states accepted by the DB: OK')

        # Existing rows kept their public visibility after the default backfill.
        rows = db.session.execute(
            text("SELECT access_level, count(*) FROM content GROUP BY access_level")
        ).fetchall()
        print('content access_level:', rows)

        # Chapters table is wired to subjects.
        print('chapters table:', Chapter.__tablename__,
              '| columns:', len(Chapter.__table__.columns))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())