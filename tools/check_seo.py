"""Verify SITE_URL produces absolute canonical URLs and sitemap entries."""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('SITE_URL', 'https://class-name-byamit.getvoroa.com/auth/login')

from app import create_app  # noqa: E402


def main():
    app = create_app()
    print('SITE_URL =', app.config['SITE_URL'])

    client = app.test_client()
    body = client.get('/sitemap.xml').data.decode()
    locs = re.findall(r'<loc>(.*?)</loc>', body)[:4]
    for loc in locs:
        print(' ', loc)

    home = client.get('/').data.decode()
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', home)
    og_url = re.search(r'property="og:url" content="([^"]+)"', home)
    print('canonical:', canonical.group(1) if canonical else 'MISSING')
    print('og:url   :', og_url.group(1) if og_url else 'MISSING')

    ok = all(
        loc.startswith('https://class-name-byamit.getvoroa.com/auth/login') for loc in locs
    ) and canonical and canonical.group(1).startswith('https://class-name-byamit.getvoroa.com/auth/login')
    print()
    print('OK' if ok else 'BAD: canonical URLs are not absolute')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())