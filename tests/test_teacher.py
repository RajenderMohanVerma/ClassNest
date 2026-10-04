"""Teacher CRUD, publication workflow and file-handling tests."""

import io
import os

from app.extensions import db
from app.models import Announcement, Content, Subject, UploadedFile


# ── Subjects ───────────────────────────────────────────────
def test_teacher_can_create_subject(client, login_teacher):
    login_teacher()
    response = client.post(
        '/teacher/subjects/create',
        data={'name': 'Physics', 'description': 'Motion and energy', 'icon': 'bi-lightning'},
        follow_redirects=False,
    )
    assert response.status_code == 302
    subject = Subject.query.filter_by(name='Physics').first()
    assert subject is not None
    assert subject.slug == 'physics'
    assert subject.total_count == 0


def test_duplicate_subject_names_get_unique_slugs(client, login_teacher):
    login_teacher()
    client.post('/teacher/subjects/create', data={'name': 'Physics'})
    client.post('/teacher/subjects/create', data={'name': 'physics'})
    assert Subject.query.count() == 2
    slugs = sorted(subject.slug for subject in Subject.query.all())
    assert slugs == ['physics', 'physics-2']
    assert len(set(slugs)) == 2


def test_subject_creation_requires_name(client, login_teacher):
    login_teacher()
    response = client.post('/teacher/subjects/create', data={'name': ''})
    assert response.status_code == 400
    assert Subject.query.count() == 0


