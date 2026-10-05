# MASTER PROMPT
# CLASSNEXT
## Complete Professional Educational Platform — A to Z

You are a senior software engineer, UI/UX designer, product architect, database architect, security engineer and deployment engineer.

Upgrade my **existing ClassNext website** into a complete, professional, responsive and production-ready educational learning platform.

# CLASSNEXT

### Tagline
**Learn • Practice • Achieve**

### Teacher
**Er. Amit Sir**

ClassNext is an educational platform for students studying in Classes 8 to 12.

The teacher/admin must be able to manage classes, subjects, chapters, playlists, courses, videos, notes, PDFs, audio, images, notices, assignments, students, permissions, free/premium content and website settings from a secure Admin Dashboard.

Students must be able to register, log in, access authorized content, watch videos, read notes, listen to audio, follow courses/playlists, track learning progress, bookmark content and purchase premium courses.

The final result must be a **real working website**, not a static mockup.

---

# 1. VERY IMPORTANT — EXISTING PROJECT

This is an **EXISTING CLASSNEXT PROJECT**.

Do not rebuild the application from scratch unless there is a genuine technical reason.

First inspect the complete existing project.

Before modifying anything:

1. Inspect the complete folder structure.
2. Inspect the existing application architecture.
3. Inspect the current database structure and existing records.
4. Inspect existing authentication.
5. Inspect existing pages and routes.
6. Inspect existing APIs and backend logic.
7. Inspect reusable components.
8. Inspect existing ClassNext branding.
9. Inspect the current Header and Footer.
10. Inspect current responsive behavior.
11. Inspect existing uploaded files and media.
12. Identify incomplete features.
13. Identify broken links.
14. Identify duplicate code.
15. Identify security problems.
16. Identify missing functionality.
17. Identify existing migrations and stored data.

### EXISTING TECHNOLOGY RULE

**Use the existing technology, framework, architecture and dependencies already present in the project.**

Do not introduce a completely different technology stack.

Do not migrate the project to another framework just for preference.

Do not replace working architecture without a strong technical reason.

Do not unnecessarily install new technologies when the existing project can handle the requirement.

Preserve and extend the current project.

---

# 2. PRESERVE EXISTING PROJECT

Preserve:

- Existing working authentication
- Existing database data
- Existing routes where possible
- Existing useful components
- Existing media/files
- Existing branding assets
- Existing working features
- Existing configuration
- Existing user accounts

Never:

- Delete production data
- Replace the database with a blank database
- Remove working functionality without reason
- Overwrite existing credentials
- Break existing authentication
- Break existing routes unnecessarily

If a database change is required, use a safe migration strategy and preserve existing data.

---

# 3. BRANDING

The official website/product name is:

# CLASSNEXT

Use **ClassNext** consistently throughout the website.

Teacher identity:

# Er. Amit Sir

Do NOT use **Er. Amit Sir Academy** as the website's primary name.

Correct branding:

```text
CLASSNEXT

Learn • Practice • Achieve

Teacher:
Er. Amit Sir
```

Use ClassNext in:

- Logo
- Header
- Footer
- Browser title
- Favicon
- Login
- Registration
- Student Dashboard
- Admin Dashboard
- Notifications
- Emails
- Receipts
- Public pages
- Social sharing
- Website settings

Use **Er. Amit Sir** for teacher/instructor content.

Do not invent:

- Qualifications
- Awards
- Achievements
- Experience
- Student count
- Testimonials
- Reviews

Only show teacher information entered by Admin.

---

# 4. DESIGN REFERENCE

Use the previously provided 21st.dev Creative Tim blog-page reference as **visual inspiration only**.

Use its general design language:

- Spacious sections
- Clean layout
- Modern hero
- Category navigation
- Large content cards
- Image-led sections
- Strong typography
- Clean footer
- Responsive layout
- Smooth interactions

Do NOT:

- Clone the website
- Copy source code
- Copy branding
- Copy exact layout
- Reproduce copyrighted assets

Create an original design specifically for ClassNext.

The final UI must feel like a professional educational platform, not a blog copy.

---

# 5. VISUAL STYLE

ClassNext should feel:

- Professional
- Modern
- Premium
- Academic
- Student-friendly
- Clean
- Trustworthy
- Interactive
- Fast
- Easy to navigate

Avoid:

- Generic template look
- Excessive gradients
- Excessive glassmorphism
- Overloaded pages
- Tiny text
- Excessive shadows
- Random decorative elements
- Too many colors
- Excessive animations
- Fake statistics
- Fake testimonials

---

# 6. DESIGN SYSTEM

Create a consistent visual system for:

- Colors
- Typography
- Buttons
- Cards
- Inputs
- Forms
- Navigation
- Dropdowns
- Dialogs
- Alerts
- Badges
- Tables
- Pagination
- Tabs
- Progress bars
- Skeleton loaders
- Empty states
- Error states
- Toast notifications

Keep the design system centralized so the visual style can easily be changed later.

---

# 7. COLOR DIRECTION

Use a professional education-focused color palette.

