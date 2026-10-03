# ClassNest Design System

## Product identity

- **Name:** ClassNest
- **Tagline:** Teacher & Student Learning Portal
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

The landing page redirects users to the appropriate experience. Login and
registration use focused forms with validation feedback and flash messages.

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

Do not introduce new one-off colors or spacing values when an existing token or
component can express the design.

## Theming

- `app/static/js/theme.js` runs before paint, reads `classnest_theme` from
  `localStorage`, and falls back to `prefers-color-scheme`.
- `app/static/js/app.js` toggles the theme, persists the choice, and keeps the
  `#themeToggle` icon in sync with `data-theme-icon`.
- `[data-theme='dark']` in `tokens.css` overrides the color, border, and shadow
  tokens; `components.css` sets `color-scheme: dark`.
- The choice is applied on `<html data-theme="light|dark">`.

## Accessibility and responsive behavior

- Use semantic headings, labels, buttons, and links.
- Provide a skip link to `#main-content`.
- Track state with `aria-current`, `aria-expanded`, and `aria-pressed`.
- Keep visible focus indicators.
- Maintain readable contrast for text and status badges in both themes.
- Ensure controls remain usable at approximately 360px viewport width; touch
  targets are at least 40px.
- Avoid horizontal overflow in tables, cards, and reading pages.
- Keep entered form values available after validation errors.
- Honor `prefers-reduced-motion` by collapsing transitions to `0ms`.

## PWA behavior

- `manifest.json` defines app metadata, icons, theme, standalone display,
  `orientation: "portrait"`, and a `background_color`.
- `sw.js` uses cache-first behavior for static assets, never caches HTML, and
  falls back to the precached `/offline` page when a navigation fails.
- `app/static/js/install-prompt.js` handles mobile installation guidance with a
  7-day dismissal memory and a once-per-session display gate.
- HTTPS is required for production service-worker installation.

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
| 2026-10-03 | Replaced the stale product identity and framework assumptions with the implemented ClassNest UI system |
| 2026-10-03 | Documented template shells, CSS token files, responsive behavior, and PWA design |
| 2026-10-03 | Added dark mode, the offline page, extended error states, skip link, ARIA state, and reduced-motion rules |
