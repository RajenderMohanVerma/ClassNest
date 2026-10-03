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

## What's Inside?

✅ **30+ Templates** — All student & teacher pages  
✅ **Complete Routes** — Auth, content, subjects, announcements, profiles  
✅ **Database Models** — User, Subject, Content, Announcement, UploadedFile  
✅ **Security** — CSRF, rate limiting, password hashing, HTML sanitization  
✅ **PWA Ready** — Service worker, install prompt, offline support  
✅ **Responsive Design** — Mobile, tablet, desktop with design tokens  
✅ **Full Admin** — Teacher dashboard with all CRUD operations  

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
→ Edit `run.py` and change `port=5000` to another number, or kill process on 5000

---

## Documentation

See [README.md](README.md) for complete documentation.

**Happy learning! 🎓**
