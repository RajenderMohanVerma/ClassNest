"""Student-facing browsing, publication visibility and file access tests."""

import io
import os

from app.extensions import db
from app.models import Announcement, Chapter, Content, Course, SchoolClass, Subject, UploadedFile


def test_dashboard_renders_for_student(client, login_student, published_content, subject):
    login_student()
    response = client.get('/student/dashboard')
    assert response.status_code == 200
    assert published_content.title.encode() in response.data
    assert subject.name.encode() in response.data


def test_dashboard_handles_content_without_body(client, login_student, subject, teacher):
    bare = Content(
        title='Bare Lesson',
        slug=Content.unique_slug('Bare Lesson'),
        subject_id=subject.id,
        content_type='notes',
        body_html=None,
        description=None,
        status='published',
        created_by=teacher.id,
    )
    bare.publish()
    db.session.add(bare)
    db.session.commit()

    login_student()
    response = client.get('/student/dashboard')
    assert response.status_code == 200
    assert b'Bare Lesson' in response.data


def test_student_library_dashboard_and_search_are_scoped_to_their_class(
    client, login_student, student, school_class, subject, teacher,
):
    other_class = SchoolClass(name='Class 11', slug='class-11', created_by=teacher.id)
    db.session.add(other_class)
    db.session.flush()
    other_subject = Subject(
        name='Other Class Physics', slug='other-class-physics',
        class_id=other_class.id, created_by=teacher.id,
    )
    db.session.add(other_subject)
    db.session.flush()

    same_class = Content(
        title='My Class Learning', slug='my-class-learning',
        class_id=school_class.id, subject_id=subject.id,
        content_type='notes', status='published', access_level='public',
        created_by=teacher.id,
    )
    other_class_content = Content(
        title='Other Class Secret', slug='other-class-secret',
        class_id=other_class.id, subject_id=other_subject.id,
        content_type='notes', status='published', access_level='public',
        created_by=teacher.id,
    )
    same_class.publish()
    other_class_content.publish()
    same_class_course = Course(
        title='My Class Course', slug='my-class-course', class_id=school_class.id,
        access_level='public', status='published', created_by=teacher.id,
    )
    other_class_course = Course(
        title='Other Class Course', slug='other-class-course', class_id=other_class.id,
        access_level='public', status='published', created_by=teacher.id,
    )
    db.session.add_all([same_class, other_class_content, same_class_course, other_class_course])
    db.session.commit()

    assert student.class_id == school_class.id
    login_student()

    for path in (
        '/student/dashboard', '/student/content', '/student/search?q=class',
        '/notes', '/search?q=class',
    ):
        response = client.get(path)
        assert response.status_code == 200, path
        assert b'My Class Learning' in response.data, path
        assert b'Other Class Secret' not in response.data, path
        assert b'Other Class Physics' not in response.data, path

    assert b'Other Class Physics' not in client.get('/student/subjects').data
    classes_page = client.get('/classes').data
    assert school_class.name.encode() in classes_page
    assert other_class.name.encode() not in classes_page
    courses_page = client.get('/courses').data
    assert b'My Class Course' in courses_page
    assert b'Other Class Course' not in courses_page


