"""Generate the ClassNest app icons and favicons.

The artwork is drawn from code so the whole icon set stays visually identical
and can be regenerated at any time:

    pip install Pillow
    python tools/generate_icons.py

Design: purple-blue diagonal gradient background, white graduation cap resting
on a white open book, orange tassel bead as the single accent colour.

Outputs (all under app/static):
    icons/icon-512.png            512x512  install icon (purpose "any")
    icons/icon-192.png            192x192  install icon (purpose "any")
    icons/icon-512-maskable.png   512x512  maskable icon (safe-zone padding)
    icons/apple-touch-icon.png    180x180  iOS home screen (opaque)
    icons/favicon-32x32.png        32x32   browser tab
    icons/favicon-16x16.png        16x16   browser tab
    favicon.ico                   16/32/48 multi-resolution favicon
"""

import os

from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(BASE_DIR, 'app', 'static', 'icons')
STATIC_DIR = os.path.join(BASE_DIR, 'app', 'static')

GRADIENT_START = (122, 59, 240)   # #7A3BF0 purple
GRADIENT_END = (62, 99, 232)     # #3E63E8 blue
ACCENT = (245, 158, 11)          # #F59E0B orange
LOGO = (255, 255, 255)           # white logo
PAGE_LINE = (226, 222, 255)      # subtle page detail lines

SUPERSAMPLE = 4

# Maskable icons must survive a circular crop: keep the logo inside ~62%.
LOGO_SCALE_ANY = 0.86
LOGO_SCALE_MASKABLE = 0.60


def _gradient(size):
    """Diagonal purple-blue gradient (top-left to bottom-right)."""
    rows = []
    for y in range(size):
        row = Image.new('RGB', (size, 1))
        draw = ImageDraw.Draw(row)
        for x in range(size):
            ratio = (x + y) / (2 * (size - 1))
            draw.point(
                (x, 0),
                fill=(
                    round(GRADIENT_START[0] + (GRADIENT_END[0] - GRADIENT_START[0]) * ratio),
                    round(GRADIENT_START[1] + (GRADIENT_END[1] - GRADIENT_START[1]) * ratio),
                    round(GRADIENT_START[2] + (GRADIENT_END[2] - GRADIENT_START[2]) * ratio),
                ),
            )
        rows.append(row)
    image = Image.new('RGB', (size, size))
    for y, row in enumerate(rows):
        image.paste(row, (0, y))
    return image


def _draw_logo(image, logo_scale):
    """Draw the graduation cap + open book centred on ``image``."""
    draw = ImageDraw.Draw(image)
    canvas = image.size[0]
    box = canvas * logo_scale
    left = (canvas - box) / 2

    def point(x, y):
        return (left + x * box, left + y * box)

    def polygon(points, fill):
        draw.polygon([point(x, y) for x, y in points], fill=fill)

    def line(points, fill, width_ratio):
        draw.line(
            [point(x, y) for x, y in points],
            fill=fill,
            width=max(1, round(width_ratio * box)),
            joint='curve',
        )

    # Open book pages (centre gap shows the gradient, reading as the spine).
    left_page = [(0.145, 0.600), (0.482, 0.652), (0.482, 0.858), (0.145, 0.802)]
    right_page = [(0.518, 0.652), (0.855, 0.600), (0.855, 0.802), (0.518, 0.858)]
    polygon(left_page, LOGO)
    polygon(right_page, LOGO)

    # Subtle text lines on each page.
    for page_x in (0.482, 0.518):
        direction = -1 if page_x > 0.5 else 1
        for step in range(2):
            top = 0.706 + step * 0.052
            line(
                [
                    (page_x - 0.026 * direction, top),
                    (page_x + direction * 0.22, top - 0.036),
                ],
                PAGE_LINE,
                0.014,
            )

    # Cap band sits behind the mortarboard.
    draw.rounded_rectangle(
        [*point(0.300, 0.442), *point(0.700, 0.556)],
        radius=0.035 * box,
        fill=LOGO,
    )

    # Mortarboard diamond.
    polygon(
        [(0.500, 0.240), (0.876, 0.404), (0.500, 0.568), (0.124, 0.404)],
        LOGO,
    )

    # Tassel with the orange bead accent.
    line([(0.876, 0.404), (0.876, 0.618)], LOGO, 0.020)
    bead_x, bead_y = point(0.876, 0.652)
    radius = 0.046 * box
    draw.ellipse(
        [bead_x - radius, bead_y - radius, bead_x + radius, bead_y + radius],
        fill=ACCENT,
    )


def render(size, maskable=False, opaque=False):
    canvas = size * SUPERSAMPLE
    image = _gradient(canvas)
    _draw_logo(image, LOGO_SCALE_MASKABLE if maskable else LOGO_SCALE_ANY)
    image = image.resize((size, size), Image.LANCZOS)
    return image.convert('RGB') if opaque else image


def write_png(image, name):
    path = os.path.join(ICON_DIR, name)
    image.save(path, 'PNG', optimize=True)
    print(f'  {name:28} {image.size[0]}x{image.size[1]}  {os.path.getsize(path):,} bytes')


def main():
    os.makedirs(ICON_DIR, exist_ok=True)

    print('App icons')
    write_png(render(512), 'icon-512.png')
    write_png(render(192), 'icon-192.png')
    write_png(render(512, maskable=True), 'icon-512-maskable.png')
    write_png(render(180, opaque=True), 'apple-touch-icon.png')

    print('Favicons')
    write_png(render(32), 'favicon-32x32.png')
    write_png(render(16), 'favicon-16x16.png')

    ico_path = os.path.join(STATIC_DIR, 'favicon.ico')
    render(48).save(ico_path, 'ICO', sizes=[(16, 16), (32, 32), (48, 48)])
    print(f'  {"favicon.ico":28} 16/32/48        {os.path.getsize(ico_path):,} bytes')

    print('\nDone. Icons written to app/static/icons and app/static/favicon.ico')


if __name__ == '__main__':
    main()