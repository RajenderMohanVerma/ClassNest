# 📚 ClassNest Project Index

## 🎯 Quick Navigation

### I want to...

#### 🚀 Get Started NOW
→ Open **[QUICKSTART.md](QUICKSTART.md)** (5 min read)
- Installation and database setup
- Creating the first teacher account
- Local smoke test

#### ⏱️ Understand the Build (5 minutes)
→ Open **[QUICKSTART.md](QUICKSTART.md)** (5 min read)
- Installation steps
- Creating test accounts
- Verifying everything works
- Basic feature walkthrough

#### 📖 Learn Everything (30 minutes)
→ Open **[README.md](README.md)** (comprehensive guide)
- Complete API documentation
- Database schema details
- Deployment instructions
- Production checklist
- Troubleshooting guide
- Security best practices

#### 🔧 Understand the Architecture
→ Open **[BUILD_SUMMARY.md](BUILD_SUMMARY.md)** (technical deep-dive)
- Project structure overview
- Design decisions explained
- Security implementation details
- Database and ORM details
- Files and their purposes
- What was built and why

#### ✅ Verify Everything Works
→ Open **[CHECKLIST.md](CHECKLIST.md)** (verification guide)
- All 20 build prompt sections verified
- File-by-file checklist
- Security features inventory
- Design system verification
- PWA features checklist
- Testing recommendations
- Deployment readiness checklist

---

## 📂 Directory Structure

```
ClassNest/
├── 📄 Documentation
│   ├── QUICKSTART.md          ← 5-minute setup guide
│   ├── README.md              ← Complete documentation
│   ├── BUILD_SUMMARY.md       ← Technical architecture
│   └── CHECKLIST.md           ← Verification checklist
│
├── 🚀 Entry Points
│   ├── run.py                 ← Start the app (python run.py)
│   ├── init_db.py             ← Initialize database
│   └── create_teacher.py      ← Create teacher account
│
├── ☁️ Vercel Deployment
│   ├── api/index.py           ← Flask serverless entry point
│   └── vercel.json            ← Vercel routing/build configuration
│
├── ⚙️ Configuration
│   ├── requirements.txt        ← Python dependencies
│   ├── .env.example           ← Environment template
│   ├── .gitignore             ← Git exclusions
│   └── manifest.json          ← PWA manifest
│
├── 🎮 Application (app/)
│   ├── __init__.py            ← App factory, blueprints
│   ├── config.py              ← Configuration management
│   ├── extensions.py          ← Database & auth setup
│   │
│   ├── models/                ← Database models
│   │   ├── user.py            ← User accounts (teacher/student)
│   │   ├── subject.py         ← Topics/classes
│   │   ├── content.py         ← Learning materials
│   │   ├── announcement.py    ← News & updates
│   │   └── uploaded_file.py   ← Attachments & resources
│   │
│   ├── routes/                ← API endpoints (40 routes)
│   │   ├── public.py          ← Public pages + offline page (2 routes)
│   │   ├── auth.py            ← Login/register/logout (3 routes)
│   │   ├── teacher.py         ← Teacher dashboard (19 routes)
│   │   ├── student.py         ← Student portal (9 routes)
│   │   ├── files.py           ← Authenticated file delivery (2 routes)
│   │   └── api.py             ← JSON endpoints (2 routes)
│   │
│   ├── services/              ← Business logic
│   │   ├── decorators.py      ← Auth decorators (@teacher_required, etc)
│   │   ├── uploads.py         ← File validation, UUID storage, deletion
│   │   ├── sanitizer.py       ← HTML sanitization
│   │   ├── accounts.py        ← Shared profile/password updates
│   │   └── pagination.py      ← Filter-preserving pagination args
│   │
│   ├── templates/             ← Jinja2 HTML (36 files)
│   │   ├── base.html          ← Master template
│   │   ├── partials/          ← Reusable components
│   │   │   ├── alerts.html
│   │   │   ├── teacher_sidebar.html
│   │   │   ├── student_sidebar.html
│   │   │   ├── topbar.html
│   │   │   ├── content_card.html
│   │   │   └── pagination.html
│   │   ├── public/            ← Public pages
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── offline.html
│   │   ├── errors/            ← Error pages
│   │   │   ├── error.html     ← Shared error shell
│   │   │   ├── 400.html
│   │   │   ├── 403.html
│   │   │   ├── 404.html
│   │   │   ├── 413.html
│   │   │   ├── 429.html
│   │   │   └── 500.html
│   │   ├── teacher/           ← Teacher pages (11 files)
│   │   │   ├── dashboard.html
│   │   │   ├── subjects.html
│   │   │   ├── subject_form.html
│   │   │   ├── content_list.html
│   │   │   ├── content_form.html
│   │   │   ├── content_preview.html
│   │   │   ├── announcements.html
│   │   │   ├── announcement_form.html
│   │   │   ├── students.html
│   │   │   ├── files.html
│   │   │   └── profile.html
│   │   └── student/           ← Student pages (8 files)
│   │       ├── dashboard.html
│   │       ├── subjects.html
│   │       ├── subject_detail.html
│   │       ├── content_library.html
│   │       ├── content_detail.html
│   │       ├── announcements.html
│   │       ├── search.html
│   │       └── profile.html
│   │
│   └── static/                ← CSS, JS, icons
│       ├── css/
│       │   ├── tokens.css     ← Design tokens (light + dark themes)
│       │   ├── components.css ← UI library (20+ components)
│       │   └── pages.css      ← Page-specific styles
│       ├── js/
│       │   ├── app.js         ← App logic & interactivity
│       │   ├── theme.js       ← Dark-mode bootstrap
│       │   └── install-prompt.js ← PWA install handler
│       └── icons/             ← PWA icons
│           ├── icon-192.png
│           ├── icon-512.png
│           └── apple-touch-icon.png
│
├── 🧪 tests/                  ← Pytest suite (77 tests, SQLite)
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_teacher.py
│   └── test_student.py
│
└── 📊 Project Files
    └── instance/uploads/      ← Upload directory (outside app/static)
```

