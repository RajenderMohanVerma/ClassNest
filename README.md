# ClassNest: Teacher–Student Learning Portal

A modern, production-ready educational content management system built with Flask, PostgreSQL, and vanilla HTML/CSS/JavaScript. ClassNest enables teachers to create and publish learning materials, manage students, and send announcements, while students can browse content, search, and track their learning journey.

## Features

### 👨‍🏫 Teacher Dashboard
- **Dashboard** — Overview with statistics (total content, published, drafts, subjects, students)
- **Content Management** — Create, edit, publish, preview, and delete learning materials
- **Content Types** — Six types: notes, study material, PDF resources, video lessons, announcements, reference links
- **Subject Management** — Organize content by subjects with custom icons
- **Announcements** — Broadcast messages to all students, with publish/unpublish
- **Student Overview** — View and search registered students
- **File Management** — Review every upload, delete files, clear previews
- **Filters & Pagination** — Search by title/topic/body, filter by status, subject, type; sort newest/oldest/title
- **Profile** — Update personal info and change password

### 👨‍🎓 Student Dashboard
- **Dashboard** — Welcome with recently published content, subject browse, and announcements
- **Subject Browsing** — Browse all available subjects with published lesson counts
- **Content Library** — Published content only, with subject/type filters, per-type counts, and sorting
- **Search** — Full-text search across titles, topics, and body text
- **Content Reading** — Sanitized rich text plus attachments, videos, and external resources
- **Downloads** — Original file names, served only through the authenticated `/files` route
- **Announcements** — Published announcements, newest first
- **Profile** — Update personal info and change password

### 🔒 Security & Access Control
- **Role-Based Access** — Teacher and student roles with proper authorization checks
- **Secure Authentication** — Password hashing with Werkzeug (scrypt), session-based auth, optional "remember me"
- **CSRF Protection** — Token-based CSRF protection on all forms
- **Rate Limiting** — Brute-force protection on login (10/min) and register (5/min), plus a 300/hour global default
- **Input Sanitization** — Bleach allowlist sanitizes all HTML; `script/style/iframe/object/embed/form` content is removed
- **File Upload Security** — Extension allowlist, MIME allowlist, and magic-byte validation; UUID storage outside `app/static`
- **Private File Delivery** — `/files/...` requires login; students get 403 for unpublished content
- **Response Security Headers** — CSP, `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy`, `Permissions-Policy`, HSTS in production
- **No Caching of Private Pages** — `Cache-Control: no-store` on every authenticated page
- **Safe Redirects** — `next` parameters must stay on this site

### 📱 Progressive Web App (PWA)
- **Service Worker** — Cache-first for static assets; HTML is never cached and falls back to `/offline`
- **Install Prompt** — Mobile-only PWA install suggestion with iOS/Android detection and dismissal memory
- **Offline Page** — `/offline` renders a friendly cached fallback when the network is unavailable
- **Responsive Design** — Works seamlessly on desktop, tablet, and mobile

### 🎨 Design System
- **Design Tokens** — CSS variables for colors, typography, spacing, shadows
- **Dark Mode** — Manual light/dark toggle with system preference default and no-flash loading
- **Component Library** — Pre-built UI components (cards, forms, tables, badges, pagination, toasts)
- **Accessibility** — Skip link, `aria-current`/`aria-expanded` state, 40px+ touch targets, `prefers-reduced-motion` support
- **Professional Theme** — Modern, accessible design with proper contrast ratios
- **Customizable** — Easy to rebrand by modifying config and design tokens

### 🧪 Testing
- **77 automated tests** covering auth, roles, CRUD, publication, uploads, search, pagination, and error handling
- **Isolated test database** — in-memory SQLite via `TestingConfig`, never touches Supabase

## Tech Stack

- **Backend**: Flask 3.1 + SQLAlchemy 2.x ORM
- **Database**: Supabase PostgreSQL
- **Frontend**: Vanilla HTML, CSS (custom + Bootstrap Icons), JavaScript
- **Authentication**: Werkzeug password hashing + Flask session
- **Deployment**: Gunicorn (Procfile) or Vercel serverless (`api/index.py` + `vercel.json`)

## Prerequisites

- **Python 3.9+** (Flask 3.1 requirement)
- **Supabase PostgreSQL** (Session Pooler connection recommended for Vercel)
- **pip** (Python package manager)
- **virtualenv** (recommended)

