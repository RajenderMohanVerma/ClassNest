import re

import bleach

# Elements whose *content* must be discarded, not just their tags.
UNSAFE_BLOCKS = re.compile(
    r'<\s*(script|style|iframe|object|embed|form)\b[^>]*>.*?<\s*/\s*\1\s*>',
    re.IGNORECASE | re.DOTALL,
)
UNOPENED_BLOCKS = re.compile(
    r'<\s*(script|style|iframe|object|embed|form)\b[^>]*>.*',
    re.IGNORECASE | re.DOTALL,
)

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
    text = UNSAFE_BLOCKS.sub('', html_content)
    text = UNOPENED_BLOCKS.sub('', text)
    return bleach.clean(
        text,
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


def plain_text(value, max_length=None):
    """Normalise untrusted form input to a single-line, length-capped string.

    Tags are stripped, control characters are removed and runs of whitespace
    collapse, so a contact-form submission cannot inject markup or smuggle a
    multi-line value into a single-line column.
    """
    if value is None:
        text = ''
    elif not isinstance(value, str):
        text = str(value)
    else:
        text = value
    text = strip_html(text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if max_length is not None:
        text = text[:max_length].rstrip()
    return text