# ClassNest — Teacher–Student Learning Portal
## COMPLETE BUILD PROMPT (Modified Edition)

> **Stack:** Flask + PostgreSQL + HTML + CSS + JavaScript
> **Extra requirement:** Mobile "Install the app" popup (PWA) on first open
> **Status:** One self-contained build instruction. Paste the whole file into the builder AI.

---

## HOW TO USE THIS PROMPT (read this first, builder AI)

1. Read this document top to bottom, in order. Do not skip sections.
2. Treat the tech stack in §2 as LOCKED — do not substitute anything.
3. Build the MVP in logical phases (§19). Test every phase (§17) before moving on.
4. The mobile "Install the app" popup (§20) is a launch requirement, not an afterthought — build and test it.
5. Deliver everything listed in §18. No fake functionality, no demo-only UI, no placeholder data presented as real.

## WHAT CHANGED IN THIS MODIFIED EDITION

| # | Change | Reason |
|---|--------|--------|
| 1 | **Tech stack locked: Python Flask (backend), PostgreSQL (database), HTML + CSS + vanilla JavaScript (frontend)** | Human's decision — the original prompt left the stack open |
| 2 | PostgreSQL is used everywhere — schema, initialization, backup and deployment use one managed database | One real database for development and production |
| 3 | **New §20: mobile "Install the app" popup (PWA)** — when a user opens the site on a phone, the first thing they see is an install prompt with proper install/dismiss behavior | New human requirement |
| 4 | All original requirements (roles, pages, dashboards, content system, security, testing, deliverables) kept exactly as-is | Nothing dropped |

---

Act as a senior full-stack developer, UI/UX designer, database architect, and application security engineer.

Build a complete, professional, modern, responsive Teacher–Student Learning Portal. The platform will allow a teacher to publish educational content and students to log in and access that content from their own dashboards.

The website must be production-minded, easy to maintain, visually polished, mobile-friendly, and fully functional. Do not create only a static UI or a demo with fake functionality.

## 1. PROJECT OBJECTIVE

Create a private educational content management platform with exactly two roles:

1. Teacher/Admin
2. Student

The teacher is the administrator who controls educational content. Students can view content that has been published and made available to them.

The project should be suitable for a college/MCA project and should have a professional SaaS-style user experience.

Suggested project name: ClassNest — Teacher & Student Learning Portal.

Keep the project name, logo, and basic branding easy to change (one config file / one settings module — no hard-coded brand strings scattered through templates).

## 2. REQUIRED TECHNOLOGY STACK (LOCKED — do not substitute)

- Backend: Python Flask 3.x (application factory pattern, Blueprints per area: public, auth, teacher, student, api)
- Database: Supabase PostgreSQL — used in development AND production
- Database access: SQLAlchemy 2.x via Flask-SQLAlchemy. All queries go through the ORM — never build SQL by string interpolation. Schema changes only through Flask-Migrate (Alembic) migrations
- Frontend: HTML5, CSS3, vanilla JavaScript (ES6) — NO build step, NO npm, NO frontend framework
- Templates: Flask Jinja2 (server-side rendering), with reusable partials/macros for navigation, sidebar, footer, alerts, cards, forms
- UI framework: Bootstrap 5, customized with original CSS (design tokens in §3 as CSS variables — the site must look custom-designed, not like a stock Bootstrap template)
- Icons: Bootstrap Icons or Lucide
- Typography: Inter or Plus Jakarta Sans
- Authentication: Flask sessions with secure configuration + Werkzeug password hashing
- File uploads: secure Flask upload handling (see §11)
- Charts: Chart.js only where genuinely useful (teacher dashboard stats)
- PWA: Web App Manifest + Service Worker for the mobile install prompt (see §20)

Project structure (clean and organized):

