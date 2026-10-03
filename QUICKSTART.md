# ClassNest — Quick Start Guide

Get ClassNest running in 5 minutes.

## 1️⃣ Install Dependencies

```bash
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

## 2️⃣ Set Up Environment

```bash
cp .env.example .env
```

Edit `.env` and set `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy output and paste into `SECRET_KEY=...` in `.env`

Set at least these values in `.env`:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Supabase PostgreSQL (Session Pooler) URL |
| `SECRET_KEY` | Random 64-char session signing key |
| `UPLOAD_FOLDER` | Upload directory — keep it outside `app/static` |
| `SESSION_HOURS` | "Remember me" session lifetime (default 8) |
| `RATE_LIMIT_STORAGE_URI` | `memory://` locally, Redis in production |

## 3️⃣ Initialize Database

Create a Supabase project, copy the PostgreSQL Session Pooler URL, and set it
before initializing the schema:
```powershell
$env:DATABASE_URL="postgresql://postgres.project-ref:password@pooler.supabase.com:5432/postgres?sslmode=require"
$env:FLASK_ENV="development"
python init_db.py
```

## 4️⃣ Create Teacher Account

```bash
python create_teacher.py
# Enter: name, email, password
```

## 5️⃣ Start the Server

```bash
python run.py
```

Visit **http://localhost:5000**

### Login:
- **Email/Password**: Use what you entered in step 4 (teacher)
- **Or register** at `/auth/register` as a student

---

## 6️⃣ Run the Tests (optional)

```bash
pip install -r requirements-dev.txt
pytest
```

77 tests run against an in-memory SQLite database, so nothing touches Supabase.

---

## What's Inside?

✅ **36 Templates** — All student, teacher, error, and offline pages  
✅ **Complete Routes** — Auth, content, subjects, announcements, files, profiles, API  
✅ **Database Models** — User, Subject, Content, Announcement, UploadedFile  
✅ **Security** — CSRF, rate limiting, password hashing, HTML sanitization, upload signature checks, security headers  
✅ **PWA Ready** — Service worker, install prompt, `/offline` fallback page  
✅ **Dark Mode** — Light/dark toggle with system preference default  
✅ **Responsive Design** — Mobile, tablet, desktop with design tokens  
✅ **Full Admin** — Teacher dashboard with all CRUD operations  
✅ **Health Check** — `GET /healthz` verifies database reachability

---

## Next Steps

1. **Create a Subject** → Teacher → Subjects → New Subject
2. **Add Content** → Teacher → Content → New Content
3. **Publish** → Toggle "Publish now" before saving
4. **Post Announcement** → Teacher → Announcements → New Announcement
5. **View as Student** → Logout → Register → Browse Content

---

## Troubleshooting

**`ImportError: No module named 'psycopg2`**
→ Run `pip install -r requirements.txt`

**`sqlalchemy.exc.OperationalError`**
→ Check the Supabase `DATABASE_URL`, password, pooler host, and
`sslmode=require`, then run `python init_db.py` again.

**Port 5000 already in use**  
→ Set another port instead of editing code: `PORT=8000 python run.py`
(PowerShell: `$env:PORT=8000; python run.py`)

**Uploaded file returns 404**
→ Files live in `UPLOAD_FOLDER` (`instance/uploads` by default). Run
`python init_db.py` once to move older files out of `app/static/uploads`.

---

## Documentation

- [README.md](README.md) — complete documentation
- [INDEX.md](INDEX.md) — repository map
- [CHECKLIST.md](CHECKLIST.md) — build and verification status
- [docs/](docs/) — PRD, architecture, design, task, rules, memory

**Happy learning! 🎓**
