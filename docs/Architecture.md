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
├── __init__.py                 # create_app, extensions, blueprints, errors
├── config.py                   # environment-driven configuration
├── extensions.py               # db, migrate, csrf, limiter
├── models/
│   ├── user.py                 # teacher and student accounts
│   ├── subject.py              # subject/topic records
│   ├── content.py              # notes, videos, PDF/resource metadata
│   ├── announcement.py         # teacher announcements
│   └── uploaded_file.py        # attachment metadata
├── routes/
│   ├── public.py               # public landing route
│   ├── auth.py                 # login, registration, logout
│   ├── teacher.py              # teacher dashboard and CRUD
│   ├── student.py              # student browsing and profile
│   └── api.py                  # JSON statistics endpoint
├── services/
│   ├── decorators.py           # login and role authorization
│   ├── sanitizer.py            # allowlisted HTML sanitization
│   └── uploads.py              # extension/MIME validation and storage
├── templates/                  # base, partials, public, teacher, student
└── static/                     # CSS, JavaScript, icons
```

The application is created by `create_app()` and registers five blueprints:
public, auth, teacher, student, and API. The same factory can be used by
`run.py`, tests, the Flask CLI, and a Vercel serverless entry point.

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
| `User` | Account, role, profile, password hash | owns subjects/content/announcements/files |
| `Subject` | Teacher-owned learning subject | has many content records |
| `Content` | Learning item and publication state | belongs to a subject and author |
| `Announcement` | Teacher message with publication state | belongs to an author |
| `UploadedFile` | Stored attachment metadata | belongs to uploader and optional content |

All timestamps are timezone-aware UTC values. Slugs are generated for subjects
and content to provide readable URLs.

## Storage boundaries

The database stores metadata and text content. Uploads are written to the
configured `UPLOAD_FOLDER`, using a UUID filename after extension and MIME
validation. Local storage is suitable for development only. Production
deployments on serverless platforms must move uploaded objects to persistent
storage such as S3, Cloudflare R2, Cloudinary, or Vercel Blob while retaining
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
TLS-terminating reverse proxy. For Vercel, use an `api/index.py` entry point
that exposes `app = create_app()` and configure `vercel.json`.

## Security boundaries

- Never commit `.env`, database files, or uploaded files.
- Set a strong production `SECRET_KEY`.
- Use Supabase PostgreSQL through the Session Pooler URL.
- Keep `SESSION_COOKIE_SECURE=True` behind HTTPS.
- Sanitize user-authored HTML before storing it.
- Validate both upload extension and MIME type.
- Keep teacher role assignment outside public registration.
- Use Redis-backed rate-limit storage when running multiple production
  instances.

## Known architecture limitations

- There is no email/password-reset provider in the current MVP.
- Upload storage is local and must be replaced for durable serverless hosting.
- Flask-Migrate is configured, but an initial migration history has not been
  committed; `init_db.py` currently creates tables directly.
- No background job queue, real-time notifications, or payment workflow is
  implemented.

## Change record

| Date | Change |
|------|--------|
| 2026-10-03 | Replaced the stale TypeScript architecture with the implemented Flask architecture |
| 2026-10-03 | Documented models, blueprints, security, storage, and deployment boundaries |