## Installation & Setup

### 1. Clone the Repository

```bash
cd Amit\ Academy
```

### 2. Create and Activate Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
# Copy template
cp .env.example .env
```

Edit `.env`:

```env
# Supabase PostgreSQL connection
DATABASE_URL=postgresql://postgres.project-ref:password@pooler.supabase.com:5432/postgres?sslmode=require

# Flask secret key (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-random-64-char-secret-key

# Upload settings (keep uploads outside app/static)
UPLOAD_FOLDER=instance/uploads
MAX_UPLOAD_MB=16

# Session and rate limiting
SESSION_HOURS=8
RATE_LIMIT_STORAGE_URI=memory://
RATE_LIMIT_DEFAULT=300 per hour

# Branding
APP_NAME=ClassNest
APP_TAGLINE=Teacher & Student Learning Portal

# Flask environment
FLASK_ENV=development
FLASK_DEBUG=true
```

Full list of variables: see [`.env.example`](.env.example).

**Generate a secure SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Set Up Supabase PostgreSQL

Use the Supabase Session Pooler connection URL:

```powershell
$env:DATABASE_URL="postgresql://postgres.project-ref:password@pooler.supabase.com:5432/postgres?sslmode=require"
$env:FLASK_ENV="development"
python init_db.py
```

### 6. Create Teacher Account

Only teachers can be created via CLI (not through public registration):

```bash
python create_teacher.py
# Follow prompts to enter name, email, and password
```

### 7. Run the Application

```bash
python run.py
```

Visit `http://localhost:5000` in your browser.

**Login:**
- **Teacher**: Use credentials from `create_teacher.py`
- **Student**: Register at `/auth/register`

---

## Project Structure

```
Amit Academy/
├── app/
│   ├── __init__.py          # Flask app factory, blueprints, error handlers, healthz
│   ├── config.py            # Dev/production/testing configuration + validation
│   ├── extensions.py        # SQLAlchemy, Flask-Migrate, CSRF, rate limiter
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── subject.py
│   │   ├── content.py
│   │   ├── announcement.py
│   │   └── uploaded_file.py
│   ├── routes/              # Flask blueprints
│   │   ├── public.py        # Landing page, offline page
│   │   ├── auth.py          # Login/Register/Logout (POST logout)
│   │   ├── teacher.py       # Teacher dashboard & features
│   │   ├── student.py       # Student dashboard & features
│   │   ├── files.py         # Authenticated file delivery
│   │   └── api.py           # JSON endpoints
│   ├── services/            # Business logic
│   │   ├── uploads.py       # File validation, UUID storage, deletion
│   │   ├── sanitizer.py     # HTML sanitization
│   │   ├── accounts.py      # Shared profile/password logic
│   │   ├── pagination.py    # Filter-preserving pagination args
│   │   └── decorators.py    # Auth decorators
│   ├── templates/           # Jinja2 templates (36 files)
│   │   ├── base.html
│   │   ├── partials/
│   │   ├── public/
│   │   ├── errors/
│   │   ├── teacher/
│   │   └── student/
│   └── static/              # CSS, JS, icons
│       ├── css/             # Design tokens, components, pages
│       ├── js/              # App logic, theme, PWA install prompt
│       └── icons/           # PWA icons
├── api/index.py             # Vercel serverless entry point
├── tests/                   # Pytest suite (77 tests, SQLite)
├── docs/                    # PRD, architecture, design, task, rules, memory
├── requirements.txt         # Runtime dependencies
├── requirements-dev.txt     # Test/lint dependencies
├── Procfile                 # Gunicorn start command
├── vercel.json              # Vercel build + rewrite rules
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── init_db.py               # Schema init + additive sync + upload migration
├── create_teacher.py       # CLI tool for teacher account creation
├── run.py                  # Application entry point
├── manifest.json           # PWA metadata
└── sw.js                   # Service worker
```

> Uploads are stored in `instance/uploads` (configurable via `UPLOAD_FOLDER`). The old
> `app/static/uploads` folder is only read as a legacy fallback for files created before
> the move, and `/static/uploads/...` always returns 404.

---

## Usage Guide

### For Teachers