```
classNest/
├── app/
│   ├── __init__.py          # app factory, config, extensions
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # public, auth, teacher, student blueprints
│   ├── services/            # db helpers, upload handling, search
│   ├── templates/           # base, partials/, public/, teacher/, student/, errors/
│   └── static/
│       ├── css/             # tokens.css, components.css, pages.css
│       ├── js/              # app.js, install-prompt.js, sw registration
│       ├── icons/           # pwa icons (192, 512, maskable, apple-touch)
│       └── uploads/         # dev upload dir (gitignored; path from env)
├── migrations/              # Alembic (Flask-Migrate)
├── manifest.json            # PWA manifest
├── sw.js                    # service worker
├── create_teacher.py        # CLI: secure initial teacher account
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── tests/
```

Do not introduce React, Node.js, Firebase, or unnecessary services unless explicitly requested.

## 3. DESIGN DIRECTION

Create a premium, modern academic SaaS interface inspired by high-quality learning management systems and professional admin dashboards.

The website must look custom-designed, not like an unmodified Bootstrap template.

### Color palette

- Primary navy: #172554
- Primary indigo: #4F46E5
- Page background: #F8FAFC
- Card background: #FFFFFF
- Main text: #0F172A
- Secondary text: #64748B
- Success: #10B981
- Warning: #F59E0B
- Error: #EF4444
- Border: #E2E8F0

Use CSS variables for colors, spacing, typography, shadows, radii, and transitions. One tokens file is the single source of truth — no hard-coded color values in component CSS.

### Layout

Desktop:

- Collapsible left sidebar
- Clean top navigation bar
- Main content area with consistent spacing
- Responsive cards and data tables
- Profile menu and notifications area

Mobile:

- Sidebar becomes a drawer or off-canvas menu
- Navigation remains easy to use with one hand
- Cards stack vertically
- Tables become responsive cards or scrollable regions
- Forms use mobile-friendly inputs
- Buttons have comfortable touch targets (min 44px)

### Visual details

- Rounded cards with 14–18px corner radii
- Subtle borders and restrained shadows
- Clear visual hierarchy
- Modern empty states with helpful messages
- Skeleton loading states where asynchronous loading exists
- Toast notifications for success and error feedback
- Confirmation dialogs for destructive actions
- Smooth, subtle transitions lasting approximately 150–250ms
- Accessible focus indicators and reduced-motion support
- Consistent spacing and alignment throughout the application

Avoid excessive gradients, oversized headings, distracting animations, excessive glassmorphism, and unnecessary decorative elements.

## 4. USER ROLES AND PERMISSIONS

### Teacher/Admin

The teacher can:

- Log in securely.
- Access the administrative dashboard.
- Create, edit, preview, publish, unpublish, and delete educational content.
- Create and manage subjects.
- Organize content by subject, topic, and content type.
- Upload permitted educational files.
- Add external video and resource links.
- Create and manage announcements.
- Search and filter content.
- View the published student-facing version of content.
- View basic statistics such as total content items, published items, drafts, and subjects.
- Manage their own profile and change their password.

The teacher/admin role must not be assignable through ordinary public registration.

### Student

The student can:

- Register or log in according to the configured registration policy.
- Access a personal student dashboard.
- View published educational content.
- Browse subjects and topics.
- Search content by title, keyword, subject, and type.
- Read notes and formatted text.
- View or download permitted PDF and document resources.
- Open external educational video links.
- View announcements.
- View recently published resources.
- Manage their profile and change their password.
- Log out securely.

Students must not be able to create, edit, publish, or delete teacher content.

Students must never see draft or unpublished content.

## 5. REQUIRED PAGES

### Public pages

1. Login page
2. Student registration page, if public registration is enabled
3. Forgot-password page only if a genuine recovery workflow is implemented (real token-based reset — do not include a fake one)
4. Access-denied page
5. Custom 404 page
6. Custom 500 error page

The login page should provide clear validation, password visibility toggle, loading feedback, and links to permitted account actions.

### Teacher/Admin pages