def test_student_cannot_open_another_class_content_subject_chapter_or_file(
    app, client, login_student, student, school_class, subject, teacher, png_bytes,
):
    other_class = SchoolClass(name='Class 11', slug='class-11', created_by=teacher.id)
    db.session.add(other_class)
    db.session.flush()
    other_subject = Subject(
        name='Other Class Physics', slug='other-class-physics',
        class_id=other_class.id, created_by=teacher.id,
    )
    db.session.add(other_subject)
    db.session.flush()
    other_chapter = Chapter(
        title='Other Class Chapter', slug='other-class-chapter',
        class_id=other_class.id, subject_id=other_subject.id,
        status='published', created_by=teacher.id,
    )
    db.session.add(other_chapter)
    db.session.flush()
    stored_name = 'e' * 32 + '.png'
    other_content = Content(
        title='Other Class Secret', slug='other-class-secret',
        class_id=other_class.id, subject_id=other_subject.id,
        chapter_id=other_chapter.id, thumbnail=stored_name,
        content_type='notes', status='published', access_level='public',
        created_by=teacher.id,
    )
    other_content.publish()
    db.session.add(other_content)
    db.session.commit()
    with open(f"{app.config['UPLOAD_FOLDER']}/{stored_name}", 'wb') as handle:
        handle.write(png_bytes)

    login_student()

    assert client.get(f'/student/content/{other_content.slug}').status_code == 404
    assert client.get(f'/content/{other_content.slug}').status_code == 404
    assert client.get(f'/student/subjects/{other_subject.slug}').status_code == 404
    assert client.get(f'/subjects/{other_subject.slug}').status_code == 404
    assert client.get(f'/chapters/{other_chapter.slug}').status_code == 404
    assert client.get(f'/classes/{other_class.slug}').status_code == 404
    assert client.get(f'/files/{stored_name}').status_code == 403

    os.remove(f"{app.config['UPLOAD_FOLDER']}/{stored_name}")


def test_students_never_see_drafts(client, login_student, content, published_content):
    login_student()
    response = client.get('/student/content')
    assert published_content.title.encode() in response.data
    assert content.title.encode() not in response.data


def test_student_cannot_open_draft_detail(client, login_student, content):
    login_student()
    assert client.get(f'/student/content/{content.slug}').status_code == 404


def test_student_can_read_published_content(client, login_student, published_content):
    login_student()
    response = client.get(f'/student/content/{published_content.slug}')
    assert response.status_code == 200
    assert b'Published body' in response.data


def test_subject_detail_lists_only_published(client, login_student, subject, content, published_content):
    login_student()
    response = client.get(f'/student/subjects/{subject.slug}')
    assert published_content.title.encode() in response.data
    assert content.title.encode() not in response.data


def test_unknown_subject_returns_404(client, login_student):
    login_student()
    assert client.get('/student/subjects/not-a-subject').status_code == 404


def test_library_filters(client, login_student, subject, teacher):
    notes = Content(
        title='Notes Lesson', slug=Content.unique_slug('Notes Lesson'),
        subject_id=subject.id, content_type='notes', status='published', created_by=teacher.id,
    )
    notes.publish()
    video = Content(
        title='Video Lesson', slug=Content.unique_slug('Video Lesson'),
        subject_id=subject.id, content_type='video_lesson', status='published', created_by=teacher.id,
    )
    video.publish()
    db.session.add_all([notes, video])
    db.session.commit()

    login_student()
    response = client.get('/student/content?type=video_lesson')
    assert b'Video Lesson' in response.data
    assert b'Notes Lesson' not in response.data


def test_library_ignores_invalid_filter_values(client, login_student, published_content):
    login_student()
    assert client.get('/student/content?subject=not-an-int').status_code == 200
    assert client.get('/student/content?type=bogus').status_code == 200


def test_library_subject_filter_preserves_selection(client, login_student, subject, published_content):
    login_student()
    response = client.get(f'/student/content?subject={subject.id}')
    assert response.status_code == 200
    assert b'value="%d" selected' % subject.id in response.data


def test_pagination_preserves_active_filters(client, login_student, subject, teacher):
    for index in range(15):
        item = Content(
            title=f'Bulk Lesson {index}',
            slug=Content.unique_slug(f'Bulk Lesson {index}'),
            subject_id=subject.id,
            content_type='notes',
            status='published',
            created_by=teacher.id,
        )
        item.publish()
        db.session.add(item)
    db.session.commit()

    login_student()
    response = client.get(f'/student/content?subject={subject.id}&sort=newest')
    assert response.status_code == 200
    body = response.data
    assert b'page=2' in body
    assert b'subject=%d' % subject.id in body
    assert b'sort=newest' in body


