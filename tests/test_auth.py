"""Authentication, session and role-enforcement tests."""

from app.models import User


def test_public_root_redirects_to_login(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


def test_login_page_renders(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'ClassNest' in response.data


def test_login_with_valid_credentials(client, teacher, login):
    response = login(teacher.email, 'teacherpass')
    assert response.status_code == 302
    assert '/teacher/dashboard' in response.headers['Location']


def test_login_with_invalid_password_is_rejected(client, teacher, login):
    response = login(teacher.email, 'wrong-password')
    assert response.status_code == 401
    assert b'Invalid email or password' in response.data


def test_login_ignores_attempted_role_escalation(client, student, login):
    response = login(student.email, 'studentpass')
    assert response.status_code == 302
    assert '/student/dashboard' in response.headers['Location']
    with client.session_transaction() as session:
        assert session['user_role'] == 'student'


def test_login_honours_safe_next_parameter(client, teacher, login):
    response = client.post(
        '/auth/login?next=/student/content',
        data={'email': teacher.email, 'password': 'teacherpass'},
    )
    assert response.status_code == 302
    assert response.headers['Location'] == '/student/content'


def test_login_ignores_external_next_parameter(client, teacher):
    response = client.post(
        '/auth/login?next=https://evil.example/steal',
        data={'email': teacher.email, 'password': 'teacherpass'},
    )
    assert response.status_code == 302
    assert response.headers['Location'] == '/teacher/dashboard'


def test_registration_creates_student_only(client, app):
    response = client.post(
        '/auth/register',
        data={
            'name': 'New Student',
            'email': 'new.student@example.com',
            'password': 'secret123',
            'confirm_password': 'secret123',
        },
    )
    assert response.status_code == 302
    user = User.query.filter_by(email='new.student@example.com').first()
    assert user is not None
    assert user.role == 'student'
    assert user.password_hash != 'secret123'


def test_registration_rejects_duplicate_email(client, student):
    response = client.post(
        '/auth/register',
        data={
            'name': 'Copy Cat',
            'email': student.email,
            'password': 'secret123',
            'confirm_password': 'secret123',
        },
    )
    assert response.status_code == 400
    assert b'already exists' in response.data


def test_registration_validates_fields(client):
    response = client.post(
        '/auth/register',
        data={
            'name': 'A',
            'email': 'not-an-email',
            'password': '123',
            'confirm_password': '456',
        },
    )
    assert response.status_code == 400
    body = response.data
    assert b'valid email address' in body
    assert b'at least 6 characters' in body
    assert b'do not match' in body


def test_registration_does_not_allow_role_field(client):
    client.post(
        '/auth/register',
        data={
            'name': 'Sneaky',
            'email': 'sneaky@example.com',
            'password': 'secret123',
            'confirm_password': 'secret123',
            'role': 'teacher',
        },
    )
    user = User.query.filter_by(email='sneaky@example.com').first()
    assert user.role == 'student'


def test_logout_requires_post(client, login_student):
    login_student()
    assert client.get('/auth/logout').status_code == 405

    response = client.post('/auth/logout')
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert 'user_id' not in session


def test_protected_routes_redirect_anonymous_users(client):
    for path in ('/teacher/dashboard', '/student/dashboard', '/student/content'):
        response = client.get(path)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']


def test_student_cannot_open_teacher_routes(client, login_student):
    login_student()
    for path in (
        '/teacher/dashboard',
        '/teacher/content',
        '/teacher/subjects',
        '/teacher/students',
        '/teacher/files',
        '/teacher/announcements',
        '/teacher/profile',
    ):
        assert client.get(path).status_code == 403, path


def test_student_cannot_post_teacher_mutations(client, login_student, subject):
    login_student()
    response = client.post(
        '/teacher/subjects',
        data={'name': 'Hijacked'},
        follow_redirects=False,
    )
    assert response.status_code == 403


def test_teacher_cannot_open_student_routes(client, login_teacher):
    login_teacher()
    for path in (
        '/student/dashboard',
        '/student/content',
        '/student/subjects',
        '/student/announcements',
    ):
        assert client.get(path).status_code == 403, path


def test_healthz_reports_database_status(client):
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.get_json()['database'] == 'ok'


def test_security_headers_present(client):
    response = client.get('/auth/login')
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['X-Frame-Options'] == 'DENY'
    assert 'Content-Security-Policy' in response.headers


def test_api_stats_requires_teacher(client, login_student, published_content):
    login_student()
    response = client.get('/api/stats')
    assert response.status_code == 403
    assert response.get_json()['error'] == 'Unauthorized'


def test_api_stats_returns_teacher_totals(client, login_teacher, published_content, content):
    login_teacher()
    payload = client.get('/api/stats').get_json()
    assert payload['total_content'] == 2
    assert payload['published'] == 1
    assert payload['drafts'] == 1


def test_missing_page_returns_404_page(client):
    response = client.get('/does-not-exist')
    assert response.status_code == 404
    assert b'404' in response.data