1. **Login**: Go to `/auth/login` with teacher credentials
2. **Dashboard**: View statistics and recent activity
3. **Create Content**:
   - Go to "Content" → "New Content"
   - Fill in title, description, select subject and content type
   - Add rich text body content
   - Upload optional attachments
   - Save as draft or publish immediately
4. **Manage Subjects**:
   - Go to "Subjects" to view all subjects
   - Create new subjects or edit existing ones
5. **Send Announcements**:
   - Go to "Announcements" → "New Announcement"
   - Write title and message
   - Publish to make visible to all students
6. **View Students**:
   - Go to "Students" to see list of registered students
7. **Manage Files**:
   - Go to "Files" to view all uploaded attachments
   - Delete files no longer needed

### For Students

1. **Register**: Go to `/auth/register` to create account
2. **Dashboard**: View recent content, subject quick access, and announcements
3. **Browse Content**:
   - "Content Library" — Search and filter by subject/type
   - "Subjects" — Browse by subject
4. **Read Content**:
   - Click any content card to view full details
   - Download attachments if available
5. **Search**:
   - Use dashboard search bar or "Search" page
6. **Announcements**:
   - View all teacher announcements on "Announcements" page
7. **Profile**:
   - Update personal info and password

---

## Database Models

### User
- `id` (Primary Key)
- `email` (Unique)
- `name`
- `password_hash`
- `role` (teacher / student)
- `avatar` (Optional)
- `created_at`, `updated_at` (Timestamps)

### Subject
- `id` (Primary Key)
- `name`
- `slug` (URL-friendly, unique; duplicates get `-2`, `-3`, …)
- `description` (Optional)
- `icon` (Bootstrap icon class)
- `created_by` (Foreign Key → User, required)
- `created_at`, `updated_at`

### Content
- `id` (Primary Key)
- `title`, `slug` (unique), `description`
- `body_html` (Sanitized HTML)
- `content_type` (notes / study_material / pdf_resource / video_lesson / announcement / reference_link)
- `status` (draft / published)
- `subject_id` (Foreign Key → Subject)
- `created_by` (Foreign Key → User)
- `thumbnail`, `attachment`, `video_url`, `resource_url`
- `tags`, `topic` (For search/filtering)
- `created_at`, `published_at`, `updated_at` (Timestamps)

### Announcement
- `id` (Primary Key)
- `title`, `body`
- `is_published` (Boolean)
- `created_by` (Foreign Key → User)
- `created_at`, `published_at`, `updated_at` (Timestamps)

### UploadedFile
- `id` (Primary Key)
- `original_name` (Filename user uploaded)
- `stored_name` (UUID-based storage name, unique)
- `mime_type`
- `size_bytes`
- `uploaded_by` (Foreign Key → User)
- `content_id` (Foreign Key → Content, nullable, cascades on delete)
- `created_at` (Timestamp)

---

## API Endpoints

### Public & App Routes
- `GET /` — Redirects to login (or dashboard if logged in)
- `GET /offline` — Offline fallback page for the service worker
- `GET /healthz` — Deployment smoke test (`{"status","database","app"}`, 200 or 503)
- `GET /manifest.json`, `GET /sw.js` — PWA metadata and service worker
- `GET /auth/login` — Login page
- `POST /auth/login` — Submit login (honours a same-site `next`)
- `GET /auth/register` — Register page
- `POST /auth/register` — Submit registration
- `POST /auth/logout` — Logout (`GET /auth/logout` returns 405)

### Teacher Routes
- `GET /teacher/dashboard` — Dashboard
- `GET /teacher/subjects` — List subjects
- `GET|POST /teacher/subjects/create` — Create subject
- `GET|POST /teacher/subjects/<id>/edit` — Edit subject
- `POST /teacher/subjects/<id>/delete` — Delete subject (only when empty)
- `GET /teacher/content` — List content (supports `q`, `status`, `subject`, `type`, `sort`)
- `GET|POST /teacher/content/create` — Create content
- `GET|POST /teacher/content/<id>/edit` — Edit content
- `GET /teacher/content/<id>/preview` — Preview content
- `POST /teacher/content/<id>/toggle` — Publish/unpublish
- `POST /teacher/content/<id>/delete` — Delete content and its files
- `GET /teacher/announcements` — List announcements
- `GET|POST /teacher/announcements/create` — Create announcement
- `GET|POST /teacher/announcements/<id>/edit` — Edit announcement
- `POST /teacher/announcements/<id>/delete` — Delete announcement
- `GET /teacher/students` — List/search students
- `GET /teacher/files` — List files
- `POST /teacher/files/<id>/delete` — Delete file
- `GET|POST /teacher/profile` — Profile page and updates

