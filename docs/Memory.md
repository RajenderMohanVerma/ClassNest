# Memory

## Current project state

- Project: Er. Amit Sir Academy
- Documentation baseline created: 2026-10-03
- Implementation status: Phase 1 foundation scaffold
- Root specification: `PROJECT_MEMORY.md`
- Chosen technology stack: Next.js 15/React 19 web, Fastify 5 API,
  PostgreSQL/Prisma, TypeScript, external storage abstraction, Razorpay
- Execution mode: AUTONOMOUS

## Locked decisions

- Use a statically typed implementation with strict type checking where
  supported.
- Public pages must be server-rendered or statically generated.
- Backend API is versioned at `/api/v1`.
- Authentication uses short-lived access tokens and rotating refresh tokens
  stored in secure cookies; sessions are stored in the database.
- Premium access is granted only by verified payment or an explicit admin grant.
- Premium files require a fresh signed URL after an access check.
- Store currency amounts as INR paise integers.
- Store time in UTC and display it in Asia/Kolkata.
- Never store secrets in source control or documentation.

## Documentation workflow

1. Read `Memory.md`, `PRD.md`, `Architecture.md`, `Design.md`, `Rules.md`,
   and `Task.md` before starting a significant change.
2. Record new decisions and completed work in the relevant document.
3. Keep this file current after every meaningful phase.
4. If a decision conflicts with `PROJECT_MEMORY.md`, stop and get approval
   before changing the locked decision.

## Decision log

| Date | Decision | Reason |
|------|----------|--------|
| 2026-10-03 | Split the master specification into six maintained docs | Make project context easy to find and update |
| 2026-10-03 | Selected Next.js + Fastify + PostgreSQL/Prisma TypeScript monorepo | Meets SSR, separate API, relational DB, and strict typing requirements |

## Known gaps

- Docker is not installed in the current environment, so PostgreSQL container
  health and migrations need to be verified on a machine with Docker.
- Authentication, database schema, and migrations are the next implementation
  work after the foundation scaffold.
