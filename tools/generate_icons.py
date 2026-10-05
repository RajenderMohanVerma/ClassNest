"""Generate the ClassNext logo, app icons and favicons.

One geometry definition drives every asset, so the SVG used on the website and
the PNGs used by the browser, Android and iOS can never drift apart.

    pip install Pillow
    python tools/generate_icons.py

Design: purple-blue diagonal gradient background, a white graduation cap resting
on a white open book, and a single orange tassel bead as the accent.

Geometry is written in a 0..1 "logo box"; both renderers place that box inside
the canvas so the mark scales identically at every size.

Outputs:
    app/static/icons/logo.svg              scalable logo (website + SVG favicon)
    app/static/icons/icon-512.png          512x512 install icon (purpose "any")
    app/static/icons/icon-192.png          192x192 install icon (purpose "any")
    app/static/icons/icon-512-maskable.png 512x512 maskable icon (safe zone)
    app/static/icons/apple-touch-icon.png  180x180 iOS icon (opaque, no alpha)
    app/static/icons/favicon-32x32.png      32x32  browser tab
    app/static/icons/favicon-16x16.png      16x16  browser tab
    app/static/favicon.ico                 16/32/48 multi-resolution favicon
"""

import os

from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(BASE_DIR, 'app', 'static', 'icons')
STATIC_DIR = os.path.join(BASE_DIR, 'app', 'static')

GRADIENT_START = '#7A3BF0'   # purple
GRADIENT_END = '#3E63E8'     # blue
ACCENT = '#F59E0B'           # orange
LOGO = '#FFFFFF'             # white logo
PAGE_LINE = '#E2DEFF'        # subtle page detail lines

SUPERSAMPLE = 4

# Maskable icons must survive a circular crop, so the mark is kept smaller.
LOGO_SCALE_ANY = 0.86
LOGO_SCALE_MASKABLE = 0.60

# ── Geometry (unit coordinates inside the logo box) ─────────────────────────
LEFT_PAGE = [(0.145, 0.600), (0.482, 0.652), (0.482, 0.858), (0.145, 0.802)]
RIGHT_PAGE = [(0.518, 0.652), (0.855, 0.600), (0.855, 0.802), (0.518, 0.858)]

# Two ruled lines per page. Each stays inside its own page and tilts up toward
# the spine, so nothing bleeds across the gutter.
PAGE_LINES = tuple(
    [(0.195, top), (0.442, top - 0.036)] for top in (0.706, 0.758)
) + tuple(
    [(0.805, top), (0.558, top - 0.036)] for top in (0.706, 0.758)
)

BAND = (0.300, 0.442, 0.700, 0.556)   # x0, y0, x1, y1
BAND_RADIUS = 0.035
BOARD = [(0.500, 0.240), (0.876, 0.404), (0.500, 0.568), (0.124, 0.404)]
TASSEL = (0.876, 0.404, 0.876, 0.618)
TASSEL_WIDTH = 0.020
BEAD = (0.876, 0.652, 0.046)          # cx, cy, r


def _gradient(size):
    """Diagonal purple-blue gradient (top-left to bottom-right)."""
    start = tuple(int(GRADIENT_START[i:i + 2], 16) for i in (1, 3, 5))
    end = tuple(int(GRADIENT_END[i:i + 2], 16) for i in (1, 3, 5))
    rows = []
    for y in range(size):
        row = Image.new('RGB', (size, 1))
        draw = ImageDraw.Draw(row)
        for x in range(size):
            ratio = (x + y) / (2 * (size - 1))
            draw.point((x, 0), fill=tuple(
                round(start[channel] + (end[channel] - start[channel]) * ratio)
                for channel in range(3)
            ))
        rows.append(row)
    image = Image.new('RGB', (size, size))
    for y, row in enumerate(rows):
        image.paste(row, (0, y))
    return image


