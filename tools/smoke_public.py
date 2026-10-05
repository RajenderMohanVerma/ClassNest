"""Smoke-test every public ClassNext route against seeded data."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db  # noqa: E402
from app.config import TestingConfig  # noqa: E402
from app.models import (  # noqa: E402
    Announcement,
    Chapter,
    Content,
    Course,
    CourseLesson,
    CourseSection,
    Faq,
    SchoolClass,
    Subject,
    User,
)

PATHS = [
    '/', '/classes', '/notes', '/videos', '/free-resources', '/courses',
    '/premium', '/notices', '/about', '/faq', '/contact',
    '/legal/privacy', '/legal/terms', '/legal/refund-policy',
    '/search?q=math', '/sitemap.xml', '/robots.txt',
]


def seed():
    teacher = User(name='Er. Amit Sir', email='teacher@example.com', role='teacher')
    teacher.set_password('teacherpass')
    db.session.add(teacher)
    db.session.flush()

    school_class = SchoolClass(
        name='Class 10', slug=SchoolClass.unique_slug('Class 10'),
        description='Secondary stage', created_by=teacher.id,
    )
    db.session.add(school_class)
    db.session.flush()

    subject = Subject(
        name='Mathematics', slug=Subject.unique_slug('Mathematics'),
        description='Numbers, algebra and geometry', icon='bi-calculator',
        class_id=school_class.id, created_by=teacher.id,
    )
    db.session.add(subject)
    db.session.flush()

    chapter = Chapter(
        title='Real Numbers', slug=Chapter.unique_slug('Real Numbers'),
        subject_id=subject.id, class_id=school_class.id,
        status='published', created_by=teacher.id,
    )
    db.session.add(chapter)
    db.session.flush()

    note = Content(
        title='Properties of Real Numbers',
        slug=Content.unique_slug('Properties of Real Numbers'),
        description='A complete note on real number properties.',
        subject_id=subject.id, chapter_id=chapter.id, class_id=school_class.id,
        content_type='notes', body_html='<p>Closure, commutativity, associativity.</p>',
        tags='Revision, Important', access_level='public', created_by=teacher.id,
    )
    note.publish()
    db.session.add(note)

    video = Content(
        title='Introduction to Vectors',
        slug=Content.unique_slug('Introduction to Vectors'),
        subject_id=subject.id, class_id=school_class.id,
        content_type='video_lesson', video_url='https://example.com/embed/abc',
        access_level='public', created_by=teacher.id,
    )
    video.publish()
    db.session.add(video)
    db.session.flush()

    course = Course(
        title='Class 10 Mathematics Complete Course',
        slug=Course.unique_slug('Class 10 Mathematics Complete Course'),
        description='Full syllabus course with sections and lessons.',
        class_id=school_class.id, subject_id=subject.id, instructor_id=teacher.id,
        price=499, discount_price=399, access_level='premium',
        status='published', created_by=teacher.id,
    )
    course.published_at = course.created_at
    db.session.add(course)
    db.session.flush()

    section = CourseSection(course_id=course.id, title='Chapter 1', slug='chapter-1')
    db.session.add(section)
    db.session.flush()

    notice = Announcement(
        title='New notes published', body='<p>Check the new chapter.</p>',
        created_by=teacher.id,
    )
    notice.publish()
    db.session.add(notice)

    faq = Faq(
        question='How do I access a premium course?',
        answer='<p>Buy it, then payment is verified on the server.</p>',
        category='Getting started', status='published',
    )
    db.session.add(faq)
    db.session.flush()

    db.session.add(CourseLesson(
        course_id=course.id, section_id=section.id, content_id=note.id,
        title='Properties of Real Numbers', is_preview=True,
    ))
    db.session.add(CourseLesson(
        course_id=course.id, section_id=section.id, content_id=video.id,
        title='Introduction to Vectors',
    ))
    db.session.commit()

    return {
        'class': school_class, 'subject': subject, 'chapter': chapter,
        'note': note, 'video': video, 'course': course,
    }


def main():
    app = create_app(TestingConfig)
    failures = []

    with app.app_context():
        db.create_all()
        refs = seed()

        paths = PATHS + [
            f"/classes/{refs['class'].slug}",
            f"/subjects/{refs['subject'].slug}",
            f"/chapters/{refs['chapter'].slug}",
            f"/content/{refs['note'].slug}",
            f"/content/{refs['video'].slug}",
            f"/courses/{refs['course'].slug}",
        ]

        client = app.test_client()
        for path in paths:
            response = client.get(path)
            status = response.status_code
            flag = 'OK ' if status < 400 else 'BAD'
            if status >= 400:
                failures.append((path, status))
            print(f'  {flag} {status} {path}')

        # Negative checks: a missing record must 404, not 500.
        print()
        for path in ('/classes/does-not-exist', '/content/does-not-exist',
                     '/courses/does-not-exist', '/legal/nope'):
            status = client.get(path).status_code
            verdict = 'OK ' if status == 404 else 'BAD'
            if status != 404:
                failures.append((path, status))
            print(f'  {verdict} {status} {path} (expected 404)')

    print()
    if failures:
        print('FAILURES:', failures)
        return 1
    print('All public routes responded without a server error.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())