# Product Requirements Document

## Product summary

Er. Amit Sir Academy is an education platform where students discover
learning resources, enroll in courses, pay for premium content, learn through
structured lessons, and track progress. Administrators manage the full
content, student, commerce, and website lifecycle.

## Goals

- Provide fast, searchable access to organized academic content.
- Support free and paid courses with reliable access control.
- Let students resume learning and see meaningful progress.
- Give administrators complete CMS and commerce controls.
- Maintain secure, auditable payment and enrollment workflows.

## Personas

- Student: discovers content, learns, bookmarks, and tracks progress.
- Parent/visitor: explores classes, courses, teachers, and pricing.
- Administrator: manages content, students, payments, settings, and reports.

## MVP capabilities

- Public home, classes, subjects, chapters, courses, videos, notes, audio,
  playlists, notices, search, contact, and legal pages.
- Registration, login, email verification, password recovery, and reset.
- Student dashboard with courses, learning view, bookmarks, progress,
  notifications, purchases, invoices, and profile.
- Admin dashboard with content management, media, courses, notices, students,
  orders, payments, analytics, settings, contact messages, and audit log.
- Razorpay-compatible payment flow with server-side verification and
  reconciliation.

## Non-functional requirements

- SEO-friendly public rendering.
- Server-side authorization for every protected operation.
- Schema validation on both client and server.
- Responsive and accessible UI.
- Idempotent background jobs and webhook/payment processing.
- Explicit errors and observable audit logs.

## Acceptance workflow

Admin creates and publishes a course; a visitor registers and purchases it;
the server verifies payment and creates enrollment; the student accesses
lessons, consumes content, and sees progress update. Unauthorized users must
not receive premium content or media URLs.

## Out of scope until approved

- Choosing a concrete framework or vendor not specified by the project owner.
- Adaptive HLS video streaming unless separately planned as a later phase.
- Any feature that bypasses the access-control and payment rules.

