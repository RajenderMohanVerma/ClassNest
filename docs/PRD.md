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
- Login and logout
- Student registration
- Password hashing and duplicate-email validation
- Login/register rate limits

### Teacher portal

- Dashboard statistics
- Subject create, edit, and delete
- Content create, edit, preview, publish/draft toggle, and delete
- Content types and sanitized HTML body
- Announcement create, edit, publish state, and delete
- Student overview
- Uploaded-file list and delete
- Profile and password update

### Student portal

- Dashboard with recent published material
- Subject list and subject detail
- Published content library
- Search over content fields
- Filtering by subject and content type
- Content reading view and related content
- Attachment download
- Published announcements
- Profile and password update

### Platform

- Responsive design system
- Error templates for 403, 404, and 500
- PWA manifest, service worker, and install prompt
- JSON statistics endpoint

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
- Sanitize authored HTML before rendering.
- Validate upload extension and MIME type.
- Use PostgreSQL and persistent object storage for production hosting.
- Use secure cookies and HTTPS in production.
- Keep errors explicit and avoid silent success fallbacks.
- Preserve usable mobile, keyboard, and accessibility behavior.

## Out of scope for the current MVP

- Email verification and password-reset delivery
- Payments, subscriptions, and premium enrollment
- Progress tracking, bookmarks, and certificates
- Real-time notifications or discussion forums
- Rich-text editor integration
- Background jobs and analytics rollups
- Durable serverless file storage integration

## Change record

| Date | Change |
|------|--------|
| 2026-10-03 | Replaced the stale education-platform PRD with the implemented ClassNest MVP requirements |
| 2026-10-03 | Added feature acceptance workflow, security requirements, and explicit MVP gaps |
