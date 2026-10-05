# ClassNext Design System

## Product identity

- **Name:** ClassNext
- **Tagline:** Learn • Practice • Achieve
- **Audience:** teachers and students
- **UI language:** English; content can contain user-authored Unicode text
- **Primary experience:** responsive server-rendered web application with PWA support

## Design principles

- Make subjects and published lessons easy to discover.
- Keep teacher management workflows separate from student consumption flows.
- Show success, validation, empty, denied, and error states explicitly.
- Use reusable partials and CSS components instead of page-specific duplication.
- Preserve readable typography and keyboard-visible focus states.
- Keep the interface usable from mobile widths through desktop layouts.

## Layout patterns

### Public and authentication

The public site uses a shared sticky header with a compact primary navigation,
Explore disclosure, resource search, role-aware account action, and theme toggle.
The mobile drawer supports keyboard focus, Escape, outside-click, and responsive
breakpoints. The footer combines a class-browsing call to action with role-aware
account links, help, and policy navigation. All public pages share ambient
backgrounds, responsive content widths, and elevated cards. The home hero, FAQ,
authentication pages, and footer use a deep navy-to-indigo gradient.
Login and registration use a split layout: a branded learning panel beside a
focused form. On mobile the panel becomes compact and the form stacks into one
column. Forgot-password and reset-password keep a centered single-card layout.

### Teacher shell

Teacher pages use a reusable sidebar and topbar. The dashboard shows counts and
recent activity. CRUD pages use cards, forms, tables, confirmation actions, and
publication badges.

### Student shell

Student pages use a separate navigation partial and focus on discovery:
subject cards, content cards, filters, search, reading layout, announcements,
and related content.

### Shared states

- Flash alerts for success, warning, info, and error messages
- Empty states with an explanation and next action
- 400, 403, 404, 413, 429, and 500 pages built on `errors/error.html`
- Responsive sidebar behavior on small screens (drawer with overlay, Escape to close)
- Form error and validation messaging

## Visual system

The source of truth is `app/static/css/tokens.css`. Reusable components are
defined in `app/static/css/components.css`, while page-specific adjustments are
in `app/static/css/pages.css`.

The implemented visual language includes:

- Indigo primary color (`#4F46E5`) and slate neutrals
- Emerald success, amber warning, red error, and blue information states
- Inter with a system font fallback stack
- Consistent spacing, border-radius, shadows, and focus rings
- Responsive content grids and readable lesson typography
- A dark theme: `[data-theme='dark']` token overrides plus `color-scheme: dark`
- Subtle indigo/teal ambient page backgrounds and navy gradient feature panels
- Consistent elevated cards, focus treatments, animated entrance, and hover
  feedback across public, student, and teacher layouts
- Lightweight floating details and FAQ disclosure motion; all motion respects
  `prefers-reduced-motion`

Do not introduce new one-off colors or spacing values when an existing token or
component can express the design.

## Theming

- `app/static/js/theme.js` runs before paint, reads `classnest_theme` from
  `localStorage`, and falls back to `prefers-color-scheme`.
- `app/static/js/app.js` toggles the theme, persists the choice, and keeps the
  dashboard `#themeToggle` and public `[data-theme-toggle]` icon in sync.
- `[data-theme='dark']` in `tokens.css` overrides the color, border, and shadow
  tokens; `components.css` sets `color-scheme: dark`.
- The choice is applied on `<html data-theme="light|dark">`.

## Accessibility and responsive behavior

- Use semantic headings, labels, buttons, and links.
- Provide a skip link to `#main-content`.
- Track state with `aria-current`, `aria-expanded`, and `aria-pressed`.
- Keep visible focus indicators.
- Keep the public Explore menu and mobile navigation operable by keyboard.
- Maintain readable contrast for text and status badges in both themes.
- Ensure controls remain usable at approximately 360px viewport width; touch
  targets are at least 40px.
- Stack registration fields and the shared visual panel cleanly on narrow screens.
- Avoid horizontal overflow in tables, cards, and reading pages.
- Keep entered form values available after validation errors.
- Honor `prefers-reduced-motion` by collapsing transitions to `0ms`.

## FAQ content

When no published database FAQ entries exist, `/faq` displays ten factual
ClassNext answers from `app/routes/public.py`. Published FAQ rows take precedence.
The page uses native `<details>` disclosure controls so answers remain keyboard
accessible without JavaScript.

## PWA behavior

- `manifest.webmanifest` defines app metadata, icons, theme `#4f35e8`,
  standalone display, `orientation: "any"`, and `background_color`.
  `/manifest.json` serves the same file for already-installed PWAs.
- `sw.js` uses cache-first behavior for static assets, never caches HTML, and
  falls back to the precached `/offline` page when a navigation fails.
- `app/static/js/install-prompt.js` handles mobile installation guidance with a
  7-day dismissal memory and a once-per-session display gate.
- HTTPS is required for production service-worker installation.
- `/favicon.ico` is served from the site root as well as `/static`, because
  browsers request that path without going through the static route.
- `app/static/icons/logo.svg` is the single source of truth for the mark: it
  appears in both sidebars, the auth pages, and the SVG favicon, and
  `tools/generate_icons.py` rasterises the same geometry into every PNG.
- Palette: purple `#7A3BF0` to blue `#3E63E8` gradient, white logo, orange
  `#F59E0B` accent; browser theme colour `#4f35e8`.

## Design QA checklist

- [ ] Test at mobile, tablet, desktop, and wide desktop widths.
- [ ] Test keyboard navigation and focus visibility.
- [ ] Test light and dark themes for contrast and readable status colors.
- [ ] Test empty, validation, forbidden, not-found, too-large, rate-limited, and
      server-error states.
- [ ] Test teacher and student navigation independently.
- [ ] Confirm the service worker does not cache authenticated form responses.
- [ ] Confirm `/offline` renders correctly from the service-worker cache.

## Change record

| Date | Change |
|------|--------|
| 2026-10-05 | Redesigned the public navigation and footer; added route-specific catalog/help content and corrected resource route selection |
| 2026-10-05 | Set ClassNext identity and documented the shared gradient visual language, responsive auth split, motion, and ten FAQ defaults |
| 2026-10-03 | Replaced the stale product identity and framework assumptions with the implemented ClassNest UI system |
| 2026-10-03 | Documented template shells, CSS token files, responsive behavior, and PWA design |
| 2026-10-03 | Added dark mode, the offline page, extended error states, skip link, ARIA state, and reduced-motion rules |
