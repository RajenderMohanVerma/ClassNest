# ClassNest Architecture

## Product

ClassNest is a server-rendered teacher-student learning portal built with
Flask. Teachers manage subjects, learning content, announcements, students,
and uploaded resources. Students browse published content, search the library,
read lessons, download permitted attachments, and manage their profiles.

## Technology stack

- **Backend:** Flask 3.1 application factory
- **ORM:** Flask-SQLAlchemy / SQLAlchemy 2.x
- **Database:** Supabase PostgreSQL for development and production
- **Templates:** Jinja2 server-rendered HTML
- **Frontend:** Vanilla JavaScript and custom CSS
- **Forms/security:** Flask-WTF CSRF protection, Werkzeug password hashing,
  Bleach HTML sanitization
- **Rate limiting:** Flask-Limiter
- **Migrations:** Flask-Migrate is initialized and ready for migration files
- **Production server:** Gunicorn
- **PWA:** Web manifest, service worker, and install prompt

## Application structure

```text
app/
├── __init__.py                 # create_app, blueprints, errors, /healthz, headers
├── config.py                   # dev/production/testing configuration + validation
├── extensions.py               # db, migrate, csrf, limiter
├── models/
│   ├── user.py                 # teacher and student accounts
│   ├── subject.py              # subject/topic records
│   ├── content.py              # notes, videos, PDF/resource metadata
│   ├── announcement.py         # teacher announcements
│   └── uploaded_file.py        # attachment metadata
├── routes/
│   ├── public.py               # landing route and offline page
│   ├── auth.py                 # login, registration, POST logout
│   ├── teacher.py              # teacher dashboard and CRUD
│   ├── student.py              # student browsing and profile
│   ├── files.py                # authenticated file delivery
│   └── api.py                  # JSON statistics and content-type endpoints
├── services/
│   ├── decorators.py           # login and role authorization, safe_next_url
│   ├── sanitizer.py            # allowlisted HTML sanitization
│   ├── uploads.py              # extension/MIME/signature validation and storage
│   ├── accounts.py             # shared profile and password updates
│   └── pagination.py           # filter-preserving pagination arguments
├── templates/                  # base, partials, public, teacher, student, errors
└── static/                     # CSS, JavaScript, icons

api/index.py                    # Vercel serverless entry point
tests/                          # pytest suite (in-memory SQLite)
```

The application is created by `create_app()` and registers six blueprints:
public, auth, teacher, student, files, and API. It also serves `/manifest.json`,
`/sw.js`, and `/healthz` at the app level. The same factory is used by `run.py`,
tests, the Flask CLI, and the Vercel entry point. Configuration classes cover
development, production, and testing; production refuses to boot without a real
`SECRET_KEY` and a PostgreSQL `DATABASE_URL`.

## Request and authorization flow

1. A browser sends a request to a Flask route.
2. The route reads the session and loads the current user where necessary.
3. `login_required`, `teacher_required`, or `student_required` enforces access.
4. SQLAlchemy performs database reads/writes through model relationships.
5. Mutating form requests are protected by the global CSRF extension.
6. Templates render a response or the API returns JSON.

Teacher accounts are created by `create_teacher.py`; public registration creates
student accounts only. Role checks are server-side and are not dependent on
sidebar visibility.

## Data model

| Model | Purpose | Key relationships |
|-------|---------|-------------------|
| `User` | Account, role, profile, password hash, avatar | owns subjects/content/announcements/files |
| `Subject` | Teacher-owned learning subject | has many content records |
| `Content` | Learning item and publication state | belongs to a subject and author; owns uploaded files |
| `Announcement` | Teacher message with publication state | belongs to an author |
| `UploadedFile` | Stored attachment metadata | belongs to uploader and optional content |

All timestamps are timezone-aware UTC values. Slugs are generated for subjects
and content to provide readable URLs; `unique_slug()` appends `-2`, `-3`, … when
a name repeats and supports `exclude_id` so renaming keeps the slug stable.
`content.slug` and `subjects.slug` carry unique indexes created by `init_db.py`.
`publish()`/`unpublish()` maintain `published_at`; unpublishing clears it.
`content_type`, `status`, and `users.role` also carry CHECK constraints that
mirror `config.py`.

## Storage boundaries

The database stores metadata and text content. Uploads are written to the
configured `UPLOAD_FOLDER` (default `instance/uploads`), using a UUID filename
after extension, MIME, and content-signature validation. The folder lives
outside `app/static`, and `/static/uploads/*` is rejected before routing.
`LEGACY_UPLOAD_FOLDER` (`app/static/uploads`) is a read-only fallback for files
created before the move; `init_db.py` migrates them into the current folder.
If the configured folder is unwritable, or on Vercel/Lambda, the application
falls back to `/tmp/classnest-uploads`.

Local storage is suitable for development only. Production deployments on
serverless platforms must move uploaded objects to persistent storage such as
S3, Cloudflare R2, Cloudinary, Supabase Storage, or Vercel Blob while retaining
metadata in PostgreSQL.

## Deployment architecture

```text
Browser
  │
  ├── Vercel Python function (Flask entry point)
  ├── Supabase PostgreSQL
  └── Object storage for uploaded files
```

For a traditional server deployment, Gunicorn can serve `run:app` behind a
TLS-terminating reverse proxy (`Procfile` documents the command). For Vercel,
`api/index.py` exposes `app = create_app()` after normalizing the database URL,
and `vercel.json` builds that function and rewrites all requests to it.

## Security boundaries

- Never commit `.env`, database files, or uploaded files.
- Set a strong production `SECRET_KEY`.
- Use Supabase PostgreSQL through the Session Pooler URL; `postgres://` and
  `postgresql+psycopg://` prefixes are normalized at startup.
- Keep `SESSION_COOKIE_SECURE=True` behind HTTPS.
- Sanitize user-authored HTML before storing it.
- Validate uploads on three layers: extension allowlist, client MIME allowlist,
  and content/magic-byte signature; reject empty files and never allow SVG.
- Keep uploads outside `app/static` and deliver them only through `/files/...`
  behind `@login_required` plus a publication check.
- Reject open redirects through `safe_next_url`.
- Send security response headers (`X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Permissions-Policy`, CSP, and HSTS in production) and
  `Cache-Control: no-store` on authenticated pages.
- Keep teacher role assignment outside public registration.
- Use Redis-backed rate-limit storage (`RATE_LIMIT_STORAGE_URI`) when running
  multiple production instances; the default limit is 300 requests per hour
  plus per-route limits on login and registration.

## Testing architecture

`TestingConfig` swaps PostgreSQL for in-memory SQLite, points uploads at a
temporary directory, and disables CSRF and rate limiting so the 77-test suite in
`tests/` runs in isolation from Supabase.

## Known architecture limitations

- There is no email/password-reset provider in the current MVP.
- Upload storage is local and must be replaced for durable serverless hosting.
- Flask-Migrate is configured, but an initial migration history has not been
  committed; `init_db.py` creates tables and applies an additive sync instead.
- No background job queue, real-time notifications, or payment workflow is
  implemented.
- Rate-limit counters are per-process unless a shared backend is configured.

## Change record

| Date | Change |
|------|--------|
| 2026-10-03 | Replaced the stale TypeScript architecture with the implemented Flask architecture |
| 2026-10-03 | Documented models, blueprints, security, storage, and deployment boundaries |
| 2026-10-03 | Added the files blueprint, upload-folder move with legacy fallback, testing architecture, headers, and validation rules |
