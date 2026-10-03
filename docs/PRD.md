# ClassNest Product Requirements

## Product summary

ClassNest is a teacher-student learning portal. Teachers publish structured
learning material and announcements; students discover and read published
content through a responsive web application.

## Goals

- Provide a clear teacher workflow for subjects, content, announcements, and
  uploaded resources.
- Give students a searchable, filterable content library.
- Enforce teacher/student authorization on the server.
- Provide a secure and accessible responsive interface.
- Use Supabase PostgreSQL consistently across local, preview, and production
  environments.
- Provide an installable PWA experience for supported mobile browsers.

## Personas

### Teacher

Creates subjects, authors content, publishes or drafts lessons, manages
announcements, reviews students, manages files, and updates a profile.

### Student

Registers publicly, browses subjects, reads published lessons, searches and
filters content, downloads available attachments, views announcements, and
updates a profile.

## Implemented MVP capabilities

### Public and authentication

- Landing redirect
- Login and POST-only logout (a same-site `next` target is honoured and validated)
- Student registration
- Password hashing and duplicate-email validation
- Login/register rate limits plus a 300-per-hour global default
- "Remember me" session control with `SESSION_HOURS` lifetime

### Teacher portal

- Dashboard statistics
- Subject create, edit, and delete (delete only when the subject is empty)
- Content create, edit, preview, publish/draft toggle, and delete
- Six content types and sanitized HTML body
- Unique slugs with collision suffixes
- Content list with search (`q`), status, subject, type filters and sorting
- Announcement create, edit, publish state, and delete
- Student overview with search
- Uploaded-file list and delete
- Profile and password update

### Student portal

- Dashboard with recently published material ordered by `published_at`
- Subject list with published lesson counts and subject detail
- Published content library with subject/type filters, per-type counts, and sorting
- Search over titles, topics, and body text
- Pagination that preserves the active filters and sort
- Content reading view and related content
- Attachment download through the authenticated file route, using the original filename
- Published announcements
- Profile and password update

### Platform

- Responsive design system with light and dark themes
- Error templates for 400, 403, 404, 413, 429, and 500 (JSON for API clients)
- PWA manifest, service worker, install prompt, and an offline fallback page
- JSON statistics and content-type endpoints
- Health-check endpoint reporting database reachability
- Security response headers and `no-store` caching for authenticated pages
- Automated test suite covering authentication, roles, CRUD, uploads, search, pagination, and error handling

## Functional acceptance workflow

1. A teacher account is created with `create_teacher.py`.
2. The teacher logs in and creates a subject.
3. The teacher creates content and publishes it.
4. A student registers through the public registration page.
5. The student sees the subject and published content.
6. The student searches, filters, reads, and downloads permitted content.
7. The teacher posts an announcement that appears in the student portal.
8. Unauthorized role access returns an explicit forbidden response.

## Non-functional requirements

- Never expose password hashes in templates or APIs.
- Protect mutating browser requests with CSRF.
- Sanitize authored HTML before rendering: allowlisted tags only, unsafe element
  content removed, inline `style` attributes stripped.
- Validate uploads on three layers: extension allowlist (no SVG), client MIME
  allowlist, and content/magic-byte signature; reject empty files.
- Never serve uploads from the public static tree; deliver them only through the
  authenticated file route behind a publication check.
- Reject open redirects: `next` targets must stay on this site.
- Send security response headers and disable caching for authenticated pages.
- Use PostgreSQL and persistent object storage for production hosting.
- Use secure cookies and HTTPS in production.
- Share rate-limit state across instances with `RATE_LIMIT_STORAGE_URI`.
- Keep errors explicit and avoid silent success fallbacks.
- Preserve usable mobile, keyboard, and accessibility behavior.

## Out of scope for the current MVP

- Email verification and password-reset delivery
- Payments, subscriptions, and premium enrollment
- Progress tracking, bookmarks, and certificates
- Real-time notifications or discussion forums
- Rich-text editor integration
- Background jobs and analytics rollups
- Durable serverless file storage integration (Vercel currently writes to
  `/tmp/classnest-uploads`, which is ephemeral)

## Change record

| Date | Change |
|------|--------|
| 2026-10-03 | Replaced the stale education-platform PRD with the implemented ClassNest MVP requirements |
| 2026-10-03 | Added feature acceptance workflow, security requirements, and explicit MVP gaps |
| 2026-10-03 | Documented dark mode, offline page, health check, secure file delivery, unique slugs, filter-preserving pagination, three-layer upload validation, and the 77-test suite |