1. Admin dashboard
2. Manage all content
3. Create new content
4. Edit content
5. Content preview
6. Manage subjects
7. Manage announcements
8. File/resource management
9. Student account overview, limited to necessary account information
10. Profile and account settings

### Student pages

1. Student dashboard
2. All subjects
3. Subject details
4. Content library
5. Content detail / reading page
6. Announcements
7. My profile
8. Search results
9. Helpful empty states for new accounts or subjects without published content

## 6. TEACHER CONTENT CREATION SYSTEM

This is the core feature of the application.

Build a polished content editor with the following fields:

- Content title
- Short description
- Subject
- Topic or chapter
- Content type
- Formatted text content
- Optional thumbnail or cover image
- Optional PDF or permitted document attachment
- Optional external video URL
- Optional external resource URL
- Tags
- Draft or published status
- Created and updated timestamps

Supported content types should include:

- Notes
- Study material
- PDF/document resources
- Video lessons
- Announcements
- Reference links

Do not require every field for every content type.

### Publishing workflow

1. Teacher creates content.
2. Teacher saves it as a draft or publishes it.
3. Teacher can preview exactly how the content will appear to students.
4. Published content becomes available on the student dashboard.
5. Draft or unpublished content remains hidden from students.
6. Editing published content updates the student-facing version appropriately.
7. Deleting content requires confirmation.

The editor should preserve formatting safely and display clear validation messages.

If rich-text editing is implemented, sanitize the HTML before rendering it (server-side sanitization, e.g., bleach with an allowlist). Never render untrusted user-provided HTML without sanitization.

## 7. DASHBOARD DESIGN

### Teacher dashboard

Create a welcome header with the teacher's name and a prominent "Create Content" button.

Display summary cards for:

- Total content items
- Published content
- Draft content
- Total subjects

Below the summary cards, include:

- Recent content activity
- Recently edited drafts
- Published content list
- Quick actions
- Latest announcements
- Search and filtering controls

Only display meaningful statistics derived from actual database records.

Do not show fake analytics or fabricated activity.

### Student dashboard

Create a welcoming header such as "Welcome back, [Student Name]".

Include:

- Recently published content
- Browse subjects section
- Latest announcements
- Recently added study materials
- Content-type filters
- Search bar
- Quick links to subjects and resources

Use attractive subject cards with a title, short description, and relevant icon or thumbnail.

If there is no published content, show a helpful empty state rather than a broken layout.

## 8. CONTENT READING EXPERIENCE

Create a clean reading interface optimized for learning.

Include:

- Content title
- Subject and topic labels
- Publication date
- Readable text width
- Clear heading hierarchy
- Lists and code blocks where appropriate
- Attached resource section
- Open/download buttons where permitted
- Related resources when available
- Back-to-subject navigation

Use comfortable line height, readable font sizes, and sufficient contrast.

For external video links, validate allowed URL schemes and embed only trusted providers where appropriate.

## 9. DATABASE DESIGN (PostgreSQL)

Create a normalized PostgreSQL schema with tables such as:

- users — id, name, email (UNIQUE), password_hash, role (teacher/student), created_at, updated_at
- subjects — id, name, slug (UNIQUE), description, icon, created_by (FK → users), created_at, updated_at
- content — id, title, slug, description, subject_id (FK → subjects), topic, content_type, body_html (sanitized), thumbnail, attachment, video_url, resource_url, tags, status (draft/published), created_by (FK → users), created_at, updated_at
- announcements — id, title, body, is_published, published_at, created_by (FK → users), created_at, updated_at
- uploaded_files — id, original_name, stored_name (uuid), mime_type, size_bytes, uploaded_by (FK → users), content_id (FK → content, nullable), created_at

Include:

- Primary keys (GENERATED ALWAYS AS IDENTITY)
- Foreign keys with sensible ON DELETE behavior (e.g., RESTRICT/SET NULL — never silently cascade content away)
- Appropriate unique constraints (email, slugs)
- CHECK constraints for status and role values
- TIMESTAMPTZ created/updated timestamps
- Indexes on frequently queried columns: content(subject_id, status, created_at), users(email), content(slug); a GIN full-text index for content search
- Content publication status and subject relationships
- Creator/author relationships

Store passwords as secure hashes (Werkzeug), never as plaintext.

All database access goes through SQLAlchemy — parameterized queries throughout, no raw SQL string interpolation.

Use database transactions for related updates.

Do not create a separate table or field unless it supports a real feature.

Migrations via Flask-Migrate (Alembic): `flask db migrate` / `flask db upgrade`. The initialization/upgrade process must be idempotent and must never erase existing data.

Provide a secure initial teacher account creation process using the `create_teacher.py` CLI command (credentials from environment variables, password entered securely at the prompt). Do not hardcode a production password. Recommend forcing a password change on first login.

## 10. AUTHENTICATION AND SECURITY

Implement real server-side authorization.

Required protections:

- Secure password hashing using Werkzeug (generate_password_hash / check_password_hash)
- Server-side role checks for every protected route (a decorator like @teacher_required / @login_required — never template-only checks)
- Session handling: strong SECRET_KEY from environment variables; SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SECURE=True in production, SESSION_COOKIE_SAMESITE="Lax"; clear and rotate the session at login and logout
- Secure logout that fully invalidates the session
- CSRF protection (Flask-WTF) for all state-changing forms
- Input validation and output escaping (Jinja autoescaping kept on)
- SQL injection prevention (ORM-only queries)
- Secure upload validation (see §11)
- Protection against path traversal
- File size limits
- Safe filenames (uuid-based stored names)
- Appropriate security headers
- Rate limiting / throttling for authentication attempts (Flask-Limiter or equivalent) where feasible
- Secret keys loaded from environment variables
- Production-safe error handling (custom 500 page, no stack traces to users)
- No sensitive information in logs or client-side code

Do not rely on frontend visibility or JavaScript checks for permissions.

A student who manually enters an admin URL must be denied access by the server.

A student must not be able to retrieve unpublished content by changing an ID in the URL.

Teacher/admin registration must not be exposed as an unrestricted public option.

Never commit secrets, passwords, database credentials, or private configuration files to GitHub.

## 11. FILE UPLOADS AND RESOURCE HANDLING

Support appropriate educational file formats, such as PDF and selected document/image types.

Implement:

- File extension and MIME-type validation (check both — never trust the extension alone)
- File size limits (configurable via env, e.g., MAX_UPLOAD_MB)
- Safe filename generation (uuid stored names; original name kept only as metadata)
- Upload error handling with clear user-facing messages
- Duplicate filename protection
- Resource metadata in the uploaded_files table
- Secure access checks before serving private or unpublished resources (students must not download attachments of draft content by guessing URLs)
- Clear upload progress or loading feedback where applicable

Do not trust file extensions alone.

Store uploaded files in a configured directory (UPLOAD_FOLDER from env). For production deployment, use persistent object storage for uploaded files if the application host does not provide persistent local storage.

The database (PostgreSQL) and the upload directory must both live on persistent storage in production — on hosts without persistent disks, use managed PostgreSQL plus object storage.

## 12. SEARCH AND FILTERS

Implement functional server-side search and filters for:

- Content title
- Keywords
- Subject
- Topic
- Content type
- Publication status (for teachers only)

Add sorting by newest and oldest.

Use pagination when content grows beyond a reasonable page size.

Filters must work with actual database data and preserve relevant selections.

## 13. ACCESSIBILITY AND RESPONSIVENESS

Follow good accessibility practices:

- Semantic HTML
- Proper labels for all form controls
- Keyboard-accessible menus and dialogs
- Visible focus indicators
- Accessible error messages
- Sufficient text/background contrast
- Alt text for meaningful images
- Reduced-motion support