---

## 🎯 Use Cases

### Use Case 1: "I just cloned the repo"
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Run the 5 commands
3. Start building!

### Use Case 2: "I need to understand what was built"
1. Read [QUICKSTART.md](QUICKSTART.md) (understand features)
2. Read [BUILD_SUMMARY.md](BUILD_SUMMARY.md) (understand architecture)
3. Review [README.md](README.md) (detailed reference)

### Use Case 3: "I need to deploy this"
1. Read [README.md](README.md) → Deployment section
2. Check [CHECKLIST.md](CHECKLIST.md) → Pre-Launch section
3. Follow platform-specific instructions (Heroku, PythonAnywhere, etc.)

### Use Case 4: "I want to customize it"
1. Design changes: Edit `app/static/css/tokens.css`
2. Layout changes: Edit `app/templates/base.html` and sidebar files
3. Feature changes: Edit `app/routes/` and `app/models/`
4. Content changes: Edit specific template files in `app/templates/`

### Use Case 5: "Something isn't working"
1. Check [QUICKSTART.md](QUICKSTART.md) → Setup steps
2. Check [README.md](README.md) → Troubleshooting section
3. Verify database: Run `python init_db.py` again
4. Check logs: Look at Flask console output for errors

---

## 📊 Key Files Explained

### Critical Entry Points
| File | Purpose | Run With |
|------|---------|----------|
| `run.py` | Start the Flask app | `python run.py` |
| `init_db.py` | Initialize Supabase PostgreSQL tables | `python init_db.py` |
| `create_teacher.py` | Create teacher accounts | `python create_teacher.py` |
| `api/index.py` | Vercel Flask entry point | Used by Vercel |