def test_subject_with_content_cannot_be_deleted(client, login_teacher, subject, content):
    login_teacher()
    response = client.post(f'/teacher/subjects/{subject.id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert db.session.get(Subject, subject.id) is not None
    assert b'Cannot delete' in response.data


def test_empty_subject_can_be_deleted(client, login_teacher, subject):
    login_teacher()
    client.post(f'/teacher/subjects/{subject.id}/delete', follow_redirects=True)
    assert db.session.get(Subject, subject.id) is None


def test_subject_edit_updates_fields(client, login_teacher, subject):
    login_teacher()
    client.post(
        f'/teacher/subjects/{subject.id}/edit',
        data={'name': 'Advanced Mathematics', 'description': 'Updated', 'icon': 'bi-book'},
    )
    updated = db.session.get(Subject, subject.id)
    assert updated.name == 'Advanced Mathematics'
    assert updated.slug == 'advanced-mathematics'


# ── Content ────────────────────────────────────────────────
def _content_payload(**overrides):
    payload = {
        'title': 'Trigonometry',
        'description': 'Sine and cosine.',
        'topic': 'Chapter 1',
        'content_type': 'notes',
        'body_html': '<p>Intro to trig.</p>',
        'tags': 'math, trig',
        'video_url': 'https://www.example.com/video',
        'resource_url': '',
    }
    payload.update(overrides)
    return payload


def test_teacher_can_create_draft_content(client, login_teacher, subject):
    login_teacher()
    response = client.post(
        '/teacher/content/create',
        data=_content_payload(subject_id=subject.id),
        content_type='multipart/form-data',
    )
    assert response.status_code == 302
    item = Content.query.filter_by(title='Trigonometry').first()
    assert item is not None
    assert item.status == 'draft'
    assert item.published_at is None
    assert item.slug == 'trigonometry'


def test_publish_flag_sets_publication_timestamp(client, login_teacher, subject):
    login_teacher()
    client.post(
        '/teacher/content/create',
        data=_content_payload(subject_id=subject.id, status='published'),
        content_type='multipart/form-data',
    )
    item = Content.query.filter_by(title='Trigonometry').first()
    assert item.is_published
    assert item.published_at is not None


def test_content_body_is_sanitized_before_storage(client, login_teacher, subject):
    login_teacher()
    hostile = (
        '<p>Safe text</p><script>alert("xss")</script>'
        '<img src="javascript:alert(1)"><a href="javascript:alert(2)">bad</a>'
    )
    client.post(
        '/teacher/content/create',
        data=_content_payload(subject_id=subject.id, body_html=hostile),
        content_type='multipart/form-data',
    )
    body = Content.query.filter_by(title='Trigonometry').first().body_html
    assert '<script>' not in body
    assert 'alert("xss")' not in body
    assert 'javascript:' not in body
    assert 'Safe text' in body


def test_content_requires_title_and_subject(client, login_teacher, subject):
    login_teacher()
    response = client.post(
        '/teacher/content/create',
        data=_content_payload(title='', subject_id=subject.id),
        content_type='multipart/form-data',
    )
    assert response.status_code == 400
    assert Content.query.count() == 0

    response = client.post(
        '/teacher/content/create',
        data=_content_payload(subject_id=''),
        content_type='multipart/form-data',
    )
    assert response.status_code == 400
    assert Content.query.count() == 0


def test_content_rejects_invalid_type_and_url(client, login_teacher, subject):
    login_teacher()
    response = client.post(
        '/teacher/content/create',
        data=_content_payload(subject_id=subject.id, content_type='not_a_type'),
        content_type='multipart/form-data',
    )
    assert response.status_code == 400
    assert b'valid content type' in response.data

    response = client.post(
        '/teacher/content/create',
        data=_content_payload(subject_id=subject.id, video_url='javascript:alert(1)'),
        content_type='multipart/form-data',
    )
    assert response.status_code == 400
    assert b'http://' in response.data


def test_content_requires_existing_subject(client, login_teacher):
    login_teacher()
    response = client.post(
        '/teacher/content/create',
        data=_content_payload(subject_id=99999),
        content_type='multipart/form-data',
    )
    assert response.status_code == 400
    assert b'no longer exists' in response.data


def test_duplicate_titles_get_unique_slugs(client, login_teacher, subject, content):
    login_teacher()
    client.post(
        '/teacher/content/create',
        data=_content_payload(title=content.title, subject_id=subject.id),
        content_type='multipart/form-data',
    )
    slugs = {item.slug for item in Content.query.all()}
    assert len(slugs) == len(Content.query.all())


def test_edit_content_can_unpublish(client, login_teacher, published_content):
    login_teacher()
    client.post(
        f'/teacher/content/{published_content.id}/edit',
        data=_content_payload(
            title=published_content.title, subject_id=published_content.subject_id
        ),
        content_type='multipart/form-data',
    )
    item = db.session.get(Content, published_content.id)
    assert item.status == 'draft'
    assert item.published_at is None


def test_edit_content_keeps_slug_stable_for_same_title(client, login_teacher, content):
    login_teacher()
    original_slug = content.slug
    client.post(
        f'/teacher/content/{content.id}/edit',
        data=_content_payload(title=content.title, subject_id=content.subject_id),
        content_type='multipart/form-data',
    )
    assert db.session.get(Content, content.id).slug == original_slug


def test_toggle_publish_flips_state_and_timestamp(client, login_teacher, content):
    login_teacher()
    client.post(f'/teacher/content/{content.id}/toggle', follow_redirects=True)
    item = db.session.get(Content, content.id)
    assert item.is_published and item.published_at is not None

    client.post(f'/teacher/content/{content.id}/toggle', follow_redirects=True)
    item = db.session.get(Content, content.id)
    assert item.status == 'draft' and item.published_at is None


def test_content_list_filters_and_pagination(client, login_teacher, subject, content):
    login_teacher()
    response = client.get('/teacher/content?q=algebra&status=draft')
    assert response.status_code == 200
    assert b'Algebra Basics' in response.data

    response = client.get('/teacher/content?q=does-not-exist-anywhere')
    assert b'No content found' in response.data


def test_content_preview_available_to_teacher(client, login_teacher, content):
    login_teacher()
    response = client.get(f'/teacher/content/{content.id}/preview')
    assert response.status_code == 200
    assert b'Preview' in response.data


def test_missing_content_returns_404(client, login_teacher):
    login_teacher()
    assert client.get('/teacher/content/999/preview').status_code == 404


def test_deleting_content_removes_uploads(app, client, login_teacher, subject, png_bytes, fake_pdf):
    login_teacher()
    client.post(
        '/teacher/content/create',
        data={
            **_content_payload(title='With Files', subject_id=subject.id),
            'thumbnail': (io.BytesIO(png_bytes), 'cover.png'),
            'attachment': (io.BytesIO(fake_pdf), 'notes.pdf'),
        },
        content_type='multipart/form-data',
    )
    item = Content.query.filter_by(title='With Files').first()
    upload_folder = app.config['UPLOAD_FOLDER']
    stored = [f.stored_name for f in UploadedFile.query.all()]
    assert len(stored) == 2
    for name in stored:
        assert os.path.exists(os.path.join(upload_folder, name))

    client.post(f'/teacher/content/{item.id}/delete', follow_redirects=True)
    assert Content.query.filter_by(title='With Files').first() is None
    assert UploadedFile.query.count() == 0
    for name in stored:
        assert not os.path.exists(os.path.join(upload_folder, name))


def test_replacing_an_attachment_removes_the_previous_file(app, client, login_teacher, subject, fake_pdf):
    login_teacher()
    payload = {
        **_content_payload(title='Replaceable', subject_id=subject.id),
        'attachment': (io.BytesIO(fake_pdf), 'first.pdf'),
    }
    client.post('/teacher/content/create', data=payload, content_type='multipart/form-data')
    item = Content.query.filter_by(title='Replaceable').first()
    first_stored = item.attachment
    upload_folder = app.config['UPLOAD_FOLDER']
    assert os.path.exists(os.path.join(upload_folder, first_stored))

    client.post(
        f'/teacher/content/{item.id}/edit',
        data={
            **_content_payload(title='Replaceable', subject_id=subject.id),
            'attachment': (io.BytesIO(fake_pdf), 'second.pdf'),
        },
        content_type='multipart/form-data',
    )

    updated = Content.query.filter_by(title='Replaceable').first()
    assert updated.attachment and updated.attachment != first_stored
    assert os.path.exists(os.path.join(upload_folder, updated.attachment))
    assert not os.path.exists(os.path.join(upload_folder, first_stored))
    assert UploadedFile.query.count() == 1
    record = UploadedFile.query.first()
    assert record.original_name == 'second.pdf'


def test_rejected_upload_does_not_block_content_creation(
    app, client, login_teacher, subject, png_bytes
):
    login_teacher()
    response = client.post(
        '/teacher/content/create',
        data={
            **_content_payload(title='Bad Attachment', subject_id=subject.id),
            'attachment': (io.BytesIO(b'not really a pdf'), 'notes.pdf'),
        },
        content_type='multipart/form-data',
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert Content.query.filter_by(title='Bad Attachment').first() is not None
    assert UploadedFile.query.count() == 0


def test_disallowed_extension_is_rejected(client, login_teacher, subject):
    login_teacher()
    client.post(
        '/teacher/content/create',
        data={
            **_content_payload(title='Executable', subject_id=subject.id),
            'attachment': (io.BytesIO(b'MZ\x90\x00'), 'payload.exe'),
        },
        content_type='multipart/form-data',
        follow_redirects=True,
    )
    assert UploadedFile.query.count() == 0


# ── Announcements ──────────────────────────────────────────
def test_teacher_can_create_published_announcement(client, login_teacher):
    login_teacher()
    client.post(
        '/teacher/announcements/create',
        data={
            'title': 'Exam schedule',
            'body': '<p>Exam on Friday.</p><script>alert(1)</script>',
            'is_published': 'on',
        },
    )
    item = Announcement.query.filter_by(title='Exam schedule').first()
    assert item.is_published
    assert item.published_at is not None
    assert '<script>' not in item.body


def test_announcement_requires_title_and_body(client, login_teacher):
    login_teacher()
    response = client.post(
        '/teacher/announcements/create', data={'title': '', 'body': ''}
    )
    assert response.status_code == 400
    assert Announcement.query.count() == 0


def test_unpublishing_announcement_clears_timestamp(client, login_teacher, announcement):
    login_teacher()
    client.post(
        f'/teacher/announcements/{announcement.id}/edit',
        data={'title': announcement.title, 'body': announcement.body},
    )
    item = db.session.get(Announcement, announcement.id)
    assert item.is_published is False
    assert item.published_at is None


def test_delete_announcement(client, login_teacher, announcement):
    login_teacher()
    client.post(f'/teacher/announcements/{announcement.id}/delete', follow_redirects=True)
    assert Announcement.query.count() == 0


# ── Students, files, profile ───────────────────────────────
def test_teacher_sees_registered_students(client, login_teacher, student):
    login_teacher()
    response = client.get('/teacher/students')
    assert student.name.encode() in response.data


def test_teacher_can_search_students(client, login_teacher, student):
    login_teacher()
    assert b'Test Student' in client.get('/teacher/students?q=test').data
    assert b'No students match' in client.get('/teacher/students?q=zzz').data


def test_file_listing_uses_human_readable_size(
    app, client, login_teacher, subject, fake_pdf
):
    login_teacher()
    client.post(
        '/teacher/content/create',
        data={
            **_content_payload(title='Sized', subject_id=subject.id),
            'attachment': (io.BytesIO(fake_pdf), 'guide.pdf'),
        },
        content_type='multipart/form-data',
    )
    response = client.get('/teacher/files')
    assert b'guide.pdf' in response.data
    assert UploadedFile.query.first().size_display.endswith('B')


def test_teacher_profile_update(client, login_teacher, teacher):
    login_teacher()
    response = client.post(
        '/teacher/profile',
        data={'action': 'update_profile', 'name': 'Renamed Teacher', 'email': teacher.email},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert db.session.get(type(teacher), teacher.id).name == 'Renamed Teacher'


def test_teacher_profile_rejects_duplicate_email(client, login_teacher, teacher, student):
    login_teacher()
    response = client.post(
        '/teacher/profile',
        data={'action': 'update_profile', 'name': teacher.name, 'email': student.email},
        follow_redirects=True,
    )
    assert b'Email already in use' in response.data


def test_password_change_requires_current_password(client, login_teacher, teacher):
    login_teacher()
    response = client.post(
        '/teacher/profile',
        data={
            'action': 'change_password',
            'current_password': 'wrong',
            'new_password': 'newsecret1',
            'confirm_password': 'newsecret1',
        },
        follow_redirects=True,
    )
    assert b'Current password is incorrect' in response.data
    assert teacher.check_password('teacherpass')


def test_password_change_succeeds(client, login_teacher, teacher):
    login_teacher()
    response = client.post(
        '/teacher/profile',
        data={
            'action': 'change_password',
            'current_password': 'teacherpass',
            'new_password': 'newsecret1',
            'confirm_password': 'newsecret1',
        },
        follow_redirects=True,
    )
    assert b'Password changed' in response.data
    assert teacher.check_password('newsecret1')

# ── Page rendering regression ───────────────────────────────
def test_teacher_announcement_pages_render_summary(client, login_teacher, announcement):
    login_teacher()

    listing = client.get('/teacher/announcements')
    assert listing.status_code == 200
    assert b'Classes start Monday' in listing.data

    form = client.get('/teacher/announcements/create')
    assert form.status_code == 200

    edit = client.get(f'/teacher/announcements/{announcement.id}/edit')
    assert edit.status_code == 200


def test_teacher_content_edit_form_renders_summary(client, login_teacher, content):
    login_teacher()
    response = client.get(f'/teacher/content/{content.id}/edit')
    assert response.status_code == 200
    assert b'An introduction to algebra.' in response.data


def test_teacher_dashboard_and_lists_render(client, login_teacher, content, subject, announcement):
    login_teacher()
    for path in (
        '/teacher/dashboard',
        '/teacher/content',
        '/teacher/subjects',
        '/teacher/students',
        '/teacher/files',
        '/teacher/profile',
    ):
        assert client.get(path).status_code == 200, path