def test_search_matches_title_topic_and_body(client, login_student, published_content):
    login_student()
    assert published_content.title.encode() in client.get('/student/search?q=published').data
    assert b'No results found' in client.get('/student/search?q=zzzznothing').data
    assert client.get('/student/search').status_code == 200


def test_announcements_only_show_published(client, login_student, teacher, announcement):
    draft = Announcement(title='Draft notice', body='<p>Hidden.</p>', is_published=False, created_by=teacher.id)
    db.session.add(draft)
    db.session.commit()

    login_student()
    response = client.get('/student/announcements')
    assert b'Welcome week' in response.data
    assert b'Draft notice' not in response.data


def test_student_profile_update(client, login_student, student):
    login_student()
    response = client.post(
        '/student/profile',
        data={'action': 'update_profile', 'name': 'Renamed Student', 'email': student.email},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert db.session.get(type(student), student.id).name == 'Renamed Student'


def test_student_can_change_their_class_from_profile(
    client, login_student, student, teacher,
):
    other_class = SchoolClass(name='Class 11', slug='class-11', created_by=teacher.id)
    db.session.add(other_class)
    db.session.commit()
    login_student()

    response = client.post('/student/profile', data={
        'action': 'update_profile',
        'name': student.name,
        'email': student.email,
        'class_id': str(other_class.id),
    })

    assert response.status_code == 302
    assert student.class_id == other_class.id


def test_legacy_student_without_a_class_is_prompted_and_sees_no_catalog(
    client, login_student, student, published_content,
):
    student.class_id = None
    db.session.commit()
    login_student()

    dashboard = client.get('/student/dashboard')
    assert dashboard.status_code == 200
    assert b'Choose your class' in dashboard.data
    assert published_content.title.encode() not in dashboard.data

    assert published_content.title.encode() not in client.get('/student/content').data
    assert client.get(f'/student/content/{published_content.slug}').status_code == 404
    assert b'Class 10' not in client.get('/classes').data


def test_student_password_change(client, login_student, student):
    login_student()
    response = client.post(
        '/student/profile',
        data={
            'action': 'change_password',
            'current_password': 'studentpass',
            'new_password': 'brandnew1',
            'confirm_password': 'brandnew1',
        },
        follow_redirects=True,
    )
    assert b'Password changed' in response.data
    assert student.check_password('brandnew1')


# ── File access control ────────────────────────────────────
def test_anonymous_users_cannot_fetch_uploads(app, client, subject, teacher, png_bytes):
    stored = UploadedFile(stored_name='a' * 32 + '.png')
    content_item = Content(
        title='Has Cover', slug='has-cover', subject_id=subject.id,
        thumbnail=stored.stored_name, status='published', created_by=teacher.id,
    )
    db.session.add(content_item)
    db.session.commit()

    with open(f"{app.config['UPLOAD_FOLDER']}/{stored.stored_name}", 'wb') as handle:
        handle.write(png_bytes)

    response = client.get(f'/files/{stored.stored_name}')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


def test_students_cannot_fetch_draft_thumbnail(app, client, login_student, subject, teacher, png_bytes):
    stored_name = 'b' * 32 + '.png'
    draft = Content(
        title='Draft With Cover', slug='draft-with-cover', subject_id=subject.id,
        thumbnail=stored_name, status='draft', created_by=teacher.id,
    )
    db.session.add(draft)
    db.session.commit()
    with open(f"{app.config['UPLOAD_FOLDER']}/{stored_name}", 'wb') as handle:
        handle.write(png_bytes)

    login_student()
    assert client.get(f'/files/{stored_name}').status_code == 403


def test_teacher_can_fetch_draft_thumbnail(app, client, login_teacher, subject, teacher, png_bytes):
    stored_name = 'c' * 32 + '.png'
    draft = Content(
        title='Draft Cover', slug='draft-cover', subject_id=subject.id,
        thumbnail=stored_name, status='draft', created_by=teacher.id,
    )
    db.session.add(draft)
    db.session.commit()
    with open(f"{app.config['UPLOAD_FOLDER']}/{stored_name}", 'wb') as handle:
        handle.write(png_bytes)

    login_teacher()
    response = client.get(f'/files/{stored_name}')
    assert response.status_code == 200
    assert response.headers['X-Content-Type-Options'] == 'nosniff'


def test_student_download_uses_original_filename(
    client, login, student, teacher, subject, chapter, fake_pdf
):
    login(teacher.email, 'teacherpass')
    client.post(
        '/teacher/content/create',
        data={
            'title': 'Downloadable', 'class_id': subject.class_id,
            'subject_id': subject.id, 'chapter_id': chapter.id,
            'description': 'Has a PDF', 'content_type': 'pdf_resource',
            'body_html': '<p>Body</p>', 'status': 'published',
            'attachment': (io.BytesIO(fake_pdf), 'semester-notes.pdf'),
        },
        content_type='multipart/form-data',
    )

    login(student.email, 'studentpass')
    item = Content.query.filter_by(title='Downloadable').first()
    assert item is not None

    redirect_response = client.get(f'/student/content/{item.slug}/download')
    assert redirect_response.status_code == 302
    stored_name = item.attachment

    response = client.get(f'/files/{stored_name}')
    assert response.status_code == 200
    disposition = response.headers.get('Content-Disposition', '')
    assert 'semester-notes.pdf' in disposition
    assert stored_name not in disposition


def test_file_route_rejects_path_traversal(client, login_teacher):
    login_teacher()
    assert client.get('/files/..%2F..%2F.env').status_code in (400, 404)


def test_uploads_are_not_reachable_through_the_static_folder(client, subject, teacher, png_bytes):
    stored_name = 'd' * 32 + '.png'
    legacy_folder = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'app', 'static', 'uploads',
    )
    os.makedirs(legacy_folder, exist_ok=True)
    with open(os.path.join(legacy_folder, stored_name), 'wb') as handle:
        handle.write(png_bytes)
    try:
        draft = Content(
            title='Static Probe', slug='static-probe', subject_id=subject.id,
            thumbnail=stored_name, status='draft', created_by=teacher.id,
        )
        db.session.add(draft)
        db.session.commit()

        response = client.get(f'/static/uploads/{stored_name}')
        assert response.status_code == 404
    finally:
        os.remove(os.path.join(legacy_folder, stored_name))


