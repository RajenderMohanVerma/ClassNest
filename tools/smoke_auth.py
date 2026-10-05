"""Read-only smoke test of the authentication pages against the live config.

Renders the public auth forms and checks they never contain a raw token or a
hash. Nothing is submitted, so no account or token is created.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402

PATHS = {
    '/auth/login': ('password',),
    '/auth/register': ('password', 'confirm_password', 'class_id'),
    '/auth/forgot-password': ('email',),
    '/auth/reset-password/deadbeef': ('password', 'confirm_password'),
}
# An unknown reset token must bounce to the request form, not render a page.
EXPECTED_REDIRECTS = {'/auth/reset-password/deadbeef'}


def main():
    app = create_app()
    failures = []
    client = app.test_client()

    for path, fields in PATHS.items():
        response = client.get(path)
        status = response.status_code
        print(f'  {"OK " if status < 400 else "BAD"} {status} {path}')

        if status >= 400:
            failures.append((path, status))
            continue

        if path in EXPECTED_REDIRECTS:
            if status != 302 or '/auth/forgot-password' not in response.headers['Location']:
                failures.append((path, 'an invalid token should redirect to /auth/forgot-password'))
            continue

        body = response.data
        if b'csrf_token' not in body:
            failures.append((path, 'missing CSRF token'))
        for field in fields:
            if f'name="{field}"'.encode() not in body:
                failures.append((path, f'missing {field} field'))
        # A raw token must never be rendered into a page.
        if re.search(rb'[0-9a-f]{64}', body):
            failures.append((path, 'looks like a token hash leaked into the page'))

    print()
    if failures:
        print('FAILURES:', failures)
        return 1
    print('Auth pages rendered cleanly.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())