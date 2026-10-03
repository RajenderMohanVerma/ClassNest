# Rules

## Documentation rules

- These six files are required project documentation:
  `Architecture.md`, `Design.md`, `Memory.md`, `PRD.md`, `Rules.md`, and
  `Task.md`.
- Update the relevant documentation in the same change as the implementation.
- Do not silently overwrite a locked decision; record a decision and request
  approval when a change is needed.

## Engineering rules

- Preserve type safety and use strict validation.
- Follow existing naming, formatting, and component patterns.
- Prefer shared helpers and components over duplicate logic.
- Do not hide errors with broad catches, silent fallbacks, or fake success
  responses.
- Keep changes focused and test behavior that was changed.
- Never commit secrets, real credentials, or private keys.

## Security rules

- Never trust client-side authorization or payment state.
- Never put access or refresh tokens in local storage.
- Never construct SQL using string interpolation.
- Validate and authorize every API mutation on the server.
- Verify payment signatures and make webhook handling idempotent.
- Generate signed premium URLs only after a current access check.
- Log security-relevant events without logging secrets or sensitive tokens.

## Product rules

- Enrollment is created only after verified payment or an explicit admin
  grant.
- Premium content remains discoverable but not readable without access.
- Money uses integer paise; time is stored in UTC.
- Content visibility and scheduled publishing are server-enforced.
- Admin-only routes and actions require the ADMIN role.

## Definition of done

A change is done only when its requirements are documented, implementation is
complete, relevant states and errors are handled, tests or checks pass, and
`Task.md` and `Memory.md` reflect the new state.

