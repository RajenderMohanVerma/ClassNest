# ClassNest Project Memory

## Current project state

- Project: ClassNest Teacher-Student Learning Portal
- Status: Flask MVP implemented and pushed to GitHub
- Repository: `https://github.com/RajenderMohanVerma/ClassNest`
- Branch: `main`
- Vercel entry point: `api/index.py`
- Vercel configuration: `vercel.json`
- Database provider: Supabase PostgreSQL
- Runtime: Flask app factory with Jinja2 templates

## Implemented decisions

- Use Flask blueprints for public, authentication, teacher, student, and API
  concerns.
- Use SQLAlchemy models rather than raw SQL.
- Keep teacher role assignment out of ordinary public registration.
- Use session authentication with role decorators.
- Use Werkzeug password hashing.
- Enable global CSRF protection for mutating forms.
- Sanitize authored HTML with Bleach before rendering it as safe content.
- Validate uploaded files by extension and MIME type and store UUID filenames.
- Require a PostgreSQL `DATABASE_URL` in every environment.
- Keep the UI server-rendered and progressively enhanced with vanilla JS.

## Current feature inventory

- Authentication: login, student registration, logout
- Teacher: dashboard, subjects CRUD, content CRUD, preview, publish toggle,
  announcements CRUD, student list, file list/delete, profile
- Student: dashboard, subjects, content library, content detail, download,
  announcements, search, profile
- API: statistics endpoint at `/api/stats`
- PWA: manifest, service worker, install prompt, responsive UI
- Error handling: 403, 404, and 500 templates

## Known gaps and follow-up decisions

- Add a real Flask-Migrate initial migration before production schema changes.
- Complete the Vercel project import, environment variables, and production
  smoke test.
- Move file objects from local disk to persistent object storage for Vercel or
  other serverless hosting.
- Configure Redis-backed Flask-Limiter storage for multiple instances.
- Add automated route/model tests and deployment smoke tests.
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
