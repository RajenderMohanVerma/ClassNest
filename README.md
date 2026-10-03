# ClassNest: Teacher–Student Learning Portal

A modern, production-ready educational content management system built with Flask, PostgreSQL, and vanilla HTML/CSS/JavaScript. ClassNest enables teachers to create and publish learning materials, manage students, and send announcements, while students can browse content, search, and track their learning journey.

## Features

### 👨‍🏫 Teacher Dashboard
- **Dashboard** — Overview with statistics (total content, published, drafts, subjects, students)
- **Content Management** — Create, edit, publish, preview, and delete learning materials
- **Content Types** — Notes, video lessons, PDF resources with rich text editing
- **Subject Management** — Organize content by subjects with custom icons
- **Announcements** — Broadcast messages to all students
- **Student Overview** — View registered students and their information
- **File Management** — Upload and manage attachment files
- **Profile** — Update personal info and change password

### 👨‍🎓 Student Dashboard
- **Dashboard** — Welcome with recently published content, subject browse, and announcements
- **Subject Browsing** — Browse all available subjects with lesson counts
- **Content Library** — View all published content with filtering by subject and type
- **Search** — Full-text search across content titles, descriptions, and tags
- **Content Reading** — Read content with support for embedded attachments, videos, and external resources
- **Announcements** — View all published announcements
- **Profile** — Update personal info and change password

### 🔒 Security & Access Control
- **Role-Based Access** — Teacher and student roles with proper authorization checks
- **Secure Authentication** — Password hashing with bcrypt, session-based auth
- **CSRF Protection** — Token-based CSRF protection on all forms
- **Rate Limiting** — Brute-force protection on login/register (10/1min, 5/1min)
- **Input Sanitization** — Bleach library sanitizes all HTML content
- **File Upload Security** — MIME type validation, safe storage with UUIDs

### 📱 Progressive Web App (PWA)
- **Service Worker** — Cache-first for static assets, network-first for HTML
- **Install Prompt** — Mobile-only PWA install suggestion with iOS/Android detection
- **Responsive Design** — Works seamlessly on desktop, tablet, and mobile

### 🎨 Design System
- **Design Tokens** — CSS variables for colors, typography, spacing, shadows
- **Component Library** — Pre-built UI components (cards, forms, tables, badges)
- **Professional Theme** — Modern, accessible design with proper contrast ratios
- **Customizable** — Easy to rebrand by modifying config and design tokens

## Tech Stack

- **Backend**: Flask 3.1 + SQLAlchemy 2.x ORM
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: Vanilla HTML, CSS (custom + Bootstrap Icons), JavaScript
- **Authentication**: Werkzeug password hashing + Flask session
- **Deployment**: Gunicorn + Nginx (recommended)

## Prerequisites

- **Python 3.8+**
- **PostgreSQL 12+** (for production; SQLite for local development)
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
# Database connection (PostgreSQL in production)
DATABASE_URL=postgresql://username:password@localhost/classnest

# Flask secret key (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-random-64-char-secret-key

# Upload settings
UPLOAD_FOLDER=app/static/uploads
MAX_UPLOAD_MB=16

# Branding
APP_NAME=ClassNest
APP_TAGLINE=Learn Together

# Flask environment
FLASK_ENV=development
FLASK_DEBUG=true
```

**Generate a secure SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Set Up Database

```bash
# Create PostgreSQL database
createdb classnest

# Initialize Flask-Migrate and run migrations
flask db upgrade