def _draw_logo(image, logo_scale):
    """Draw the mark centred on ``image`` using Pillow."""
    draw = ImageDraw.Draw(image)
    canvas = image.size[0]
    box = canvas * logo_scale
    left = (canvas - box) / 2

    def point(x, y):
        return (left + x * box, left + y * box)

    draw.polygon([point(x, y) for x, y in LEFT_PAGE], fill=LOGO)
    draw.polygon([point(x, y) for x, y in RIGHT_PAGE], fill=LOGO)

    for (x1, y1), (x2, y2) in PAGE_LINES:
        draw.line([point(x1, y1), point(x2, y2)], fill=PAGE_LINE,
                  width=max(1, round(0.014 * box)))

    x0, y0, x1, y1 = BAND
    draw.rounded_rectangle([*point(x0, y0), *point(x1, y1)],
                           radius=BAND_RADIUS * box, fill=LOGO)
    draw.polygon([point(x, y) for x, y in BOARD], fill=LOGO)
    draw.line([point(TASSEL[0], TASSEL[1]), point(TASSEL[2], TASSEL[3])],
              fill=LOGO, width=max(1, round(TASSEL_WIDTH * box)))
    cx, cy, radius = BEAD
    bead_x, bead_y = point(cx, cy)
    r = radius * box
    draw.ellipse([bead_x - r, bead_y - r, bead_x + r, bead_y + r], fill=ACCENT)


def render(size, maskable=False, opaque=False):
    canvas = size * SUPERSAMPLE
    image = _gradient(canvas)
    _draw_logo(image, LOGO_SCALE_MASKABLE if maskable else LOGO_SCALE_ANY)
    image = image.resize((size, size), Image.LANCZOS)
    return image.convert('RGB') if opaque else image


# ── SVG renderer (same geometry, no dependencies) ───────────────────────────
def svg_markup(size=512, maskable=False, title='ClassNext'):
    scale = LOGO_SCALE_MASKABLE if maskable else LOGO_SCALE_ANY
    box = size * scale
    offset = (size - box) / 2
    fmt = lambda value: f'{round(value, 4):g}'  # noqa: E731 - keeps the SVG readable
    points = ' '.join(f'{fmt(x)},{fmt(y)}' for x, y in LEFT_PAGE)
    right = ' '.join(f'{fmt(x)},{fmt(y)}' for x, y in RIGHT_PAGE)
    lines = '\n    '.join(
        f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" '
        f'stroke="{PAGE_LINE}" stroke-width="0.014" stroke-linecap="round"/>'
        for (x1, y1), (x2, y2) in PAGE_LINES
    )
    board = ' '.join(f'{fmt(x)},{fmt(y)}' for x, y in BOARD)
    cx, cy, radius = BEAD
    gradient_id = 'cnGradient'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}"
     width="{size}" height="{size}" role="img" aria-label="{title}">
  <title>{title}</title>
  <defs>
    <linearGradient id="{gradient_id}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{GRADIENT_START}"/>
      <stop offset="1" stop-color="{GRADIENT_END}"/>
    </linearGradient>
  </defs>
  <rect width="{size}" height="{size}" fill="url(#{gradient_id})"/>
  <g transform="translate({fmt(offset)} {fmt(offset)}) scale({fmt(box)})">
    <polygon points="{points}" fill="{LOGO}"/>
    <polygon points="{right}" fill="{LOGO}"/>
    {lines}
    <rect x="{fmt(BAND[0])}" y="{fmt(BAND[1])}" width="{fmt(BAND[2] - BAND[0])}"
          height="{fmt(BAND[3] - BAND[1])}" rx="{fmt(BAND_RADIUS)}" fill="{LOGO}"/>
    <polygon points="{board}" fill="{LOGO}"/>
    <line x1="{fmt(TASSEL[0])}" y1="{fmt(TASSEL[1])}" x2="{fmt(TASSEL[2])}" y2="{fmt(TASSEL[3])}"
          stroke="{LOGO}" stroke-width="{fmt(TASSEL_WIDTH)}" stroke-linecap="round"/>
    <circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(radius)}" fill="{ACCENT}"/>
  </g>
</svg>
'''


def write_png(image, name):
    path = os.path.join(ICON_DIR, name)
    image.save(path, 'PNG', optimize=True)
    print(f'  {name:26} {image.size[0]}x{image.size[1]}  {os.path.getsize(path):,} bytes')


def main():
    os.makedirs(ICON_DIR, exist_ok=True)

    print('Logo')
    svg_path = os.path.join(ICON_DIR, 'logo.svg')
    with open(svg_path, 'w', encoding='utf-8') as handle:
        handle.write(svg_markup())
    print(f'  {"logo.svg":26} scalable      {os.path.getsize(svg_path):,} bytes')

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
    print(f'  {"favicon.ico":26} 16/32/48      {os.path.getsize(ico_path):,} bytes')

    print('\nDone. Logo and icons written to app/static.')


if __name__ == '__main__':
    main()