Preferred direction:

- Purple/blue primary colors
- White/soft neutral surfaces
- Dark readable text
- Orange/yellow only for meaningful accents
- Green for success
- Red for errors
- Distinct premium accent

Do not hard-code colors everywhere.

Use centralized theme values.

---

# 8. TYPOGRAPHY

Use the existing project typography when suitable.

Typography must have a clear hierarchy:

- Hero heading
- Page heading
- Section heading
- Card heading
- Body text
- Metadata
- Label
- Caption
- Button text

Keep the typography highly readable on mobile.

---

# 9. GLOBAL WEBSITE STRUCTURE

Create reusable layouts.

## Public Layout

- Header
- Main content
- Footer

## Student Layout

- Student navigation
- Student topbar
- Main content
- Mobile navigation

## Admin Layout

- Admin sidebar
- Admin topbar
- Main content
- Mobile drawer

---

# 10. HEADER / NAVBAR

The ClassNext Header must be **interactive, professional, responsive and visually polished**.

## Desktop Header

Include:

- ClassNext logo
- ClassNext brand name
- Home
- Classes
- Courses
- Notes
- Videos
- Premium
- Notices
- About
- Contact
- Search
- Login
- Register

When Student is logged in:

- Dashboard
- Notifications
- Profile/avatar
- Account menu
- Logout

When Admin is logged in:

- Admin Dashboard
- Profile
- Logout

Keep the header clean and organized.

Use dropdowns when necessary.

---

# 11. HEADER INTERACTIONS

Implement:

- Sticky header
- Active navigation indicator
- Smooth hover effects
- Search interaction
- Mobile hamburger menu
- Animated mobile drawer
- Profile dropdown
- Notification dropdown
- Scroll behavior
- Keyboard navigation
- Focus states

Optional:

When user scrolls down, the header may shrink slightly.

When user scrolls up, it can return to normal height.

Keep the effect subtle.

---

# 12. MOBILE HEADER

Mobile Header must include:

- ClassNext logo
- Menu button
- Search access
- Login/profile action

Mobile navigation should open in a smooth drawer/sheet.

Ensure:

- No horizontal overflow
- Large touch targets
- Clear close button
- Proper spacing
- Smooth transitions
- Good readability

---

# 13. FOOTER

Create a highly professional ClassNext Footer.

## Brand Section

```text
ClassNext

Learn • Practice • Achieve
```

Add an editable short description.

## Quick Links

- Home
- Classes
- Courses
- Notes
- Videos
- Premium
- Notices
- About
- Contact

## Learning

Display active classes dynamically:

- Class 8
- Class 9
- Class 10
- Class 11
- Class 12

Never permanently hard-code the classes.

If Admin adds Class 7 later, it should automatically appear where appropriate.

## Support

- Help
- FAQ
- Contact
- Report a Problem

Only show actual pages.

## Legal

- Privacy Policy
- Terms & Conditions
- Refund Policy
- Cookie Policy where applicable

## Social

Allow Admin to configure:

- YouTube
- Instagram
- Facebook
- LinkedIn
- Telegram
- WhatsApp
- Other social links

Do not show empty social icons.

## Footer Bottom

Use:

```text
© [Current Year] ClassNext. All rights reserved.
```

Add a subtle back-to-top button if suitable.

---

# 14. FOOTER RESPONSIVENESS

Desktop:

- Multi-column

Tablet:

- Responsive grid

Mobile:

- Stacked sections

Optional collapsible sections on mobile.

---

# 15. USER ROLES

There are three levels of access.

## Guest / Public Visitor

Can:

- Browse public pages
- Browse classes
- Browse free resources
- View public notices
- View public courses
- Contact ClassNext
- Register
- Login

## Student

Can:

- Login
- Access assigned class/content
- Watch videos
- Read notes
- Download permitted files
- Listen to audio
- Browse playlists
- Access enrolled courses
- Purchase premium courses
- Track learning progress
- Bookmark resources
- Receive notifications
- Manage profile

## Admin / Teacher

Can manage the complete ClassNext platform.

---

# 16. ADMIN CAPABILITIES

Admin must be able to:

- Add Class
- Edit Class
- Disable Class
- Archive Class
- Add Subject
- Edit Subject
- Add Chapter
- Edit Chapter
- Create Playlist
- Reorder playlist items
- Add Video
- Edit Video
- Schedule Video
- Publish Video
- Add Notes
- Upload PDFs
- Upload Audio
- Upload Images
- Create Courses
- Create Sections
- Add Lessons
- Set Free/Premium
- Set Price
- Publish/Unpublish
- Create Notices
- Schedule Notices
- Create Assignments
- Manage Students
- Manage Enrollments
- Grant/Revoke access
- Manage Orders
- View Payments
- Manage Homepage
- Manage Branding
- Manage Header
- Manage Footer
- Manage Teacher Profile
- Manage SEO content
- Manage social links
- Manage FAQs
- Manage contact enquiries

---

# 17. CLASS MANAGEMENT

Initial classes:

- Class 8
- Class 9
- Class 10
- Class 11
- Class 12