### Configuration
| File | Purpose |
|------|---------|
| `requirements.txt` | Python package dependencies (pip install) |
| `requirements-dev.txt` | Test dependencies (pytest) |
| `.env.example` | Template for environment variables (copy to `.env`) |
| `app/config.py` | Flask configuration (dev vs prod vs testing) |
| `vercel.json` | Vercel build and route configuration |
| `Procfile` | Gunicorn start command for hosts that use it |

### Application Core
| File | Purpose | Key Sections |
|------|---------|-------------|
| `app/__init__.py` | Flask app factory | Blueprint registration, error handlers, `/healthz`, security headers |
| `app/extensions.py` | Database & auth initialization | SQLAlchemy, CSRF, Rate limiter |
| `app/models/*` | SQLAlchemy ORM models | User, Subject, Content, Announcement, File |
| `app/routes/*` | API endpoints (40 routes) | Public, Auth, Teacher, Student, Files, API |
| `app/services/*` | Business logic | Auth decorators, file validation, sanitization, accounts, pagination |
| `tests/*` | Automated tests (77) | Auth, roles, CRUD, uploads, search, pagination, errors |

### Frontend
| File | Purpose |
|------|---------|
| `app/templates/base.html` | Master HTML template (inherited by all pages) |
| `app/templates/public/*` | Login, registration, and offline pages |
| `app/templates/teacher/*` | All teacher-facing pages |
| `app/templates/student/*` | All student-facing pages |
| `app/templates/errors/*` | 400 / 403 / 404 / 413 / 429 / 500 pages |
| `app/static/css/*.css` | Styling (design tokens, components, pages) |
| `app/static/js/*.js` | Client-side logic (app shell, theme, install prompt) |
| `manifest.json` | PWA configuration |
| `sw.js` | Service worker served from the application root |

---

## 🔄 Common Workflows

### Starting the App
```bash
# 1. Install dependencies (first time only)
pip install -r requirements.txt

# 2. Initialize database (first time only)
python init_db.py

# 3. Create teacher account (first time only)
python create_teacher.py

# 4. Start the server (every time)
python run.py

# 5. Open browser
http://localhost:5000
```

### Adding a New Feature
```bash
# 1. Create model (if needed)
vim app/models/mynew.py

# 2. Create route
vim app/routes/teacher.py  # or student.py

# 3. Create template
vim app/templates/teacher/mynew.html  # or student/

# 4. Test
# Restart the app and test in browser
```

