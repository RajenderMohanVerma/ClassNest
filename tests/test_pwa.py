"""PWA asset, manifest and head-tag tests.

These verify the install experience: every declared icon must exist at the exact
declared size, the manifest must be valid JSON with the right MIME type, and
every page must advertise the icons, favicons and theme colour.
"""

import json
import os
import struct

import pytest

from app import db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
        assert png_dimensions(icon['src']) == tuple(
            int(part) for part in icon['sizes'].lower().split('x')
        ), icon['src']


def test_legacy_manifest_path_still_works(client):
    response = client.get('/manifest.json')
    assert response.status_code == 200
    assert response.mimetype == 'application/manifest+json'
    assert json.loads(response.get_data(as_text=True))['short_name'] == 'ClassNest'


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
    assert '<meta name="apple-mobile-web-app-title" content="ClassNest">' in body
    assert '<meta name="apple-mobile-web-app-status-bar-style" content="default">' in body
    assert '<meta name="theme-color" content="#4f35e8">' in body
    assert 'ClassNest - Your Smart Learning Companion' in body


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