Classes must come from the database.

Admin can:

- Add
- Edit
- Rename
- Change description
- Add thumbnail
- Reorder
- Enable/disable
- Archive

Example:

Admin later adds:

**Class 7**

No source-code modification should be needed.

---

# 18. SUBJECT MANAGEMENT

Structure:

```text
Class
 ↓
Subject
 ↓
Chapter
 ↓
Content
```

Subject fields can include:

- Name
- Description
- Thumbnail
- Class
- Status
- Display order

Admin can create and manage subjects independently for each class.

---

# 19. CHAPTER MANAGEMENT

Admin can:

- Create chapter
- Edit chapter
- Archive chapter
- Reorder chapter
- Add description
- Assign videos
- Assign notes
- Assign audio
- Assign images
- Assign assignments

---

# 20. CONTENT TYPES

Support:

- Video
- Note
- PDF
- Audio
- Image
- Notice
- Playlist
- Course
- Assignment
- Study Material

---

# 21. CONTENT STATES

Support:

```text
DRAFT
SCHEDULED
PUBLISHED
UNPUBLISHED
ARCHIVED
```

Draft and scheduled content must not accidentally become visible.

---

# 22. VIDEO MANAGEMENT

Admin can configure:

- Title
- Description
- Thumbnail
- Video source
- Class
- Subject
- Chapter
- Playlist
- Course
- Tags
- Duration
- Free/Premium
- Featured
- Publication status
- Publish date

Support the existing project's current video workflow.

Do not unnecessarily replace it.

---

# 23. VIDEO PAGE

Example:

`/videos/[slug]`

Show:

- Video player
- Title
- Description
- Class
- Subject
- Chapter
- Playlist
- Course
- Duration
- Publish date
- Bookmark
- Progress
- Previous lesson
- Next lesson
- Related videos
- Related notes
- Related resources

Do not autoplay videos with sound.

---

# 24. VIDEO PROGRESS

Track:

- Current playback position
- Completion percentage
- Completion state
- Last viewed time

Show:

**Continue from where you stopped**

When student returns to a lesson, continue from saved progress.

---

# 25. NOTE / PDF SYSTEM

Admin can upload:

- Notes
- PDFs
- Revision materials
- Study documents
- Question papers

Fields:

- Title
- Description
- Class
- Subject
- Chapter
- Thumbnail
- File
- File type
- File size
- Free/Premium
- Download permission
- Publication status

---

# 26. PDF EXPERIENCE

Student can:

- Preview PDF
- Zoom
- Navigate pages
- Download if allowed
- Bookmark
- Open related resources

Premium files must be protected.

---

# 27. AUDIO SYSTEM

Admin can upload audio lectures.

Support:

- Title
- Description
- Class
- Subject
- Chapter
- Thumbnail
- Audio
- Duration
- Free/Premium
- Download permission

Student audio player:

- Play
- Pause
- Seek
- Volume
- Speed

---

# 28. IMAGE SYSTEM

Admin can upload:

- Diagrams
- Question images
- Homework
- Educational illustrations
- Infographics

Fields:

- Title
- Description
- Class
- Subject
- Chapter
- Category
- Visibility

---

# 29. PLAYLIST SYSTEM

Admin can create playlists.

Example:

**Class 10 Mathematics — Trigonometry**

Admin can:

- Add videos
- Remove videos
- Reorder videos
- Set visibility
- Assign class
- Assign subject
- Assign chapter

Students can:

- Open playlist
- Continue learning
- See completed lessons
- Previous/next navigation
- See progress

---

# 30. COURSE SYSTEM

Course fields:

- Title
- Slug
- Description
- Thumbnail
- Class
- Subject
- Instructor
- Price
- Discount price
- Free/Premium
- Featured
- Status
- Publish date

Course structure:

```text
Course
 ↓
Sections
 ↓
Lessons
 ↓
Videos / Notes / Audio / Resources
```

---

# 31. FREE CONTENT

Support:

- Free videos
- Free notes
- Free PDFs
- Free audio
- Free sample lessons
- Free playlists
- Free course previews

Show a clear:

**FREE**

badge.

---

# 32. PREMIUM CONTENT

Support:

- Premium courses
- Premium playlists
- Premium lessons
- Premium videos
- Premium notes
- Premium audio

For the MVP, prioritize premium course access.

---

# 33. PREMIUM EXPERIENCE

Create a dedicated:

**Premium Courses**

section.

Example:

```text
PREMIUM

Class 10 Mathematics
Complete Course

₹499

[Buy Now]
```

Clearly distinguish:

- Free
- Premium
- Locked
- Purchased

---

# 34. PREMIUM LOCK SCREEN

Unauthorized student sees:

```text
Premium Content

This content is available after enrollment.

[View Course]
[Buy Now]
```

Never expose protected media URLs to unauthorized users.

---

# 35. PAYMENT AND PURCHASE FLOW

Integrate the existing/currently selected payment service for premium purchases.

Required flow:

```text
Student
↓
Premium Course
↓
Buy Now
↓
Order Created
↓
Payment
↓
Server Verification
↓
Payment Confirmation
↓
Enrollment Created
↓
Premium Access Granted
```

Never trust only the client-side payment result.

Payment verification must happen on the server side.

---

# 36. ORDER MANAGEMENT

Store appropriate information for:

- Order
- Student
- Course
- Amount
- Payment status
- Order status
- Payment reference
- Purchase date

Statuses:

```text
PENDING
PAID
FAILED
REFUNDED
CANCELLED
```

Ensure repeated callbacks or retries do not create duplicate purchases.

---

# 37. ENROLLMENT SYSTEM

After verified payment:

Create enrollment.

Enrollment should contain:

- Student
- Course
- Purchase
- Access status
- Purchase date
- Optional expiry if later required

---

# 38. ADMIN MANUAL PREMIUM ACCESS

Admin can:

- Grant access
- Revoke access
- View enrollment
- View payment status

Every manual access change should be recorded.

---

# 39. PURCHASE HISTORY

Student Dashboard must include:

**My Purchases**

Show:

- Course
- Amount
- Order ID
- Purchase date
- Payment status
- Access status

---

# 40. RECEIPT / INVOICE

Create a clean receipt page containing:

- ClassNext
- Student name
- Course
- Order ID
- Payment reference
- Amount
- Date
- Payment status

---

# 41. STUDENT DASHBOARD

Route:

`/student/dashboard`

Include:

- Welcome section
- My Class
- My Courses
- Continue Learning
- Recent Videos
- Recent Notes
- Premium Courses
- Notices
- Bookmarks
- Progress
- Notifications
- Profile

Only display actual user data.

---

# 42. STUDENT LEARNING

Route:

`/student/learning`

Display:

- Subjects
- Courses
- Playlists
- Current lessons
- Completed lessons
- In-progress lessons
- Notes
- Audio
- Videos

---

# 43. BOOKMARK SYSTEM

Student can bookmark:

- Videos
- Notes
- Audio
- Courses
- Playlists

Create:

**My Bookmarks**

Only show bookmarks belonging to the current student.

---

# 44. RECENTLY VIEWED

Track recently accessed content.

Display:

**Continue Learning**

Do not expose another student's activity.

---

# 45. COURSE PROGRESS

Show actual progress.

Example:

```text
Class 10 Mathematics
72% Complete
```

Never use fake percentages.

---

# 46. NOTIFICATIONS

Create an in-app notification center.

Notifications can include:

- New video
- New note
- New notice
- Course purchase
- Premium access
- Course update
- Important announcement

Include:

- Bell icon
- Unread badge
- Dropdown
- Notification page
- Mark as read
- Mark all as read

---

# 47. ASSIGNMENTS

Support basic assignment management.

Admin can create:

- Title
- Description
- Class
- Subject
- Chapter
- Attachment
- Due date
- Instructions

Student can:

- View assignment
- Open/download attachment

Advanced submission/evaluation can remain future scope.

---

# 48. NOTICE SYSTEM

Admin can:

- Create notice
- Edit notice
- Publish
- Pin
- Schedule
- Set expiry
- Archive

Audience can be:

- All students
- Specific class
- Specific course
- Specific eligible students

---

# 49. SEARCH

Create global search.

Search:

- Classes
- Subjects
- Chapters
- Videos
- Notes
- Courses
- Playlists
- Audio
- Notices

Include:

- Debounced search
- Search results page
- Filters
- Empty state
- Loading state
- Error state

Only show resources the current user is authorized to see.

---

# 50. FILTERS

Support:

- Class
- Subject
- Chapter
- Content type
- Free/Premium
- Featured
- Latest
- Course
- Playlist

---

# 51. ADMIN DASHBOARD

Route:

`/admin/dashboard`

Show real data:

- Total Students
- Active Students
- Classes
- Subjects
- Videos
- Notes
- Courses
- Enrollments
- Orders
- Revenue

Never hard-code fake numbers.

---

# 52. ADMIN QUICK ACTIONS

Add quick actions:

```text
+ Add Class
+ Add Subject
+ Add Chapter
+ Upload Video
+ Upload Note
+ Add Audio
+ Create Playlist
+ Create Course
+ Publish Notice
```

---

# 53. ADMIN TABLES

Admin tables should support:

- Search
- Filter
- Sort
- Pagination
- Status badge
- Edit
- View
- Publish
- Unpublish
- Archive
- Safe delete

Use confirmation dialogs before destructive actions.

---

# 54. MEDIA LIBRARY

Create a central media library.

Categories:

- Images
- Videos
- Audio
- PDFs
- Documents

Features:

- Search
- Preview
- Reuse
- Replace
- Archive/delete unused media

Do not delete media still referenced by active content.

---

# 55. WEBSITE CUSTOMIZATION

Admin should be able to manage normal website content without developer help.

## Branding

- ClassNext logo
- Favicon
- Website name
- Tagline
- Teacher photo

## Teacher Profile

- Er. Amit Sir
- Qualification
- Subjects
- Classes
- Bio
- Social links

