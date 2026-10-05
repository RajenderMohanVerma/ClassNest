# ClassNext Project Memory

## Current project state

- Project: ClassNext — online teaching platform by Er. Amit Sir
- Tagline: `Learn • Practice • Achieve`
- Status: Phases 1-4 built; Phase 5 (student area) is next
- Canonical specification: `docs/ClassNext — Final A-to-Z Master Development Prompt.md`
  (111 sections). It supersedes any earlier prompt for this project.
- Repository: `https://github.com/RajenderMohanVerma/ClassNest`
- Branch: `main`
- Vercel entry point: `api/index.py`
- Database provider: Supabase PostgreSQL
- Runtime: Flask app factory with Jinja2 templates
- Upload storage: `instance/uploads` by default, `/tmp/classnext-uploads` on Vercel

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
- Use additive migrations only. Never reset or rebuild the database.
- Require email verification only when a mail transport is configured; a failed
  send rolls the new account back rather than stranding an unverifiable user.
- Re-check `account_status` on every request, so a suspension ends the live
  session immediately rather than at the next login.
- Keep premium checkout disabled until a gateway is configured, so an
  incomplete integration can never present a fake payment success.

## Current feature inventory

### Public website (Phase 3)
- Home, classes, subject, chapter and content pages; notes / videos /
  free-resources libraries; courses and course detail; premium; notices; about;
  FAQ; contact; legal (privacy, terms, refund); search; `sitemap.xml`;
  `robots.txt`
- Shared shell: responsive header, footer, dark/light theme, search, account menu
- SEO: canonical URL, Open Graph, JSON-LD, per-page titles and descriptions,
  `noindex` on gated pages

### Authentication (Phase 4)
- Login with validated `next`, student registration (name, email, password,
  class, optional phone), POST logout
- Email verification and password reset via single-use, expiring, hashed
  `account_tokens`; verification resend; forgot-password that never reveals
  whether an address has an account
- Account status (`active` / `suspended` / `disabled`) enforced at login and on
  every request; `last_login_at` recorded

### Teacher
- Dashboard, subjects CRUD, content CRUD with unique slugs, preview, publish
  toggle, list filters/search/sort/pagination, announcements CRUD, student
  search, file list/delete, profile

### Student
- Dashboard, subjects with published counts, content library with
  filters/sort/pagination, content detail, download through `/files`, search over
  title/topic/body, announcements, profile

### Platform
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
- Verification scripts: `tools/smoke_live.py`, `tools/smoke_auth.py`,
  `tools/check_seo.py`
- Tests: 234 pytest tests in `tests/` against in-memory SQLite (110 original,
  54 schema, 60 public site, 31 auth, plus route coverage)

## Known gaps and follow-up decisions

- Phase 5 student area: `/student/learning`, bookmarks, progress, notifications.
- Phase 6 admin CMS: `/admin/*` CRUD for classes, chapters, courses, notices,
  site settings, audit log.
- Phase 7 premium: checkout, server-side payment verification, orders, receipts.
- Move file objects from local disk to persistent object storage for Vercel or
  other serverless hosting (currently `/tmp/classnext-uploads`).
- Configure shared Flask-Limiter storage (`RATE_LIMIT_STORAGE_URI`) for multiple
  instances.
- Set `MAIL_*` in production to enable verification and password-reset email.
- Two production `Content` rows reference thumbnails
  (`84e110d6defe4111b79b6064d24a1e99.png`, `78eacaa7a91a4f68be67cb5f3a85886d.jpg`)
  that are not among the 6 `uploaded_files` records; confirm before publishing.

## Documentation workflow

1. Read the six files in `docs/` before significant changes.
2. Update the relevant document in the same change as implementation.
3. Record meaningful decisions and known gaps here.
4. Update `Task.md` with acceptance criteria and verification results.
5. Never record real credentials, connection strings, or private data.

## Change record

| Date | Decision or update |
|------|-------------------|
| 2026-10-05 | Rebuilt the project as ClassNext; additive schema foundation, responsive UI shell, and the full public website |
| 2026-10-05 | Added email verification, password reset, account-status enforcement, and 31 auth tests (234 total) |
| 2026-10-03 | Reconciled project memory with the implemented Flask application |
| 2026-10-03 | Recorded current features, GitHub state, deployment gaps, and follow-up work |
| 2026-10-03 | Added the Vercel entry point and deployment configuration |
| 2026-10-03 | Recorded dark mode, offline page, health check, files blueprint, unique slugs, `published_at`, filter-preserving pagination, upload hardening, security headers, and the 77-test suite |
