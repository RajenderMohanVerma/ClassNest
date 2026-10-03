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
- 403, 404, and 500 pages
- Responsive sidebar behavior on small screens
- Form error and validation messaging

## Visual system

The source of truth is `app/static/css/tokens.css`. Reusable components are
defined in `app/static/css/components.css`, while page-specific adjustments are
in `app/static/css/pages.css`.

The implemented visual language includes:

- Indigo primary color and slate neutrals
- Green success, amber warning, red error, and blue information states
- System font stack for fast loading
- Consistent spacing, border-radius, shadows, and focus rings
- Responsive content grids and readable lesson typography

Do not introduce new one-off colors or spacing values when an existing token or
component can express the design.

## Accessibility and responsive behavior

- Use semantic headings, labels, buttons, and links.
- Keep visible focus indicators.
- Maintain readable contrast for text and status badges.
- Ensure controls remain usable at approximately 360px viewport width.
- Avoid horizontal overflow in tables, cards, and reading pages.
- Keep entered form values available after validation errors.

## PWA behavior

- `manifest.json` defines app metadata, icons, theme, and standalone display.
- `sw.js` uses cache-first behavior for static assets and network-first
  behavior for HTML.
- `app/static/js/install-prompt.js` handles mobile installation guidance.
- HTTPS is required for production service-worker installation.

## Design QA checklist

- [ ] Test at mobile, tablet, desktop, and wide desktop widths.
- [ ] Test keyboard navigation and focus visibility.
- [ ] Test empty, validation, forbidden, not-found, and server-error states.
- [ ] Test teacher and student navigation independently.
- [ ] Confirm the service worker does not cache authenticated form responses.

## Change record

| Date | Change |
|------|--------|
| 2026-10-03 | Replaced the stale product identity and framework assumptions with the implemented ClassNest UI system |
| 2026-10-03 | Documented template shells, CSS token files, responsive behavior, and PWA design |
