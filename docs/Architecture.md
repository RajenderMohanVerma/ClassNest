# Architecture

## Project

Er. Amit Sir Academy — Learn, Practice, Achieve.

This document records the technical structure and cross-system decisions. The
complete master specification is maintained in the repository root at
`PROJECT_MEMORY.md`; update this document whenever an implementation decision
changes.

## Required architecture

- Public pages must support SSR or SSG for SEO.
- The backend is a separate REST API service under `/api/v1`.
- API responses use the envelope `{ success, data, message, meta }`.
- Use a relational database with migrations. PostgreSQL is the recommended
  production database.
- Files are stored through an external storage provider. Store metadata in the
  database, not large file contents.
- Background jobs run for scheduled publishing, notice expiry, payment
  reconciliation, queued email, and analytics rollups.
- Client and server both validate form and API input with schemas.

## Selected implementation stack

- Web application: Next.js 15, React 19, TypeScript, App Router.
- API service: Fastify 5, TypeScript, versioned REST routes.
- Database: PostgreSQL with Prisma migration workflow.
- Development orchestration: npm workspaces and Docker Compose for PostgreSQL.
- Payment provider: Razorpay.

## Core domains

1. Authentication and revocable sessions.
2. Classes, subjects, chapters, courses, lessons, and content items.
3. Students, enrollments, bookmarks, progress, and notifications.
4. Orders, payments, invoices, and verified course access.
5. Admin CMS, media library, settings, analytics, and audit logs.

## Security boundaries

- The backend is the only authority for content access decisions.
- Access tokens are short-lived; refresh tokens rotate and are revocable.
- Authentication cookies are `httpOnly`, `Secure`, and `SameSite=Lax`.
- Premium media is returned only through short-lived signed URLs after an
  enrollment check.
- Passwords use a memory-hard password hash.
- Mutating cookie-authenticated requests require Origin/Referer validation.
- Money is stored as integer paise, never floating-point values.

## Time and localization

- Store timestamps in UTC.
- Display dates in `Asia/Kolkata`.
- Support UTF-8 content in English, Hindi, and Hinglish.

## Change record

| Date | Change | Reason |
|------|--------|--------|
| 2026-10-03 | Created architecture source document | Establish project documentation baseline |
| 2026-10-03 | Added Next.js/Fastify TypeScript monorepo foundation | Begin Phase 1 implementation |
