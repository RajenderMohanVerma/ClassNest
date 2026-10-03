# Design

## Product identity

- Name: Er. Amit Sir Academy
- Tagline: Learn • Practice • Achieve
- Audience: school students, parents, teachers, and administrators
- UI language: English; learning content may be English, Hindi, or Hinglish

## Design principles

- Make learning content easy to discover and resume.
- Use consistent layouts for public, student, and admin experiences.
- Keep premium and free content visibly distinct without blocking discovery.
- Show loading, empty, error, success, and access-denied states explicitly.
- Prefer reusable components and design tokens over page-specific styling.
- Keep keyboard access, readable contrast, responsive layouts, and clear focus
  states in every interface.

## Main experience patterns

### Public

Header, navigation, search, content cards, filters, detail pages, related
content, and clear calls to action.

### Authentication

Focused forms for login, registration, password recovery, reset, and email
verification. Errors are specific and actionable.

### Student dashboard

Authenticated shell with dashboard summary, course learning view, progress,
bookmarks, purchases, notifications, and profile.

### Admin

Sidebar navigation, table/list views, filters, create/edit forms, media
selection, confirmation dialogs, audit visibility, and role protection.

## Visual system

Use one shared token source for colors, typography, spacing, borders, shadows,
breakpoints, and motion. Do not introduce one-off values when a token exists.
The detailed token values and page-by-page UI requirements remain defined in
`PROJECT_MEMORY.md` until the implementation stack is selected.

## Design quality checklist

- Responsive at mobile, tablet, and desktop widths.
- No horizontal overflow.
- Buttons and links have clear hover, focus, disabled, and loading states.
- Forms preserve entered values when validation fails.
- Destructive actions require confirmation.
- Empty states explain what the user can do next.

## Change record

| Date | Change | Reason |
|------|--------|--------|
| 2026-10-03 | Created design source document | Establish project documentation baseline |

