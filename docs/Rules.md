# ClassNest Engineering Rules

## Documentation rules

- Keep the six files in `docs/` aligned with the implementation.
- Update the relevant documentation in the same change as an implementation.
- Do not describe planned features as implemented.
- Record known limitations instead of hiding them.
- Never commit `.env`, database files, uploaded files, credentials, or keys.

## Engineering rules

- Preserve the Flask application-factory pattern.
- Keep blueprint responsibilities separated by user experience/domain.
- Prefer SQLAlchemy ORM and existing model relationships over raw SQL.
- Reuse decorators, services, template partials, and CSS tokens.
- Validate input at the server boundary.
- Surface failures with a user-visible message or an appropriate error response.
- Avoid broad exception handlers and silent fallback behavior.
- Keep changes focused and run the smallest relevant verification.

## Security rules

- Enforce authorization on the server for every teacher/student route.
- Never allow public registration to assign the teacher role.
- Hash passwords with Werkzeug (salted scrypt); never store plaintext passwords.
- Keep CSRF protection enabled for browser form mutations; logout is POST-only.
- Sanitize user-authored HTML before using the `safe` rendering path: allowlisted
  tags only, `script/style/iframe/object/embed/form` content removed, inline
  `style` attributes stripped, comments stripped.
- Validate uploads on three layers: extension allowlist (no SVG), client MIME
  allowlist, and content/magic-byte signature; reject empty files and verify
  images when Pillow is available.
- Generate UUID storage names and never trust user-provided paths.
- Keep uploads outside `app/static`; `/static/uploads/*` must return 404.
- Deliver files only through `/files/...` behind a login check and a publication
  check for students.
- Reject open redirects: `next` targets must be same-site relative paths and must
  not target `/auth/*`.
- Send security response headers (`X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Permissions-Policy`, CSP, HSTS in production) and
  `Cache-Control: no-store` on authenticated pages.
- Use a strong `SECRET_KEY` and secure cookies in production; refuse to start
  production with the default key.
- Use Supabase PostgreSQL in every environment except the isolated test suite.
- Use shared rate-limit storage (`RATE_LIMIT_STORAGE_URI`) for multiple
  production instances; the default limit is 300 requests per hour plus per-route
  limits on login and registration.
- Never log secrets, passwords, session values, or database URLs.
- Keep PWA assets complete and consistent: every icon declared in the
  manifest must exist at the declared size, and `<meta name="theme-color">`
  must match `manifest.webmanifest`.
- Regenerate icons with `tools/generate_icons.py`; do not hand-edit PNG binaries.

## Database and storage rules

- Use UTC-aware timestamps.
- Keep database schema changes in migrations once the migration workflow is
  introduced; until then `init_db.py` may only add tables, columns, and indexes
  additively.
- Keep `subjects.slug` and `content.slug` unique.
- Store upload metadata in the database and large objects in persistent object
  storage for production.
- Do not treat Vercel/serverless local disk as durable storage.
- Back up production PostgreSQL before schema changes.

## Definition of done

A change is complete only when:

1. The requirement is documented.
2. Implementation is complete and consistent with existing patterns.
3. Relevant success, empty, validation, denied, and error states are handled.
4. Targeted tests or checks pass (`pytest` for behavior changes).
5. `Task.md` and `Memory.md` reflect the new state.
6. No secrets or runtime data are included in the commit.

## Change record

| Date | Update |
|------|--------|
| 2026-10-03 | Replaced stale Next.js/payment rules with rules for the implemented Flask MVP |
| 2026-10-03 | Added server-side security, storage, migration, and documentation requirements |
| 2026-10-03 | Added sanitizer, upload, file-delivery, redirect, header, caching, and slug rules now enforced in code |