Test layouts at approximately 360px, 390px, 768px, 1024px, and 1440px viewport widths.

Ensure no horizontal overflow, clipped dialogs, overlapping buttons, or unreadable tables.

## 14. PERFORMANCE AND CODE QUALITY

- Use reusable Jinja partials for navigation, sidebar, footer, alerts, and common components.
- Keep route handlers, database logic, configuration, and templates organized.
- Use a shared design system (CSS variables in tokens.css) rather than repeated values.
- Minimize unnecessary JavaScript dependencies.
- Optimize images and load only necessary assets.
- Add useful indexes for frequently queried database columns (§9).
- Handle empty results, database errors, missing files, and invalid input gracefully.
- Use clear function names and comments for important logic.
- Avoid duplicated routes and duplicated business logic.

Do not add complicated microservices or unnecessary architecture to this student project.

## 15. MVP SCOPE

The first working version must include:

1. Secure teacher/admin login
2. Student registration and login, according to the selected registration policy
3. Role-based dashboards
4. Subject creation and management
5. Educational content creation and editing
6. Draft and publish workflow
7. Student-only published content browsing
8. PDF/resource upload with validation
9. Search and filters
10. Announcements
11. Profile management
12. Responsive UI
13. Secure logout
14. Custom error pages
15. Database initialization and setup documentation
16. Mobile "Install the app" popup (§20)

Build these features fully before adding advanced features.

## 16. FEATURES OUTSIDE THE MVP

Do not implement these unless the core application is complete and the feature is explicitly requested:

- Live chat
- AI tutor or chatbot
- Online payments
- Video conferencing
- Complex grading and examination engines
- Gamification
- Multi-institution tenancy
- Mobile native applications
- Advanced learning analytics

## 17. TESTING REQUIREMENTS

Verify that:

- Teacher login works.
- Student login works.
- Invalid credentials are rejected.
- Students cannot access admin routes.
- Teachers can create and edit content.
- Drafts remain hidden from students.
- Publishing makes content visible to students.
- Unpublishing hides it again.
- Subject filtering works.
- Search works.
- Valid files upload successfully.
- Invalid or oversized files are rejected.
- Unauthenticated users cannot access protected content.
- Logout invalidates the authenticated session.
- CSRF protection works on applicable forms.
- Responsive layouts remain usable on mobile.
- Errors do not expose secrets or stack traces to users.
- The mobile install popup behaves per §20 on Android (Chrome) and iOS (Safari), and never appears on desktop.

Use automated tests (pytest) for authentication, role permissions, content publication, and critical CRUD operations where feasible. Document manual test results for the install popup on real phones.

## 18. REQUIRED PROJECT DELIVERABLES

Produce:

1. Complete working source code
2. Organized project folder structure (per §2)
3. requirements.txt
4. PostgreSQL schema + Flask-Migrate migrations (no raw dump-and-pray setup)
5. Environment variable example file (.env.example) without real secrets — must include DATABASE_URL, SECRET_KEY, UPLOAD_FOLDER, MAX_UPLOAD_MB
6. .gitignore
7. README.md with setup and run instructions (PostgreSQL setup included)
8. Secure initial teacher account setup instructions (create_teacher.py)
9. Database backup instructions (pg_dump / managed backup)
10. Deployment notes and limitations (persistent storage, HTTPS, env vars)
11. Test instructions and results
12. Screens/pages for both roles
13. PWA assets: manifest.json, sw.js, app icons (192px, 512px, maskable, apple-touch-icon 180px), install-prompt JS

## 19. DEVELOPMENT WORKFLOW

Before changing any existing project:

1. Inspect the current folder structure and existing code.
2. Identify the current framework, routes, templates, assets, and database.
3. Preserve existing working features.
4. Present a concise implementation plan.
5. Implement the MVP in logical phases.
6. Run the application and test the critical flows.
7. Fix errors before declaring completion.
8. Document any incomplete functionality or deployment limitations.

