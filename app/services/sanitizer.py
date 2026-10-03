import bleach

# Tags a teacher may use inside authored lesson content.
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's', 'a', 'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'pre', 'code',
    'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'hr', 'span', 'div',
    'sub', 'sup', 'mark', 'figure', 'figcaption',
]

# Attributes per tag. Inline `style` is intentionally not allowed: authored
# content should express presentation through the design system's classes.
ALLOWED_ATTRS = {
    '*': ['class', 'id'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height', 'loading'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan', 'scope'],
    'ol': ['start'],
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto', 'tel']


def sanitize_html(html_content):
    """Allowlist-sanitize user-authored HTML before it is stored."""
    if not html_content:
        return ''
    return bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
        strip_comments=True,
    )


def strip_html(html_content):
    """Return readable plain text from authored HTML (used for previews)."""
    if not html_content:
        return ''
    return bleach.clean(html_content, tags=[], attributes={}, strip=True)