Only show information entered by Admin.

---

# 56. HOMEPAGE CMS

Admin can manage:

- Hero heading
- Hero description
- Hero image
- CTA text
- Featured courses
- Featured videos
- Featured notes
- Latest content
- Notices
- Teacher section
- Contact CTA

Admin should be able to enable/disable major homepage sections.

---

# 57. HOMEPAGE STRUCTURE

Recommended homepage order:

```text
Header
↓
Hero
↓
Class Navigation
↓
Featured Courses
↓
Latest Videos
↓
Free Resources
↓
Premium Courses
↓
Latest Notes
↓
Audio Lectures
↓
Important Notices
↓
About Er. Amit Sir
↓
Why Learn With ClassNext
↓
Contact CTA
↓
Footer
```

If a section has no data, hide it gracefully or show an appropriate empty state.

---

# 58. ABOUT PAGE

Route:

`/about`

Display:

**Er. Amit Sir**

Content:

- Introduction
- Teaching experience
- Qualification
- Classes taught
- Subjects taught
- Social links

All information must be Admin-controlled.

Do not invent information.

---

# 59. CONTACT PAGE

Route:

`/contact`

Form:

- Name
- Email
- Phone where needed
- Subject
- Message

Requirements:

- Validation
- Error states
- Loading state
- Success state
- Server-side validation
- Spam/rate protection

Save submissions for Admin.

Statuses:

```text
NEW
IN_PROGRESS
RESOLVED
ARCHIVED
```

---

# 60. FAQ PAGE

Route:

`/faq`

Include questions related to:

- Registration
- Login
- Classes
- Notes
- Videos
- Premium courses
- Payments
- Access
- Password reset

Prepare it so Admin can manage FAQ entries later.

---

# 61. AUTHENTICATION

Support:

- Student registration
- Student login
- Admin login
- Logout
- Forgot password
- Reset password
- Email verification
- Secure password hashing
- Protected routes
- Role-based authorization

Use the project's existing authentication mechanism and improve it rather than replacing it unnecessarily.

---

# 62. STUDENT REGISTRATION

Fields:

- Full Name
- Email
- Password
- Confirm Password
- Class

Optional:

- Phone

Students must never be able to choose or create an Admin role.

---

# 63. EMAIL VERIFICATION

If email verification exists or is required, use a secure verification process.

Requirements:

- Expiration
- Single use
- Rate limiting
- Secure storage
- No token leakage

---

# 64. FORGOT PASSWORD

Flow:

```text
Email
↓
Secure reset request
↓
Verification
↓
New password
↓
Success
↓
Login
```

Use secure, expiring, single-use reset credentials.

Avoid account enumeration.

---

# 65. ROLE-BASED ACCESS

Use reusable authorization checks.

The server must protect:

- Admin routes
- Student routes
- Content endpoints
- Downloads
- Payment operations
- Premium content
- User data

Do not rely only on frontend visibility.

---

# 66. CONTENT VISIBILITY

Support:

```text
PUBLIC
LOGGED_IN
CLASS_SPECIFIC
COURSE_SPECIFIC
PREMIUM
STUDENT_SPECIFIC
DRAFT
SCHEDULED
ARCHIVED
```

Every protected operation must validate:

- Authentication
- Account status
- Publication status
- Class permissions
- Enrollment
- Payment status
- Content visibility

---

# 67. PREMIUM MEDIA SECURITY

Protected:

- Videos
- PDFs
- Audio
- Downloads

must not expose unrestricted permanent public URLs.

Use authorized delivery or secure temporary access according to the existing project setup.

---

# 68. FILE UPLOAD SECURITY

Validate:

- File type
- File extension
- File size
- File content where possible

Protect against:

- Path traversal
- Executable files
- Unsafe file names
- Unauthorized uploads
- Malicious uploads

Only authorized Admins can upload/manage content.

---

# 69. DATABASE / DATA MODEL RULE

Use the **existing database and data structure**.

Add or modify models only when required.

Do not recreate the entire database.

Do not duplicate existing tables unnecessarily.

Preserve relationships and existing records.

Important logical relationships:

```text
Class
 ↓
Subject
 ↓
Chapter
 ↓
Content
```

and:

```text
Class
 ↓
Course
 ↓
Section
 ↓
Lesson
 ↓
Content
```

Student:

```text
Student
 ↓
Class Access
 ↓
Enrollment
 ↓
Learning Progress
```

---

# 70. SAFE DATA HANDLING

Prefer safe archive/disable behavior for important records.

Avoid destructive deletion where related data exists.

Use appropriate:

- Active/inactive state
- Archive state
- Deletion timestamp where applicable

---

# 71. SEO

Public pages should have:

- Proper page title
- Meta description
- Canonical URL where appropriate
- Open Graph information
- Correct heading hierarchy
- Meaningful image alt text
- Sitemap where appropriate
- Robots configuration

Do not index:

- Student dashboard
- Admin pages
- Private resources
- Premium-protected content

---

# 72. PWA

If PWA is already present, preserve and improve it.