If starting from an empty project, scaffold the application cleanly per §2.

Do not delete existing files, replace working features with mockups, or claim that a feature works without implementing and testing it.

## 20. MOBILE "INSTALL THE APP" POPUP (PWA) — REQUIRED

### Goal

When a user opens the website on a phone, the FIRST thing they see is a popup prompting them to install the app. This must work like a real PWA install flow, not a fake banner.

### 20.1 Make the site installable (PWA basics)

- Serve `manifest.json` from the site root with: name "ClassNest", short_name "ClassNest", start_url "/", scope "/", display "standalone", orientation "portrait", theme_color "#172554", background_color "#F8FAFC", icons 192x192 and 512x512 PNG (maskable purpose included), plus an apple-touch-icon 180x180.
- Every page includes: `<link rel="manifest" href="/manifest.json">`, `<meta name="theme-color" content="#172554">`, apple-touch-icon link, and `apple-mobile-web-app-capable` meta tags.
- Register a service worker (`sw.js`) on every page. It must: precache the app shell (CSS, JS, icons, offline fallback page); use cache-first for static assets and network-first for HTML pages; use versioned cache names; never cache POST/auth responses; handle updates without breaking logged-in pages.
- Production MUST be served over HTTPS — browsers only allow installation on secure origins (localhost is exempt for development).

### 20.2 The popup behavior (the actual requirement)

- Show ONLY on phones: detect via mobile user-agent OR (`pointer: coarse` media query AND viewport width < 768px).
- NEVER show if the app is already installed: check `matchMedia('(display-mode: standalone)').matches` and `navigator.standalone === true` (iOS).
- Timing: on the first page load of the visit, right after the page renders — a modal bottom sheet over a dimmed background, appearing before the user interacts with anything else. Dismissing it reveals the site normally; it must never trap the user.
- Android / Chrome / Edge: intercept the `beforeinstallprompt` event, call `preventDefault()`, store the event. The bottom sheet shows: app icon + "ClassNest", headline "Install the app", one-line benefit ("Faster access — open ClassNest straight from your home screen"), two buttons: [Install] [Not now]. Tapping Install calls the stored prompt and handles the user's choice.
- iPhone / Safari (no `beforeinstallprompt`): the same bottom sheet, but with simple steps instead of an Install button: "Tap Share, then Add to Home Screen, then Add." Detect iOS via user-agent.
- Fallback: if `beforeinstallprompt` never fires on an Android device, still show the sheet with generic instructions ("Open the browser menu, then tap Add to Home screen / Install app").
- Dismissal memory: store the dismissal timestamp in localStorage (`classnest_install_dismissed_at`); do not show the popup again for 7 days. If the user installs the app (`appinstalled` event fires, or the install choice was accepted), store `classnest_installed = "1"` and never show it again.
- Styling: bottom sheet with 18px rounded top corners, slide-up animation ~200ms, close (x) button, matches the §3 design system, and fully respects `prefers-reduced-motion`.

### 20.3 Acceptance for §20

- On a real Android phone (Chrome), first visit: the popup appears before anything else; tapping Install installs the app to the home screen; launching from the home screen opens it standalone (no browser address bar).
- On an iPhone (Safari), first visit: the popup shows the Add-to-Home-Screen steps.
- Dismissing hides it for 7 days; after installing it never appears again; on desktop browsers it never appears at all.
- No console errors; the service worker registers cleanly; Lighthouse PWA "installable" checks pass.

## FINAL ACCEPTANCE CRITERIA

The final application should look like a polished educational SaaS platform, work on mobile and desktop, support exactly two application roles, and allow a teacher to publish educational content that students can securely access.

Opening the site on a phone must first show the "Install the app" popup per §20.

Prioritize professional UI, real functionality, secure role-based access, maintainable code, and a clear MVP over unnecessary features.

**END OF BUILD PROMPT — begin at HOW TO USE THIS PROMPT, step 1.**