def test_authenticated_pages_are_not_cached(client, login_student, published_content):
    with client.session_transaction() as flask_session:
        flask_session.clear()

    public = client.get('/offline')
    assert public.status_code == 200
    assert 'no-store' not in public.headers.get('Cache-Control', '')

    login_student()
    response = client.get('/student/dashboard')
    assert response.status_code == 200
    assert 'no-store' in response.headers['Cache-Control']

# ── Page rendering regression ───────────────────────────────
def test_student_dashboard_renders_announcement_summary(client, login_student, announcement):
    login_student()
    response = client.get('/student/dashboard')
    assert response.status_code == 200
    assert b'Classes start Monday' in response.data

    listing = client.get('/student/announcements')
    assert listing.status_code == 200
    assert b'Classes start Monday' in listing.data


def test_student_content_detail_renders_tags_and_summary(client, login_student, published_content):
    published_content.tags = 'algebra, basics'
    db.session.commit()

    login_student()
    response = client.get(f'/student/content/{published_content.slug}')
    assert response.status_code == 200
    assert b'algebra' in response.data
    assert b'basics' in response.data


def test_student_pages_render(client, login_student, published_content, subject, announcement):
    login_student()
    for path in (
        '/student/dashboard',
        '/student/subjects',
        f'/student/subjects/{subject.slug}',
        '/student/content',
        '/student/announcements',
        '/student/search',
        '/student/search?q=published',
        '/student/profile',
    ):
        assert client.get(path).status_code == 200, path