### Deploying to Production
```bash
# 1. Update environment
cp .env.example .env
# Edit .env with production values

# 2. Install production dependencies
pip install -r requirements.txt
pip install gunicorn

# 3. Initialize database
python init_db.py

# 4. Create admin account
python create_teacher.py

# 5. Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Deploying to Vercel

This is a Flask serverless deployment; an `index.html` file is not required.
Vercel routes all requests to `api/index.py`, which exposes the Flask app.

1. Create a managed PostgreSQL database using Supabase.
2. Run `python init_db.py` once with the production `DATABASE_URL`.
3. Run `python create_teacher.py` once with the same database URL.
   `APP_NAME`, `APP_TAGLINE`, `SESSION_HOURS`, `MAX_UPLOAD_MB`, `RATE_LIMIT_STORAGE_URI`, and `RATE_LIMIT_DEFAULT` as Vercel environment variables.
5. Add `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV=production`, `FLASK_DEBUG=0`,
   `APP_NAME`, `APP_TAGLINE`, and `MAX_UPLOAD_MB` as Vercel environment variables.
6. Deploy from the `main` branch.

Local upload staging files are ignored and must not be used as durable
production storage. Move uploads to Supabase Storage before enabling deployed
file uploads.

---

## 🔐 Security Reminders

Before going to production:
- ✅ Change `SECRET_KEY` in `.env`
- ✅ Set `FLASK_ENV=production`
- ✅ Enable HTTPS (Let's Encrypt)
- ✅ Use Supabase PostgreSQL
- ✅ Review `.env` file (never commit secrets)
- ✅ Set up Redis for rate limiting
- ✅ Monitor error logs
- ✅ Regular backups

---

## 📞 Support & Resources

### Documentation
- [QUICKSTART.md](QUICKSTART.md) - Setup walkthrough
- [README.md](README.md) - Complete guide
- [BUILD_SUMMARY.md](BUILD_SUMMARY.md) - Technical details
- [CHECKLIST.md](CHECKLIST.md) - Verification

### External Resources
- Flask: https://flask.palletsprojects.com
- SQLAlchemy: https://www.sqlalchemy.org
- Jinja2: https://jinja.palletsprojects.com
- PWA: https://web.dev/progressive-web-apps/

### Troubleshooting
1. Check [README.md → Troubleshooting](README.md#troubleshooting)
2. Check [docs/Rules.md](docs/Rules.md) for project rules and review [docs/Memory.md](docs/Memory.md)
3. Review error message in Flask console
4. Check database connection and initialization

---

## ✅ Verification Checklist

Before considering the project complete:
- [ ] Read QUICKSTART.md
- [ ] Run `pip install -r requirements.txt`
- [ ] Run `python init_db.py`
- [ ] Run `python create_teacher.py`
- [ ] Run `python run.py`
- [ ] Open http://localhost:5000
- [ ] Login as teacher
- [ ] Create a subject
- [ ] Create content
- [ ] Log out and register as student
- [ ] Browse teacher's content
- [ ] Verify search works
- [ ] Try mobile view (F12 → responsive design mode)
- [ ] Test on actual mobile if possible

---

## 📈 Project Stats

| Metric | Value |
|--------|-------|
| Python Files | 22 |
| Jinja2 Templates | 36 |
| Project Files (tracked) | 90 |
| Database Tables | 5 |
| API Routes | 40 |
| CSS Components | 20+ |
| Automated Tests | 77 |
| Status | ✅ Production-Ready |

---

## 🎓 What's Implemented

### Sections from Build Prompt
✅ All 20 sections fully implemented:
- Overview, Scope, Design System, Features
- Teacher Flow, Content Management, Student Flow
- Advanced Features, Database, Authentication
- Content Management, Announcements, Components
- Layout, Responsive Design, Navigation
- Forms & Validation, Error Handling, Accessibility
- PWA Features

### Teacher Features
✅ Dashboard with statistics  
✅ Create/edit/delete subjects  
✅ Create/publish/draft content with unique slugs  
✅ Filter, sort, and paginate content lists  
✅ Post announcements with publish/unpublish  
✅ Search enrolled students  
✅ Upload files & resources with signature validation  
✅ Profile settings & password change  

### Student Features
✅ Dashboard with recommendations  
✅ Browse subjects & content  
✅ Read sanitized content  
✅ Download resources through the authenticated `/files` route  
✅ Search across titles, topics, and body text  
✅ Filter by subject & type, sort by newest/oldest/title  
✅ View announcements  
✅ Profile settings  

### Technical Features
✅ Responsive design (mobile to desktop)  
✅ Dark mode toggle with system preference  
✅ Progressive Web App (offline fallback, installable)  
✅ CSRF protection  
✅ Password hashing (scrypt)  
✅ Rate limiting (login, register, global default)  
✅ HTML sanitization  
✅ Three-layer file upload validation  
✅ Role-based access control  
✅ Security headers, CSP, and `no-store` on private pages  
✅ Error handling (400, 403, 404, 413, 429, 500)  
✅ Accessibility (semantic HTML, focus states, skip link, reduced motion)  
✅ Health check endpoint (`/healthz`)  
✅ Automated test suite (77 tests)  

---

## 🚀 Next Steps

1. **Read** [QUICKSTART.md](QUICKSTART.md)
2. **Run** the 5 setup commands
3. **Explore** the application
4. **Read** [README.md](README.md) for complete documentation
5. **Deploy** when ready (see README → Deployment)

---

**Everything is ready to go. Pick a document above and get started!** 🎉