If missing, add proper installable support using the existing project setup.

Include:

- App name
- Short name
- Theme
- Background
- Correct icons
- Favicon
- Maskable icon where appropriate
- Mobile launch behavior

Do not cache private student data or protected content in a way that can cause cross-user access.

---

# 73. PERFORMANCE

Optimize:

- Images
- Thumbnails
- Loading
- Queries
- API usage
- Large lists
- Search
- Mobile rendering

Use pagination for large datasets.

Use lazy loading where useful.

Avoid unnecessary requests.

---

# 74. RESPONSIVE DESIGN

The entire website must work on:

- Mobile phones
- Tablets
- Laptops
- Desktop
- Large desktop screens

Check common widths including:

```text
360px
390px
430px
768px
1024px
1280px
1440px
1920px
```

No:

- Horizontal scrolling
- Broken cards
- Clipped buttons
- Overlapping elements
- Unusable forms

---

# 75. ACCESSIBILITY

Implement:

- Semantic HTML
- Proper labels
- Keyboard navigation
- Visible focus states
- Accessible dialogs
- Correct alt text
- Good contrast
- Readable text
- Reduced-motion support

Do not use emoji as a replacement for professional interface icons.

---

# 76. ANIMATIONS

Use subtle, professional interactions:

- Hero entrance
- Section reveal
- Card hover
- Button feedback
- Dropdown transitions
- Mobile drawer
- Modal transitions
- Bookmark interaction
- Loading skeletons

Do not animate everything.

Animations must not hurt performance.

---

# 77. LOADING STATES

Create:

- Skeleton cards
- Dashboard skeleton
- Table skeleton
- Button loading
- Upload progress
- Payment processing state
- Page loading states

Never leave blank screens during loading.

---

# 78. EMPTY STATES

Use clear states such as:

```text
No courses available yet.
```

```text
No notes found.
```

```text
No notifications yet.
```

Explain what the user can do next when useful.

---

# 79. ERROR STATES

Create:

- 401
- 403
- 404
- 500
- Payment Failed
- Access Denied
- Content Not Found
- Network Error

Keep all error pages visually consistent with ClassNext.

---

# 80. SECURITY

Implement appropriate security throughout the current application.

Protect against:

- Unauthorized access
- Privilege escalation
- Invalid sessions
- Unsafe uploads
- Input attacks
- Cross-user data access
- Protected content bypass
- Payment tampering
- Unverified callbacks
- Excessive login attempts
- Session misuse

Do not expose:

- Passwords
- Secrets
- Private tokens
- Internal credentials
- Protected media URLs

---

# 81. PAYMENT SECURITY

Never grant premium access based only on the browser's payment-success state.

Always verify payment on the server side.

Payment callbacks must be safe against retries and duplicate processing.

---

# 82. ADMIN AUDIT LOG

Track important actions such as:

- Created class
- Published video
- Updated price
- Granted premium access
- Revoked access
- Disabled student
- Changed homepage
- Changed website settings

Never log passwords or security secrets.

---

# 83. ADMIN SETTINGS

Create:

`/admin/settings`

Sections:

- General
- Branding
- Header
- Footer
- Homepage
- Teacher Profile
- Social Links
- SEO
- Contact
- Payment
- Email
- Media/Storage settings that already exist in the project

---

# 84. HEADER SETTINGS

Admin can manage:

- Logo
- Brand text
- Navigation visibility
- CTA text

Prevent configuration that creates invalid routes or broken links.

---

# 85. FOOTER SETTINGS

Admin can manage:

- Description
- Quick links
- Learning links
- Support links
- Social links
- Legal links
- Contact details

---

# 86. HOMEPAGE SETTINGS

Admin can:

- Enable/disable sections
- Reorder major sections where practical
- Choose featured courses
- Choose featured videos
- Choose featured notes
- Edit hero content
- Edit teacher section
- Edit CTA content

---

# 87. FEATURED CONTENT

Admin can mark content as:

**Featured**

Featured items should appear in their appropriate sections.

Do not create fake popularity metrics.

---

# 88. SCHEDULED PUBLISHING

Admin can schedule:

- Videos
- Notes
- Courses
- Notices

Scheduled content must remain hidden until the scheduled time.

---

# 89. DRAFT PREVIEW

Admin can preview draft content.

Draft content must never appear to unauthorized students or public visitors.

---

# 90. CONTENT TAGS

Allow tags such as:

- Revision
- Important
- Exam
- Practice
- Formula
- Homework
- Board

Use tags for search/filter where useful.

---

# 91. COURSE DETAIL PAGE

Display:

- Thumbnail
- Course title
- Instructor: Er. Amit Sir
- Description
- Class
- Subject
- Price
- Discount
- Buy/Continue button
- Course sections
- Lessons
- Free preview lessons
- Locked premium lessons
- Related courses

---

# 92. FREE PREVIEW

Admin can mark selected premium lessons as:

**Free Preview**

Students can watch/view preview content before purchasing.

Other lessons remain locked.

---

# 93. STUDENT ACCESS AFTER PURCHASE

