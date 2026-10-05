"""Read-only smoke test of the live site (no writes, no seeding).

Runs against the configured database with the real config, hitting the public
pages exactly as a visitor would.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db  # noqa: E402
from app.models import Chapter, Content, Course, SchoolClass, Subject  # noqa: E402

PATHS = [
    '/', '/classes', '/notes', '/videos', '/free-resources', '/courses',
    '/premium', '/notices', '/about', '/faq', '/contact',
    '/legal/privacy', '/legal/terms', '/legal/refund-policy',
    '/search?q=math', '/sitemap.xml', '/robots.txt', '/healthz',
]


def main():
    app = create_app()
    failures = []

    with app.app_context():
        print('live rows: classes=%s subjects=%s content=%s courses=%s chapters=%s' % (
            SchoolClass.query.count(), Subject.query.count(),
            Content.query.count(), Course.query.count(), Chapter.query.count(),
        ))

        detail_paths = []
        row = SchoolClass.query.filter_by(is_enabled=True).first()
        if row:
            detail_paths.append(f'/classes/{row.slug}')
        row = Subject.query.first()
        if row:
            detail_paths.append(f'/subjects/{row.slug}')
        row = Chapter.query.first()
        if row:
            detail_paths.append(f'/chapters/{row.slug}')
        row = Content.query.filter_by(status='published').first()
        if row:
            detail_paths.append(f'/content/{row.slug}')

        client = app.test_client()
        for path in PATHS + detail_paths:
            response = client.get(path)
            status = response.status_code
            if status >= 400:
                failures.append((path, status))
            print(f'  {"OK " if status < 400 else "BAD"} {status} {path}')

    print()
    if failures:
        print('FAILURES:', failures)
        return 1
    print('Live public site responded cleanly.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())