# ClassNest Task Log

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

## Current priority: production deployment readiness

- [ ] Add and verify an initial Flask-Migrate migration.
- [x] Add Vercel `api/index.py` and `vercel.json` for the selected deployment
      target.
- [ ] Provision managed PostgreSQL and run `python init_db.py`.
- [ ] Replace local uploads with durable object storage.
- [ ] Configure production `SECRET_KEY`, secure cookies, and
      `RATE_LIMIT_STORAGE_URI`.
- [x] Add automated authentication, authorization, CRUD, and upload tests.
- [ ] Run a production smoke test against the deployed URL (`/healthz`).

## Acceptance criteria for the next deployment task

- The application boots from the deployment entry point.
- All required environment variables are configured without secrets in Git.
- Database tables exist in managed PostgreSQL.
- Teacher login and student registration work.
- Teacher content creation and student content reading work.
- Unauthorized role access is rejected.
- Uploaded objects remain available after a new deployment.
- Production logs contain no credentials or sensitive session values.

## Verification commands

### Local smoke check

```powershell
python init_db.py
python -c "from run import app; print(sorted(rule.rule for rule in app.url_map.iter_rules()))"
```

### Automated tests

```powershell
pip install -r requirements-dev.txt
pytest
```

### Git delivery check

```powershell
git status --short --branch
git log -1 --oneline
```

## Change record

| Date | Update |
|------|--------|
| 2026-10-03 | Replaced the old TypeScript foundation task list with the completed Flask implementation log |
| 2026-10-03 | Added GitHub delivery status and production deployment follow-up tasks |
| 2026-10-03 | Added Vercel serverless entry point and deployment configuration |
| 2026-10-03 | Recorded the 77-test suite, dark mode, offline page, health check, files blueprint, security headers, and upload-folder move |