Flow:

```text
Purchase
↓
Verified payment
↓
Enrollment
↓
My Courses
↓
Continue Course
↓
Protected Lessons
```

---

# 94. MANUAL PREMIUM ACCESS

Admin can manually grant/revoke access.

Record:

- Student
- Course
- Admin
- Date
- Action
- Optional reason

---

# 95. NOTIFICATION CENTER

Student notification page:

`/student/notifications`

Features:

- All notifications
- Unread
- Mark read
- Mark all read

---

# 96. ADMIN CONTACT MANAGEMENT

Admin can search/filter contact enquiries by:

- Name
- Email
- Status
- Date

---

# 97. ADMIN STUDENT MANAGEMENT

Admin can:

- Search
- Filter by class
- View profile
- Manage class
- Activate
- Suspend
- Disable
- View courses
- View purchases
- View progress
- Grant access

Never expose passwords.

---

# 98. MVP SCOPE

The first production launch is the **MVP**.

## MVP PUBLIC WEBSITE

Must include:

- Home
- Header
- Footer
- Classes
- Subjects
- Notes
- Videos
- Courses
- Free Resources
- Premium
- Notices
- About
- Contact
- FAQ
- Privacy
- Terms
- Refund Policy where payment is active

## MVP AUTHENTICATION

Must include:

- Student registration
- Student login
- Admin login
- Logout
- Forgot password
- Reset password
- Email verification
- Role-based access

## MVP ADMIN

Must include:

- Admin Dashboard
- Class Management
- Subject Management
- Chapter Management
- Video Management
- Notes/PDF Management
- Audio Management
- Image Management
- Playlist Management
- Course Management
- Notice Management
- Student Management
- Content Access Control
- Free/Premium Control
- Homepage Management
- Header/Footer settings
- Basic website settings

## MVP STUDENT

Must include:

- Student Dashboard
- My Learning
- Classes
- Subjects
- Videos
- Notes
- Audio
- Notices
- Courses
- Bookmarks
- Progress
- Continue Learning
- Notifications
- Profile

## MVP PREMIUM

Must include:

- Premium Courses
- Pricing
- Payment flow
- Payment verification
- Order management
- Enrollment
- Protected content
- Purchase history
- Receipt

## MVP CORE

Must include:

- Responsive design
- Search
- Filters
- SEO basics
- PWA support
- Security
- Error handling
- Loading states
- Empty states
- Testing
- Deployment readiness

---

# 99. DO NOT BLOCK MVP WITH FUTURE FEATURES

Do not make MVP unnecessarily huge.

Future features:

- Live classes
- Real-time chat
- Community
- Parent accounts
- Multiple teachers
- Advanced tests
- Certificates
- Subscription plans
- AI tutor
- AI content generation
- AI recommendations
- Native mobile application
- Advanced DRM
- Referral system
- Advanced CRM
- Advanced attendance
- Advanced coupon system

Keep the project architecture flexible enough to support these later.

---

# 100. PHASE 2

After MVP is stable:

- Quizzes
- MCQs
- Assignment submissions
- Online tests
- Automatic evaluation
- Certificates
- Coupons
- Advanced analytics
- Email campaigns
- Push notifications
- Bulk content upload
- CSV import/export
- Advanced recommendations

---

# 101. PHASE 3

Later:

- Live classes
- Doubt solving
- Chat
- Community
- Parent portal
- Multiple instructors
- Subscription plans
- AI tutor
- AI-generated tests
- AI recommendations
- Mobile application

Do not implement automatically.

---

# 102. NO FAKE FUNCTIONALITY

Do not create:

- Fake analytics
- Fake revenue
- Fake student count
- Fake testimonials
- Fake reviews
- Fake progress
- Fake payment success
- Fake API results
- Dead buttons

Every MVP feature must be functional.

---

# 103. NO BROKEN BUTTONS

Every button must:

- Perform an actual action
- Navigate to a valid route
- Submit a working form
- Open an actual feature
- Or be intentionally disabled with a clear reason

No meaningless buttons.

---

# 104. NO BROKEN LINKS

Verify all links in:

- Header
- Footer
- Public pages
- Student Dashboard
- Admin Dashboard
- Course pages
- Content pages
- Legal pages

---

# 105. MOBILE EXPERIENCE

Pay special attention to mobile users.

The following must work properly on small screens:

- Header
- Navigation
- Course cards
- Video player
- PDF viewer
- Search
- Student Dashboard
- Payment flow
- Notifications
- Profile
- Admin Dashboard
- Forms
- Tables

---

# 106. ADMIN MOBILE EXPERIENCE

Admin Dashboard must also work well on:

- Mobile
- Tablet
- Desktop

Use:

- Responsive sidebar
- Mobile drawer
- Responsive cards
- Responsive tables
- Touch-friendly controls

---

# 107. DESIGN QUALITY BAR

The final product should feel like:

**Teacher Brand + Learning Platform + Digital Study Library + Course Platform**

It must NOT feel like:

