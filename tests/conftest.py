"""Shared pytest fixtures.

The suite runs against an in-memory SQLite database (see TestingConfig) so it
never touches the PostgreSQL instance used for development or production.
"""

import os
import shutil
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('FLASK_ENV', 'testing')

from app import create_app, db  # noqa: E402
from app.config import TestingConfig  # noqa: E402
from app.models import (  # noqa: E402
    Announcement,
    Chapter,
    Content,
    Course,
    CourseLesson,
    CourseSection,
    SchoolClass,
    Subject,
    UploadedFile,
    User,
)


@pytest.fixture()
def app():
    upload_dir = tempfile.mkdtemp(prefix='classnext-test-')

    class _TestConfig(TestingConfig):
        UPLOAD_FOLDER = upload_dir

    application = create_app(_TestConfig)

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()

    shutil.rmtree(upload_dir, ignore_errors=True)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def teacher(app):
    user = User(name='Test Teacher', email='teacher@example.com', role='teacher')
    user.set_password('teacherpass')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def student(app):
    user = User(name='Test Student', email='student@example.com', role='student')
    user.set_password('studentpass')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def subject(app, teacher, school_class):
    item = Subject(
        name='Mathematics',
        slug=Subject.unique_slug('Mathematics'),
        description='Numbers and logic',
        icon='bi-calculator',
        class_id=school_class.id,
        created_by=teacher.id,
    )
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture()
def content(app, teacher, subject):
    item = Content(
        title='Algebra Basics',
        slug=Content.unique_slug('Algebra Basics'),
        description='An introduction to algebra.',
        subject_id=subject.id,
        content_type='notes',
        body_html='<p>Variables and equations.</p>',
        status='draft',
        created_by=teacher.id,
    )
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture()
def published_content(app, teacher, subject):
    item = Content(
        title='Published Lesson',
        slug=Content.unique_slug('Published Lesson'),
        description='Visible to students.',
        subject_id=subject.id,
        content_type='study_material',
        body_html='<p>Published body.</p>',
        status='published',
        created_by=teacher.id,
    )
    item.publish()
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture()
def announcement(app, teacher):
    item = Announcement(
        title='Welcome week',
        body='<p>Classes start Monday.</p>',
        is_published=True,
        created_by=teacher.id,
    )
    item.publish()
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture()
def school_class(app, teacher):
    item = SchoolClass(
        name='Class 10',
        slug=SchoolClass.unique_slug('Class 10'),
        description='Secondary stage',
        display_order=1,
        created_by=teacher.id,
    )
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture()
def chapter(app, subject, school_class, teacher):
    item = Chapter(
        title='Real Numbers',
        slug=Chapter.unique_slug('Real Numbers'),
        subject_id=subject.id,
        class_id=school_class.id,
        display_order=1,
        status='published',
        created_by=teacher.id,
    )
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture()
def course(app, teacher, subject, school_class):
    item = Course(
        title='Class 10 Mathematics Complete Course',
        slug=Course.unique_slug('Class 10 Mathematics Complete Course'),
        description='Full syllabus course.',
        class_id=school_class.id,
        subject_id=subject.id,
        instructor_id=teacher.id,
        price=499,
        access_level='premium',
        status='published',
        created_by=teacher.id,
    )
    item.published_at = item.created_at
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture()
def course_section(app, course):
    item = CourseSection(
        course_id=course.id,
        title='Chapter 1',
        slug='chapter-1',
        display_order=0,
    )
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture()
def course_lesson(app, course, course_section, teacher, subject):
    lesson_content = Content(
        title='Introduction Lesson',
        slug=Content.unique_slug('Introduction Lesson'),
        subject_id=subject.id,
        class_id=course.class_id,
        content_type='video_lesson',
        video_url='https://example.com/v/intro.mp4',
        status='published',
        created_by=teacher.id,
    )
    lesson_content.publish()
    db.session.add(lesson_content)
    db.session.flush()

    item = CourseLesson(
        course_id=course.id,
        section_id=course_section.id,
        content_id=lesson_content.id,
        title='Introduction',
        display_order=0,
        is_preview=True,
    )
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture()
def login(client):
    def _login(email, password):
        return client.post(
            '/auth/login',
            data={'email': email, 'password': password},
            follow_redirects=False,
        )

    return _login


@pytest.fixture()
def login_teacher(client, login, teacher):
    login(teacher.email, 'teacherpass')

    def _as_teacher():
        with client.session_transaction() as session:
            session['user_id'] = teacher.id
            session['user_role'] = teacher.role
            session['user_name'] = teacher.name
        return teacher

    return _as_teacher


@pytest.fixture()
def login_student(client, login, student):
    login(student.email, 'studentpass')

    def _as_student():
        with client.session_transaction() as session:
            session['user_id'] = student.id
            session['user_role'] = student.role
            session['user_name'] = student.name
        return student

    return _as_student


@pytest.fixture()
def png_bytes():
    """Smallest valid 1x1 PNG file."""
    return (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00'
        b'\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )


@pytest.fixture()
def fake_pdf():
    return b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n%%EOF\n'