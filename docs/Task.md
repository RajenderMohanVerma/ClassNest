# ClassNext Task Log

## Working agreement

Plan meaningful work here before implementation. Every task must have a
user-facing goal, affected files, acceptance criteria, and verification notes.
Mark a task complete only after the relevant check passes.

## Completed implementation

### Project foundation

- [x] Create Flask application factory and configuration classes, including
      `TestingConfig` and startup validation of `DATABASE_URL`/`SECRET_KEY`.
- [x] Initialize SQLAlchemy, Flask-Migrate, CSRF, and rate limiter.
- [x] Register public, auth, teacher, student, files, and API blueprints plus the
      app-level `/healthz`, `/manifest.json`, and `/sw.js` routes.
- [x] Add environment-driven Supabase PostgreSQL configuration with URL
      normalization and pool health settings.
- [x] Add `.env.example`, `.gitignore`, `requirements.txt`,
      `requirements-dev.txt`, `Procfile`, `vercel.json`, and entry scripts.

### Data and services

- [x] Implement `User`, `Subject`, `Content`, `Announcement`, and
      `UploadedFile` models with publication timestamps and unique-slug helpers.
- [x] Add password hashing and role helpers.
- [x] Add login, teacher, and student authorization decorators plus
      `safe_next_url`.
- [x] Add HTML sanitization service with unsafe-block removal.
- [x] Add upload extension, MIME, magic-byte, UUID filename, and size handling.
- [x] Add shared account and pagination services.

### Authentication and routes

- [x] Implement login, student registration, POST-only logout, and rate limits.
- [x] Implement teacher dashboard, management routes, filters, and sorting.
- [x] Implement student dashboard, library, reading, search, and profile routes.
- [x] Implement authenticated file delivery with publication checks.
- [x] Implement statistics and content-type APIs, custom error pages, and a
      database health check.

### Frontend and PWA

- [x] Create base template and reusable navigation/alert/pagination/content-card
      partials.
- [x] Create all public, teacher, student, offline, and error templates.
- [x] Create design tokens (light and dark), reusable CSS components, and page
      styles.
- [x] Add app JavaScript, theme bootstrap, service worker, manifest, install
      prompt, and icons.
- [x] Add the complete app-icon and favicon set (16/32/180/192/512, maskable,
      `favicon.ico`) generated from `tools/generate_icons.py`, serve the manifest
      as `application/manifest+json`, and assert every asset in tests.

### Quality

- [x] Add automated authentication, authorization, CRUD, upload, search,
      pagination, and error-handling tests (`tests/`, 77 tests).
- [x] Add security response headers and `no-store` caching for private pages.
- [x] Move uploads outside the static tree and block `/static/uploads/*`.
- [x] Migrate legacy uploads and add unique slug indexes in `init_db.py`.

### Documentation and delivery

- [x] Add root setup, quickstart, build summary, checklist, and project index.
- [x] Reconcile all six `docs/` files with the actual Flask implementation.
- [x] Push the project to GitHub `RajenderMohanVerma/ClassNest` on `main`.

## Current priority: Phase 5 — student area

- [x] Phase 1: additive ClassNext schema foundation, applied to production
      without touching existing rows.
- [x] Phase 2: access-control service and the responsive shared UI shell.
- [x] Phase 3: public website (22 routes) with SEO, sitemap and robots.
- [x] Phase 4: email verification, password reset, and account-status
      enforcement on every request.
- [ ] Phase 5: `/student/learning`, bookmarks, progress, notifications, profile
      completion.
- [ ] Phase 6: admin CMS under `/admin/*` for classes, subjects, chapters,
      content, courses, notices, students and site settings.
- [x] Catalog workflow foundation: teacher class management, subject-to-class
      assignment, chapter CRUD, and class/subject/chapter validation when saving
      content. Existing unassigned subjects can be assigned without data loss.
- [x] Require a class at student registration; scope student catalogs, search,
      courses, direct content pages, and file downloads to that class.
- [ ] Phase 7: premium checkout with server-side payment verification, orders
      and receipts.
- [ ] Phase 8-10: security audit, performance pass, PWA offline behaviour, final
      verification.

## Acceptance criteria for Phase 5

- A signed-in student reaches `/student/learning` and sees only content they are
  entitled to.
- Bookmarks, progress and notifications read and write through authorized
  server-side routes with CSRF protection.
- No premium or draft content is reachable by an unauthorized request.
- The student area works from 360px to 1920px and passes the keyboard and focus
  checks in `docs/Design.md`.
- `pytest` stays green and no existing production row is modified.

## Verification commands

### Automated tests

```powershell
pip install -r requirements-dev.txt
pytest
```

### Read-only live checks

```powershell
python tools/smoke_live.py     # public pages against the configured database
python tools/smoke_auth.py     # auth pages render, no token leakage
python tools/check_seo.py      # canonical URLs and sitemap are absolute
```

### Git delivery check

```powershell
git status --short --branch
git log -1 --oneline
```

## Change record

| Date | Update |
|------|--------|
| 2026-10-05 | Added teacher-managed Class → Subject → Chapter → Content workflow and server-side hierarchy validation |
| 2026-10-05 | Completed Phases 1-4 and recorded the 234-test suite, live smoke scripts, and Phase 5 acceptance criteria |
| 2026-10-03 | Replaced the old TypeScript foundation task list with the completed Flask implementation log |
| 2026-10-03 | Added GitHub delivery status and production deployment follow-up tasks |
| 2026-10-03 | Added Vercel serverless entry point and deployment configuration |
| 2026-10-03 | Recorded the 77-test suite, dark mode, offline page, health check, files blueprint, security headers, and upload-folder move |