- College assignment
- Basic CRUD application
- Generic admin template
- Blog clone
- Unfinished template
- Static mockup

---

# 108. DEVELOPMENT ORDER

Follow this order.

## Phase 1 — Existing Project Audit

Understand the current application before changing anything.

## Phase 2 — Shared UI

Improve:

- Theme
- Header
- Footer
- Buttons
- Cards
- Forms
- Modals
- Tables
- Toasts
- Skeletons
- Responsive layouts

## Phase 3 — Public Website

Implement/fix:

- Home
- Classes
- Notes
- Videos
- Courses
- Premium
- Notices
- About
- Contact
- FAQ
- Legal pages

## Phase 4 — Authentication

Implement/fix:

- Register
- Login
- Logout
- Email verification
- Password reset
- Role protection

## Phase 5 — Student

Implement/fix:

- Dashboard
- Learning
- Profile
- Bookmarks
- Progress
- Notifications

## Phase 6 — Admin

Implement/fix:

- Dashboard
- Classes
- Subjects
- Chapters
- Videos
- Notes
- Audio
- Images
- Playlists
- Courses
- Notices
- Students
- Settings

## Phase 7 — Premium

Implement/fix:

- Premium courses
- Orders
- Payment
- Verification
- Enrollment
- Access control
- Purchase history
- Receipt

## Phase 8 — Security

Audit:

- Authorization
- Protected routes
- Protected files
- Uploads
- Payment
- Sessions
- Cross-user access

## Phase 9 — Performance

Improve:

- Loading
- Images
- Queries
- Search
- Large lists
- Mobile experience

## Phase 10 — Testing

Test all critical flows.

## Phase 11 — Final Verification

Verify all existing and newly added features.

---

# 109. FINAL END-TO-END FLOW

The final platform must support this complete flow:

```text
ADMIN
↓
Login
↓
Admin Dashboard
↓
Create Class
↓
Create Subject
↓
Create Chapter
↓
Upload Video
↓
Upload Notes
↓
Create Playlist
↓
Create Course
↓
Set Free / Premium
↓
Set Price
↓
Publish
↓
Student opens ClassNext
↓
Student registers
↓
Email verification
↓
Student logs in
↓
Student Dashboard
↓
Browse Class
↓
Browse Subject
↓
Open Chapter
↓
Watch Free Video
↓
Read Free Notes
↓
Open Premium Course
↓
Buy Now
↓
Payment
↓
Server Verification
↓
Payment Confirmation
↓
Enrollment
↓
Premium Access
↓
Watch Lessons
↓
Save Progress
↓
Bookmark Resource
↓
Receive Notification
↓
Return Later
↓
Continue Learning
↓
Admin sees Enrollment / Order
```

---

# 110. PRODUCTION CHECKLIST

Before considering the project complete, verify:

- Header works
- Footer works
- Navigation works
- Public pages work
- Login works
- Registration works
- Password reset works
- Student Dashboard works
- Admin Dashboard works
- Classes work
- Subjects work
- Chapters work
- Videos work
- Notes work
- PDFs work
- Audio works
- Images work
- Playlists work
- Courses work
- Premium works
- Payment flow works
- Payment verification works
- Enrollment works
- Protected content works
- Progress works
- Bookmarks work
- Notifications work
- Search works
- Filters work
- Homepage customization works
- Header settings work
- Footer settings work
- Teacher profile works
- Responsive design works
- PWA works
- SEO works
- Security checks pass
- No secrets exposed
- No unauthorized access
- No broken links
- No dead buttons
- No fake statistics
- Existing functionality still works
- No existing data is lost
- Final project starts and runs correctly

---

# 111. FINAL INSTRUCTION TO THE CODING AI

Start by inspecting the existing **ClassNext** project.

Use the **existing technology, framework, architecture and dependencies already present in the project**.

Do not change the project's technology stack unnecessarily.

Do not introduce a replacement framework simply because you prefer another approach.

Do not rebuild working functionality without a real reason.

Do not delete existing data.

Do not create a new empty database in place of the existing database.

Do not remove existing working authentication.

Do not break existing routes unnecessarily.

Do not expose private content.

Do not trust frontend-only authorization.

Do not trust frontend-only payment success.

Do not create fake production data.

Do not create fake analytics.

Do not leave incomplete MVP functionality.

Do not leave broken links.

Do not leave dead buttons.

Do not create placeholder screens where a real MVP feature is required.

Keep the existing project stable while extending it.

Use the existing project structure wherever possible.

After implementation, provide:

1. Summary of changes
2. Files created/modified
3. Database changes
4. Any required migration steps
5. Any required configuration
6. Commands required to run the existing project
7. Tests performed
8. Important security checks performed
9. External services that still require configuration
10. Any remaining limitations

---

# FINAL PRODUCT

The final website must be:

# **CLASSNEXT**

### Teacher
**Er. Amit Sir**

### Tagline
**Learn • Practice • Achieve**

The project must launch with a stable, polished and fully functional MVP.

After the MVP is stable, future features can be added without rewriting the entire project.

# END OF MASTER PROMPT