### Student Routes
- `GET /student/dashboard` — Dashboard
- `GET /student/subjects` — List subjects
- `GET /student/subjects/<slug>` — Subject detail with content
- `GET /student/content` — Content library (`q`, `subject`, `type`, `sort`)
- `GET /student/content/<slug>` — Read content
- `GET /student/content/<slug>/download` — Download attachment (redirects to `/files`)
- `GET /student/announcements` — List announcements
- `GET /student/search` — Search content
- `GET|POST /student/profile` — Profile page and updates

### File & API Routes
- `GET /files/<stored_name>` — Serve an upload (login required, publication-checked)
- `GET /files/<id>/download` — Download an upload by id
- `GET /api/stats` — Dashboard statistics (JSON, teacher only)
- `GET /api/content-types` — Content type labels (JSON, any signed-in user)

---

## Deployment

### Vercel Deployment

The project is configured for Vercel through `api/index.py` and
`vercel.json`. Flask does not require an `index.html` file: Vercel sends every
request to the Flask application entry point.

1. Push the repository to GitHub.
2. Create a Supabase PostgreSQL database, and copy its complete
   connection URL.
3. Initialize the production schema from a local machine:
   ```powershell
   $env:DATABASE_URL="postgresql://user:password@host/classnest_db?sslmode=require"
   $env:FLASK_ENV="production"
   python init_db.py
   python create_teacher.py
   ```
4. Import `RajenderMohanVerma/ClassNest` into Vercel.
5. Add these Vercel environment variables for the Production environment:
   `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV=production`, `FLASK_DEBUG=0`,
   `APP_NAME`, `APP_TAGLINE`, `SESSION_HOURS`, `MAX_UPLOAD_MB`,
   `RATE_LIMIT_STORAGE_URI`, `RATE_LIMIT_DEFAULT`.
   `UPLOAD_FOLDER` is forced to `/tmp/classnest-uploads` on Vercel, so uploaded
   files are ephemeral — move them to Supabase Storage for persistence.
6. Deploy the `main` branch and test login, registration, teacher CRUD, student
   browsing, search, `/api/stats`, and `/healthz`.

Vercel's local filesystem is not durable. The current local upload folder is
appropriate for development only. Use Vercel Blob, Cloudinary, S3, or
Cloudflare R2 before relying on production uploads. Use Redis-backed storage
for Flask-Limiter when running multiple instances.

### Traditional Production Checklist

1. **Environment Setup**
   ```bash
   export FLASK_ENV=production
   export FLASK_DEBUG=false
   export SECRET_KEY=<random-64-char-key>
   export DATABASE_URL=postgresql://user:pass@host/classnest
   ```

2. **Database Migrations**
   ```bash
   flask db upgrade
   ```