# Or create tables directly (if no migrations exist)
flask shell
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
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
│   ├── __init__.py          # Flask app factory, blueprints, error handlers
│   ├── config.py            # Configuration for dev/production
│   ├── extensions.py        # SQLAlchemy, Flask-Migrate, etc.
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── subject.py
│   │   ├── content.py
│   │   ├── announcement.py
│   │   └── uploaded_file.py
│   ├── routes/              # Flask blueprints
│   │   ├── public.py        # Public pages
│   │   ├── auth.py          # Login/Register/Logout
│   │   ├── teacher.py       # Teacher dashboard & features
│   │   ├── student.py       # Student dashboard & features
│   │   └── api.py           # API endpoints
│   ├── services/            # Business logic
│   │   ├── uploads.py       # File upload handling
│   │   ├── sanitizer.py     # HTML sanitization
│   │   └── decorators.py    # Auth decorators
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html
│   │   ├── partials/
│   │   ├── public/
│   │   ├── errors/
│   │   ├── teacher/
│   │   └── student/
│   └── static/              # CSS, JS, icons
│       ├── css/             # Design tokens, components, pages
│       ├── js/              # App logic, PWA install prompt
│       ├── uploads/         # User-uploaded files
│       └── icons/           # PWA icons
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── create_teacher.py       # CLI tool for teacher account creation
├── run.py                  # Application entry point
├── manifest.json           # PWA metadata
└── sw.js                   # Service worker
```

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
- `created_at`, `updated_at` (Timestamps)

### Subject
- `id` (Primary Key)
- `name` (Unique)
- `slug` (URL-friendly, auto-generated)
- `description` (Optional)
- `icon` (Bootstrap icon class)
- `created_at`, `updated_at`

### Content
- `id` (Primary Key)
- `title`, `slug`, `description`
- `body_html` (Sanitized HTML)
- `content_type` (notes / video_lesson / pdf_resource)
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
- `created_at`, `published_at` (Timestamps)

### UploadedFile
- `id` (Primary Key)
- `original_name` (Filename user uploaded)
- `stored_name` (UUID-based storage name)
- `mime_type`
- `size_bytes`
- `created_at` (Timestamp)

---

## API Endpoints

### Public Routes
- `GET /` — Redirects to login (or dashboard if logged in)
- `GET /auth/login` — Login page
- `POST /auth/login` — Submit login
- `GET /auth/register` — Register page
- `POST /auth/register` — Submit registration
- `POST /auth/logout` — Logout

### Teacher Routes
- `GET /teacher/dashboard` — Dashboard
- `GET /teacher/subjects` — List subjects
- `POST /teacher/subjects` — Create subject
- `GET /teacher/subjects/<id>/edit` — Edit subject
- `POST /teacher/subjects/<id>/edit` — Update subject
- `GET /teacher/content` — List content
- `GET /teacher/content/create` — Create content form
- `POST /teacher/content/create` — Create content
- `GET /teacher/content/<id>/edit` — Edit content
- `POST /teacher/content/<id>/edit` — Update content
- `GET /teacher/content/<id>/preview` — Preview content
- `POST /teacher/content/<id>/toggle` — Publish/unpublish
- `POST /teacher/content/<id>/delete` — Delete content
- `GET /teacher/announcements` — List announcements
- `GET /teacher/announcements/create` — Create announcement
- `POST /teacher/announcements/create` — Create announcement
- `GET /teacher/announcements/<id>/edit` — Edit announcement
- `POST /teacher/announcements/<id>/edit` — Update announcement
- `POST /teacher/announcements/<id>/delete` — Delete announcement
- `GET /teacher/students` — List students
- `GET /teacher/files` — List files
- `POST /teacher/files/<id>/delete` — Delete file
- `GET /teacher/profile` — Profile page
- `POST /teacher/profile` — Update profile/password

### Student Routes
- `GET /student/dashboard` — Dashboard
- `GET /student/subjects` — List subjects
- `GET /student/subjects/<slug>` — Subject detail with content
- `GET /student/content` — Content library
- `GET /student/content/<slug>` — Read content
- `GET /student/content/<slug>/download` — Download attachment
- `GET /student/announcements` — List announcements
- `GET /student/search` — Search content
- `GET /student/profile` — Profile page
- `POST /student/profile` — Update profile/password

### API Routes
- `GET /api/stats` — Dashboard statistics (JSON)

---

## Deployment

### Vercel Deployment

The project is configured for Vercel through `api/index.py` and
`vercel.json`. Flask does not require an `index.html` file: Vercel sends every
request to the Flask application entry point.

1. Push the repository to GitHub.
2. Create a managed PostgreSQL database, such as Neon, and copy its complete
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
   `APP_NAME`, `APP_TAGLINE`, and `MAX_UPLOAD_MB`.
6. Deploy the `main` branch and test login, registration, teacher CRUD, student
   browsing, search, and `/api/stats`.

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
- **XSS**: All user HTML content is sanitized with Bleach
- **Rate Limiting**: Login/register endpoints limited to 10 and 5 attempts per minute
- **Password Hashing**: Werkzeug's `generate_password_hash` uses bcrypt with salt
- **Session Cookies**: Set to HTTP-only and SameSite="Lax" for production HTTPS
- **File Uploads**: MIME type validation, UUID storage, no direct execution
- **Role-Based Access**: Server-side @teacher_required and @student_required decorators enforce permissions

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
**Solution**: Increase `MAX_CONTENT_LENGTH` in config.py and `MAX_UPLOAD_MB` in `.env`

---

## Development Tips

### Run with Auto-Reload
```bash
export FLASK_ENV=development
export FLASK_DEBUG=true
python run.py
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
    # Create subjects
    math = Subject(name="Mathematics", slug="mathematics", icon="bi-calculator")
    db.session.add_all([math])
    db.session.commit()
    
    # Create content
    # ... etc
```

---

## Performance Optimization

- **Database Indexing**: Configured on common query fields (email, slug, status)
- **Pagination**: Content lists paginated at 12-20 items per page
- **Caching**: Service worker caches static assets (CSS, JS, icons)
- **Lazy Loading**: Images use lazy-load technique in newer browsers
- **Query Optimization**: Uses SQLAlchemy `.filter()` chains efficiently

---

## Future Enhancements

- [ ] Rich-text editor (TinyMCE / Quill) for content creation
- [ ] Email notifications for announcements
- [ ] Discussion forums or comments on content
- [ ] Student progress tracking and certificates
- [ ] Real-time notifications (WebSockets)
- [ ] Dark mode toggle
- [ ] Multilingual support (i18n)
- [ ] Content versioning and rollback
- [ ] Advanced analytics and reporting
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
