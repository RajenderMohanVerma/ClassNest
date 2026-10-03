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
- Hash passwords with Werkzeug; never store plaintext passwords.
- Keep CSRF protection enabled for browser form mutations.
- Sanitize user-authored HTML before using the `safe` rendering path.
- Validate both extension and MIME type for uploaded files.
- Generate UUID storage names and never trust user-provided paths.
- Use a strong `SECRET_KEY` and secure cookies in production.
- Use PostgreSQL instead of SQLite in production.
- Use Redis-backed rate limiting for multiple production instances.
- Never log secrets, passwords, session values, or database URLs.

## Database and storage rules

- Use UTC-aware timestamps.
- Keep database schema changes in migrations once the migration workflow is
  introduced.
- Store upload metadata in the database and large objects in persistent object
  storage for production.
- Do not treat Vercel/serverless local disk as durable storage.
- Back up production PostgreSQL before schema changes.

## Definition of done

A change is complete only when:

1. The requirement is documented.
2. Implementation is complete and consistent with existing patterns.
3. Relevant success, empty, validation, denied, and error states are handled.
4. Targeted tests or checks pass.
5. `Task.md` and `Memory.md` reflect the new state.
6. No secrets or runtime data are included in the commit.

## Change record

| Date | Update |
|------|--------|
| 2026-10-03 | Replaced stale Next.js/payment rules with rules for the implemented Flask MVP |
| 2026-10-03 | Added server-side security, storage, migration, and documentation requirements |