3. **Web Server** — Use Gunicorn with Nginx reverse proxy:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 127.0.0.1:8000 run:app
   ```

4. **Nginx Configuration** (example):
   ```nginx
   server {
       listen 80;
       server_name example.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **SSL/HTTPS** — Required for PWA:
   ```bash
   # Use Let's Encrypt with Certbot
   certbot --nginx -d example.com
   ```

6. **Static Files** — Serve with Nginx:
   ```bash
   python run.py collectstatic  # (if implemented)
   # Or configure Nginx to serve app/static/ directly
   ```

7. **Persistent Storage** — Ensure uploads folder persists across deployments

---

## Security Notes

- **CSRF**: All forms include CSRF tokens; globally enabled via Flask-WTF
- **SQL Injection**: All queries use SQLAlchemy ORM (no string interpolation)
- **XSS**: User HTML is sanitized with Bleach; unsafe elements are removed with their content and inline `style` attributes are stripped
- **Rate Limiting**: Login 10/min, register 5/min, and a 300/hour global default (shared storage via `RATE_LIMIT_STORAGE_URI`)
- **Password Hashing**: Werkzeug's `generate_password_hash` uses salted scrypt
- **Session Cookies**: HTTP-only and SameSite="Lax"; `Secure` in production
- **File Uploads**: Extension, MIME, and magic-byte validation; UUID storage outside `app/static`; served only through `/files` behind a login and publication check
- **Cache Control**: Authenticated pages send `Cache-Control: no-store`
- **Response Headers**: CSP, `X-Frame-Options: DENY`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, and HSTS in production
- **Role-Based Access**: Server-side @teacher_required and @student_required decorators enforce permissions
- **Startup Validation**: Production refuses to boot without a real `SECRET_KEY` and a PostgreSQL `DATABASE_URL`

---

## Testing

```bash
pip install -r requirements-dev.txt
pytest            # 77 tests
pytest -q         # quiet output
```

`TestingConfig` gives each test run an in-memory SQLite database and a temporary
upload directory, so tests never touch the Supabase instance. Rate limiting and
CSRF are disabled there and are verified manually.

---

## Troubleshooting

### Database Connection Error
```
sqlalchemy.exc.ArgumentError: Could not parse rfc1738 URL
```
**Solution**: Check `DATABASE_URL` format in `.env`. Must be:
```
postgresql://username:password@host:5432/dbname
```

### ImportError: No module named 'psycopg2'
**Solution**: Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

### Service Worker Not Registered
**Solution**: PWA requires HTTPS in production. On localhost, it works without HTTPS.

### Upload Size Exceeded
**Solution**: Raise `MAX_UPLOAD_MB` in `.env`; `MAX_CONTENT_LENGTH` is derived from it automatically.

### File returns 404 on `/files/...`
**Solution**: Uploads must live under `UPLOAD_FOLDER`. Run `python init_db.py` once to move
files out of the old `app/static/uploads` folder into the current upload directory.

---

## Development Tips

### Run with Auto-Reload
```bash
export FLASK_ENV=development
export FLASK_DEBUG=true
python run.py
```

### Change the Port
```bash
PORT=8000 python run.py          # Windows PowerShell: $env:PORT=8000
```

### Database Shell
```bash
flask shell
>>> from app import db
>>> from app.models import *
>>> User.query.all()  # List all users
```

### Clear Database (Development Only)
```bash
flask shell
>>> from app import db
>>> db.drop_all()
>>> db.create_all()
```

### Generate Dummy Data (Optional)
Create a `seed.py` script:
```python
from app import create_app, db
from app.models import User, Subject, Content

app = create_app()
with app.app_context():
    teacher = User(name="Teacher", email="teacher@example.com", role="teacher")
    teacher.set_password("teacherpass")
    db.session.add(teacher)
    db.session.commit()

    math = Subject(name="Mathematics", slug="mathematics", icon="bi-calculator", created_by=teacher.id)
    db.session.add(math)
    db.session.commit()

    # ... more content
```

---

## Performance Optimization

- **Database Indexing**: Email, slugs, status, topic, `published_at`, `is_published`, `size_bytes`, `content_id`; unique indexes on `content.slug` and `subjects.slug`
- **Pagination**: Content 12/page, teacher files 20/page, teacher students 20/page, teacher announcements 20/page, student announcements 10/page; filters and sort are preserved across pages
- **Connection Pooling**: `pool_pre_ping` and `pool_recycle=280` keep Supabase connections healthy
- **Caching**: The service worker caches static assets only; HTML is never cached
- **Lazy Loading**: Images use native lazy loading
- **Query Optimization**: Uses SQLAlchemy `.filter()` chains efficiently

---

## Future Enhancements

- [ ] Rich-text editor (TinyMCE / Quill) for content creation
- [ ] Email notifications for announcements
- [ ] Discussion forums or comments on content
- [ ] Student progress tracking and certificates
- [ ] Real-time notifications (WebSockets)
- [ ] Multilingual support (i18n)
- [ ] Content versioning and rollback
- [ ] Advanced analytics and reporting
- [ ] Durable object storage (Supabase Storage) instead of local disk
- [ ] Mobile native app (React Native / Flutter)

---

## License

MIT License. See LICENSE file for details.

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the code comments in key files
3. Inspect browser console (F12) for frontend errors
4. Check Flask logs in terminal for backend errors

---

**Built with ❤️ using Flask, PostgreSQL, and vanilla web technologies**
