"""Student-facing browsing, publication visibility and file access tests."""

import io

from app.extensions import db
from app.models import Announcement, Content, UploadedFile


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
    assert b'page=2&amp;subject=%d&amp;sort=newest' % subject.id in response.data


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
    client, login, student, teacher, subject, fake_pdf
):
    login(teacher.email, 'teacherpass')
    client.post(
        '/teacher/content/create',
        data={
            'title': 'Downloadable', 'subject_id': subject.id,
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