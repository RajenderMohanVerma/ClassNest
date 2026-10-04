# ClassNest Project Memory

## Current project state

- Project: ClassNest Teacher-Student Learning Portal
- Status: Flask MVP implemented and pushed to GitHub
- Repository: `https://github.com/RajenderMohanVerma/ClassNest`
- Branch: `main`
- Vercel entry point: `api/index.py`
- Vercel configuration: `vercel.json` (build + rewrite to the Flask function)
- Database provider: Supabase PostgreSQL
- Runtime: Flask app factory with Jinja2 templates
- Upload storage: `instance/uploads` by default, `/tmp/classnest-uploads` on Vercel

## Implemented decisions

- Use Flask blueprints for public, authentication, teacher, student, files, and
  API concerns.
- Use SQLAlchemy models rather than raw SQL.
- Keep teacher role assignment out of ordinary public registration.
- Use session authentication with role decorators and POST-only logout.
- Use Werkzeug password hashing (salted scrypt).
- Enable global CSRF protection for mutating forms.
- Sanitize authored HTML with Bleach before rendering it as safe content, and
  remove unsafe element content entirely.
- Validate uploaded files by extension, MIME type, and content signature; reject
  SVG and empty files; store UUID filenames outside `app/static`.
- Serve files only through `/files/...` behind login and publication checks, and
  return 404 for `/static/uploads/*`.
- Send security response headers and disable caching for authenticated pages.
- Reject open redirects through `safe_next_url`.
- Require a PostgreSQL `DATABASE_URL` outside the isolated test suite.
- Keep the UI server-rendered and progressively enhanced with vanilla JS.
- Support a light/dark theme with a pre-paint bootstrap script and
  `prefers-color-scheme` default.

## Current feature inventory

- Authentication: login with validated `next`, student registration, POST logout
- Teacher: dashboard, subjects CRUD, content CRUD with unique slugs, preview,
  publish toggle, list filters/search/sort/pagination, announcements CRUD,
  student search, file list/delete, profile
- Student: dashboard, subjects with published counts, content library with
  filters/sort/pagination, content detail, download through `/files`, search over
  title/topic/body, announcements, profile
- Files: authenticated serving by stored name and by upload id
- API: statistics at `/api/stats`, content types at `/api/content-types`
- App routes: `/healthz` (database probe), `/offline`, `/manifest.webmanifest`
  (plus the `/manifest.json` alias), `/favicon.ico`, `/sw.js`
- PWA: manifest, service worker with offline fallback, install prompt, responsive UI
- Brand assets: `icons/logo.svg` is the source of truth, used in both sidebars and
  the auth pages, plus 16/32/180/192/512 PNGs, a maskable 512, and `favicon.ico`
  rasterised from the same geometry by `tools/generate_icons.py`; theme colour
  `#4f35e8`
- Theming: light and dark design tokens with a persistent toggle
- Error handling: 400, 403, 404, 413, 429, and 500 templates (JSON for API clients)
- Tests: 110 pytest tests in `tests/` against in-memory SQLite, including PWA asset
  and head-tag assertions

## Known gaps and follow-up decisions

- Add a real Flask-Migrate initial migration before production schema changes.
- Complete the Vercel project import, environment variables, and production
  smoke test.
- Move file objects from local disk to persistent object storage for Vercel or
  other serverless hosting (currently `/tmp/classnest-uploads`).
- Configure shared Flask-Limiter storage (`RATE_LIMIT_STORAGE_URI`) for multiple
  instances.
- Add deployment smoke tests; CSRF and rate limiting are disabled in
  `TestingConfig` and are verified manually.
- Add email delivery only when password reset or verification is approved.
- Add background jobs, payments, progress tracking, or notifications only as
  separately scoped features.

## Documentation workflow

1. Read the six files in `docs/` before significant changes.
2. Update the relevant document in the same change as implementation.
3. Record meaningful decisions and known gaps here.
4. Update `Task.md` with acceptance criteria and verification results.
5. Never record real credentials, connection strings, or private data.

## Change record

| Date | Decision or update |
|------|-------------------|
| 2026-10-03 | Reconciled project memory with the implemented Flask application |
| 2026-10-03 | Recorded current features, GitHub state, deployment gaps, and follow-up work |
| 2026-10-03 | Added the Vercel entry point and deployment configuration |
| 2026-10-03 | Recorded dark mode, offline page, health check, files blueprint, unique slugs, `published_at`, filter-preserving pagination, upload hardening, security headers, and the 77-test suite |
