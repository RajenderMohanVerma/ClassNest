"""PWA asset, manifest and head-tag tests.

These verify the install experience: every declared icon must exist at the exact
declared size, the manifest must be valid JSON with the right MIME type, and
every page must advertise the icons, favicons and theme colour.
"""

import json
import os
import struct
import xml.etree.ElementTree as ET

import pytest

from app import db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_NS = '{http://www.w3.org/2000/svg}'

EXPECTED_ICONS = {
    '/static/icons/favicon-16x16.png': (16, 16),
    '/static/icons/favicon-32x32.png': (32, 32),
    '/static/icons/apple-touch-icon.png': (180, 180),
    '/static/icons/icon-192.png': (192, 192),
    '/static/icons/icon-512.png': (512, 512),
    '/static/icons/icon-512-maskable.png': (512, 512),
}

REQUIRED_MANIFEST_KEYS = ('id', 'name', 'short_name', 'start_url', 'scope',
                          'display', 'theme_color', 'background_color', 'icons')


def repo_path(url_path):
    """Map a served URL (``/static/...``) to its file on disk (``app/static/...``)."""
    relative = url_path.lstrip('/')
    if relative.startswith('static/'):
        relative = os.path.join('app', relative)
    return os.path.join(BASE_DIR, relative.replace('/', os.sep))


def png_dimensions(url_path):
    """Read width/height straight from the PNG header (no Pillow needed)."""
    with open(repo_path(url_path), 'rb') as handle:
        header = handle.read(24)
    assert header[:8] == b'\x89PNG\r\n\x1a\n', f'{url_path} is not a PNG'
    return struct.unpack('>II', header[16:24])


@pytest.mark.parametrize('icon_path,dimensions', sorted(EXPECTED_ICONS.items()))
def test_icon_files_exist_with_exact_dimensions(icon_path, dimensions):
    assert png_dimensions(icon_path) == dimensions


def test_favicon_ico_exists_and_is_not_empty():
    path = os.path.join(BASE_DIR, 'app', 'static', 'favicon.ico')
    assert os.path.isfile(path)
    with open(path, 'rb') as handle:
        assert handle.read(4) == b'\x00\x00\x01\x00', 'not a valid .ico file'
    assert os.path.getsize(path) > 500


def test_favicon_is_reachable_at_the_root(client):
    """Browsers request /favicon.ico without going through /static."""
    root = client.get('/favicon.ico')
    static = client.get('/static/favicon.ico')
    assert root.status_code == 200
    assert root.mimetype == static.mimetype == 'image/x-icon'
    assert root.data == static.data


def test_manifest_file_declares_every_icon(client):
    response = client.get('/manifest.webmanifest')
    assert response.status_code == 200
    assert response.mimetype == 'application/manifest+json'

    manifest = json.loads(response.get_data(as_text=True))
    for key in REQUIRED_MANIFEST_KEYS:
        assert key in manifest, f'manifest is missing "{key}"'

    assert manifest['display'] == 'standalone'
    assert manifest['start_url'] == '/'
    assert manifest['scope'] == '/'

    declared = {icon['src']: icon for icon in manifest['icons']}
    for icon_path in EXPECTED_ICONS:
        assert icon_path in declared, f'{icon_path} is not declared in the manifest'

    maskable = [i for i in manifest['icons'] if i.get('purpose') == 'maskable']
    assert maskable, 'a maskable icon is required for Android adaptive icons'

    for icon in manifest['icons']:
        assert icon['src'].startswith('/'), 'icon src must be an absolute path'
        response = client.get(icon['src'])
        assert response.status_code == 200, icon['src']
        if icon['type'] == 'image/svg+xml':
            # Scalable icons declare "any"; verify the payload parses instead.
            ET.fromstring(response.data)
            continue
        assert png_dimensions(icon['src']) == tuple(
            int(part) for part in icon['sizes'].lower().split('x')
        ), icon['src']


def test_legacy_manifest_path_still_works(client):
    response = client.get('/manifest.json')
    assert response.status_code == 200
    assert response.mimetype == 'application/manifest+json'
    assert json.loads(response.get_data(as_text=True))['short_name'] == 'ClassNext'


def test_service_worker_is_served_with_install_headers(client):
    response = client.get('/sw.js')
    assert response.status_code == 200
    assert response.headers['Service-Worker-Allowed'] == '/'
    assert 'no-cache' in response.headers['Cache-Control']
    assert response.headers['Content-Type'].startswith('application/javascript')


@pytest.mark.parametrize('icon_path', sorted(EXPECTED_ICONS))
def test_every_icon_is_downloadable(client, icon_path):
    response = client.get(icon_path)
    assert response.status_code == 200
    assert response.mimetype == 'image/png'
    assert response.data.startswith(b'\x89PNG\r\n\x1a\n')


