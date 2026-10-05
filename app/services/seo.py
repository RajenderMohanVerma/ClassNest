"""SEO helpers: canonical URLs, Open Graph tags, sitemap and robots.

All URLs are absolute because search engines index the deployed origin, not the
local development host. ``SITE_URL`` is used when set and falls back to the
current request root.
"""

from flask import current_app, request, url_for

from app.models import CONTENT_STATUS_PUBLISHED, Chapter, Content, Course, SchoolClass, Subject


def site_base():
    configured = (current_app.config.get('SITE_URL') or '').rstrip('/')
    if configured:
        return configured
    try:
        return request.url_root.rstrip('/')
    except RuntimeError:
        return ''


def absolute_url(path=''):
    """Turn a root-relative path into an absolute URL."""
    if not path:
        return site_base() + '/'
    if path.startswith('http://') or path.startswith('https://'):
        return path
    base = site_base()
    if path.startswith('/'):
        return f'{base}{path}'
    return f'{base}/{path}'


def build_meta(title=None, description=None, path=None, og_type='website',
               image=None, noindex=False):
    """Return the values a template needs for ``<head>``.

    The site name is appended to the title unless the caller already included
    it, so pages never render a bare or duplicated brand.
    """
    app_name = current_app.config['APP_NAME']
    full_title = title if title and app_name in title else f'{title} | {app_name}' if title else app_name

    raw_description = description or current_app.config.get('APP_DESCRIPTION') or ''
    full_description = ' '.join(str(raw_description).split())[:300]

    canonical = absolute_url(path or request.path)

    resolved_image = image
    if resolved_image:
        resolved_image = absolute_url(resolved_image)
    else:
        resolved_image = absolute_url(url_for('static', filename='icons/logo.svg'))

    return {
        'title': full_title,
        'description': full_description,
        'canonical': canonical,
        'og_title': full_title,
        'og_description': full_description,
        'og_type': og_type,
        'og_image': resolved_image,
        'og_url': canonical,
        'site_name': app_name,
        'noindex': noindex,
    }


def iter_public_urls(limit_per_type=2000):
    """Yield ``(path, lastmod, changefreq, priority)`` for the sitemap.

    Only published, non-archived records are emitted: a draft slug in
    ``sitemap.xml`` would advertise content that returns 403 or 404.
    """
    yield ('/', None, 'daily', '1.0')
    for path in (
        '/classes', '/notes', '/videos', '/courses', '/premium',
        '/notices', '/about', '/contact', '/faq', '/privacy', '/terms',
    ):
        yield (path, None, 'weekly', '0.7')

    for row in SchoolClass.query.filter(
        SchoolClass.is_enabled.is_(True),
        SchoolClass.status == 'active',
    ).order_by(SchoolClass.display_order).limit(limit_per_type):
        yield (f'/classes/{row.slug}', row.updated_at, 'weekly', '0.8')

    for row in Subject.query.filter(
        Subject.is_enabled.is_(True),
        Subject.status == CONTENT_STATUS_PUBLISHED,
    ).order_by(Subject.id).limit(limit_per_type):
        yield (f'/subjects/{row.slug}', row.updated_at, 'weekly', '0.7')

    for row in Chapter.query.filter(
        Chapter.status == CONTENT_STATUS_PUBLISHED,
    ).order_by(Chapter.id).limit(limit_per_type):
        yield (f'/chapters/{row.slug}', row.updated_at, 'weekly', '0.6')

    for row in Content.query.filter(
        Content.status == CONTENT_STATUS_PUBLISHED,
        Content.access_level == 'public',
    ).order_by(Content.published_at.desc().nullslast()).limit(limit_per_type):
        yield (f'/content/{row.slug}', row.updated_at, 'weekly', '0.6')

    for row in Course.query.filter(
        Course.status == CONTENT_STATUS_PUBLISHED,
    ).order_by(Course.published_at.desc().nullslast()).limit(limit_per_type):
        yield (f'/courses/{row.slug}', row.updated_at, 'weekly', '0.7')


def xml_escape(value):
    """Escape a value for inclusion in sitemap XML."""
    if value is None:
        return ''
    return (
        str(value)
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&apos;')
    )