def test_logo_svg_exists_and_is_served(client):
    path = os.path.join(BASE_DIR, 'app', 'static', 'icons', 'logo.svg')
    assert os.path.isfile(path)

    response = client.get('/static/icons/logo.svg')
    assert response.status_code == 200
    assert response.mimetype in ('image/svg+xml', 'text/xml')


def test_logo_svg_is_valid_and_matches_the_brand_palette():
    """The SVG is the single source of truth for the mark, so validate it."""
    path = os.path.join(BASE_DIR, 'app', 'static', 'icons', 'logo.svg')
    root = ET.parse(path).getroot()

    assert root.tag == f'{SVG_NS}svg'
    assert root.get('viewBox') == '0 0 512 512'

    stops = [s.get('stop-color').lower() for s in root.iter(f'{SVG_NS}stop')]
    assert stops == ['#7a3bf0', '#3e63e8'], 'purple-blue gradient changed'

    gradient = root.find(f'.//{SVG_NS}linearGradient')
    assert gradient.get('x1') == '0' and gradient.get('y1') == '0'
    assert gradient.get('x2') == '1' and gradient.get('y2') == '1'

    accent = next(root.iter(f'{SVG_NS}circle'))
    assert accent.get('fill').lower() == '#f59e0b', 'orange accent is missing'

    # three white shapes: two book pages and the cap board
    assert len(list(root.iter(f'{SVG_NS}polygon'))) == 3
    assert len(list(root.iter(f'{SVG_NS}rect'))) == 2  # background + cap band


def test_svg_page_lines_stay_inside_their_own_page():
    """Regression: page rules used to bleed across the spine onto the other page."""
    path = os.path.join(BASE_DIR, 'app', 'static', 'icons', 'logo.svg')
    root = ET.parse(path).getroot()
    left_edge, right_edge = 0.482, 0.518

    for line in root.iter(f'{SVG_NS}line'):
        xs = (float(line.get('x1')), float(line.get('x2')))
        in_left = all(x <= left_edge + 1e-6 for x in xs)
        in_right = all(x >= right_edge - 1e-6 for x in xs)
        # the tassel hangs at x=0.876, outside both pages, which is expected
        assert in_left or in_right or min(xs) > 0.86, f'line crosses the spine: {xs}'


def test_logo_is_used_across_the_site(client, app):
    """One mark everywhere: sidebars, auth pages and the offline page."""
    with app.app_context():
        db.create_all()

    for path in ('/auth/login', '/auth/register', '/offline'):
        body = client.get(path).get_data(as_text=True)
        assert 'logo.svg' in body, f'{path} does not use the SVG logo'


def test_head_tags_are_present_on_every_page(client, app):
    """base.html drives every page, so one render checks the whole site."""
    with app.app_context():
        db.create_all()

    response = client.get('/auth/login')
    assert response.status_code == 200
    body = response.get_data(as_text=True)

    assert '<link rel="manifest" href="/manifest.webmanifest">' in body
    assert 'icons/favicon-16x16.png' in body
    assert 'icons/favicon-32x32.png' in body
    assert 'favicon.ico' in body
    assert 'icons/apple-touch-icon.png' in body
    assert 'icons/icon-192.png' in body
    assert '<meta name="mobile-web-app-capable" content="yes">' in body
    assert '<meta name="apple-mobile-web-app-capable" content="yes">' in body
    assert '<meta name="apple-mobile-web-app-title" content="ClassNext">' in body
    assert '<meta name="apple-mobile-web-app-status-bar-style" content="default">' in body
    assert '<meta name="theme-color" content="#4f35e8">' in body
    assert 'Classes, notes, videos and courses by Er. Amit Sir.' in body


def test_offline_page_carries_the_same_icons(client):
    body = client.get('/offline').get_data(as_text=True)
    assert 'icons/apple-touch-icon.png' in body
    assert 'apple-mobile-web-app-title' in body


def test_login_and_register_show_the_app_icon(client):
    for path in ('/auth/login', '/auth/register'):
        body = client.get(path).get_data(as_text=True)
        assert 'icons/icon-192.png' in body, path
        assert 'cn-auth__logo-icon' in body, path


def test_install_prompt_script_is_loaded(client):
    body = client.get('/auth/login').get_data(as_text=True)
    assert '/static/js/install-prompt.js' in body


def test_theme_color_matches_the_manifest(client):
    manifest = json.loads(client.get('/manifest.webmanifest').get_data(as_text=True))
    body = client.get('/auth/login').get_data(as_text=True)
    assert f'<meta name="theme-color" content="{manifest["theme_color"]}">' in body


def test_generated_icons_are_not_blank():
    """Guard against a transparent or single-colour icon being committed."""
    path = os.path.join(BASE_DIR, 'app', 'static', 'icons', 'icon-512.png')
    with open(path, 'rb') as handle:
        data = handle.read()
    # PNG IDAT payload must be large enough to hold a real gradient plus logo.
    assert len(data) > 5000, 'icon-512.png looks empty or unrendered'