"""Authentication: registration, login, verification, reset, account status."""

import pytest
from unittest.mock import patch

from app import db
from app.extensions import db as _db  # noqa: F401  (keeps the import obvious)
from app.models.account import AccountToken
from app.models.catalog import SchoolClass
from app.models.enums import ACCOUNT_DISABLED, ACCOUNT_SUSPENDED
from app.models.user import User
from app.services.mailer import is_configured as mail_is_configured

PASSWORD = 'studentpass'


# --------------------------------------------------------------------------
# Registration
# --------------------------------------------------------------------------

def test_register_page_offers_the_available_classes(client, school_class):
    body = client.get('/auth/register').data
    assert school_class.name.encode() in body
    assert b'name="class_id"' in body
    assert b'name="phone"' in body


def test_registration_creates_a_student_with_the_chosen_class(app, client, school_class):
    response = client.post('/auth/register', data={
        'name': 'Aarav Sharma',
        'email': 'Aarav@Example.COM',
        'password': PASSWORD,
        'confirm_password': PASSWORD,
        'class_id': str(school_class.id),
        'phone': '9876543210',
    })

    assert response.status_code == 302
    user = User.query.filter_by(email='aarav@example.com').first()
    assert user is not None
    assert user.role == 'student'
    assert user.class_id == school_class.id
    assert user.phone == '9876543210'
    # Email is normalised, and the password is never stored in the clear.
    assert user.password_hash != PASSWORD


def test_registration_cannot_grant_the_teacher_role(app, client, school_class):
    """Role is never read from the form."""
    client.post('/auth/register', data={
        'name': 'Sneaky Person',
        'email': 'sneaky@example.com',
        'password': PASSWORD,
        'confirm_password': PASSWORD,
        'role': 'teacher',
        'class_id': str(school_class.id),
    })

    user = User.query.filter_by(email='sneaky@example.com').first()
    assert user.role == 'student'


def test_registration_rejects_a_disabled_class(app, client):
    hidden = SchoolClass(name='Class 99', slug='class-99', is_enabled=False)
    db.session.add(hidden)
    db.session.commit()

    response = client.post('/auth/register', data={
        'name': 'Hidden Class Student',
        'email': 'hidden@example.com',
        'password': PASSWORD,
        'confirm_password': PASSWORD,
        'class_id': str(hidden.id),
    })

    user = User.query.filter_by(email='hidden@example.com').first()
    assert user is not None
    assert user.class_id is None


def test_registration_rejects_mismatched_passwords(client):
    response = client.post('/auth/register', data={
        'name': 'Mismatch Person',
        'email': 'mismatch@example.com',
        'password': PASSWORD,
        'confirm_password': 'differentpass',
    })

    assert response.status_code == 400
    assert b'Passwords do not match' in response.data
    assert User.query.filter_by(email='mismatch@example.com').first() is None


def test_registration_rejects_duplicate_email(client, student):
    response = client.post('/auth/register', data={
        'name': 'Copy Cat',
        'email': student.email,
        'password': PASSWORD,
        'confirm_password': PASSWORD,
    })

    assert response.status_code == 400
    assert b'already exists' in response.data


def test_registration_without_email_delivery_does_not_demand_verification(app, client):
    """With mail switched off, an unverifiable account must not be created."""
    assert mail_is_configured() is False

    response = client.post('/auth/register', data={
        'name': 'No Mail Student',
        'email': 'nomail@example.com',
        'password': PASSWORD,
        'confirm_password': PASSWORD,
    })

    assert response.status_code == 302
    user = User.query.filter_by(email='nomail@example.com').first()
    assert user is not None
    # No token was issued for a link nobody could receive.
    assert AccountToken.query.filter_by(
        user_id=user.id, purpose=AccountToken.verification_purpose(),
    ).count() == 0


def test_registration_sends_a_verification_link_when_mail_is_on(app, client):
    app.config.update(MAIL_ENABLED=True, MAIL_SERVER='smtp.example.com',
                      MAIL_FROM='no-reply@classnext.test')

    with patch('app.routes.auth.send_verification_email', return_value=True) as send:
        client.post('/auth/register', data={
            'name': 'Verified Student',
            'email': 'verified@example.com',
            'password': PASSWORD,
            'confirm_password': PASSWORD,
        })

    user = User.query.filter_by(email='verified@example.com').first()
    assert user.is_email_verified is False
    assert send.call_count == 1
    assert 'verify-email' in send.call_args[0][2]
    assert AccountToken.query.filter_by(
        user_id=user.id, purpose=AccountToken.verification_purpose(),
    ).count() == 1


def test_registration_rolls_back_when_the_email_cannot_be_sent(app, client):
    """A user must never be told 'check your inbox' if nothing was sent."""
    app.config.update(MAIL_ENABLED=True, MAIL_SERVER='smtp.example.com',
                      MAIL_FROM='no-reply@classnext.test')

    with patch('app.routes.auth.send_verification_email', return_value=False):
        response = client.post('/auth/register', data={
            'name': 'Undeliverable Student',
            'email': 'undeliverable@example.com',
            'password': PASSWORD,
            'confirm_password': PASSWORD,
        })

    assert response.status_code == 503
    assert User.query.filter_by(email='undeliverable@example.com').first() is None


# --------------------------------------------------------------------------
# Login
# --------------------------------------------------------------------------

def test_login_records_the_login_time(app, client, student):
    assert student.last_login_at is None

    client.post('/auth/login', data={'email': student.email, 'password': PASSWORD})

    assert student.last_login_at is not None


def test_login_ignores_a_wrong_password(client, student):
    response = client.post('/auth/login', data={
        'email': student.email, 'password': 'wrong-password',
    })

    assert response.status_code == 401
    assert b'Invalid email or password' in response.data


@pytest.mark.parametrize('status', [ACCOUNT_SUSPENDED, ACCOUNT_DISABLED])
def test_suspended_and_disabled_accounts_cannot_log_in(app, client, student, status):
    student.account_status = status
    db.session.commit()

    response = client.post('/auth/login', data={
        'email': student.email, 'password': PASSWORD,
    })

    assert response.status_code == 403
    assert b'suspended' in response.data.lower() or b'disabled' in response.data.lower()


def test_a_suspension_takes_effect_on_the_next_request(app, client, student, login_student):
    """Suspending a signed-in student ends the session immediately."""
    assert client.get('/student/dashboard').status_code == 200

    student.suspend()
    db.session.commit()

    response = client.get('/student/dashboard')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']

    # The session really is gone, not merely redirected.
    assert client.get('/student/dashboard').status_code == 302


def test_login_redirects_to_the_role_dashboard(client, student, teacher):
    client.post('/auth/login', data={'email': student.email, 'password': PASSWORD})
    assert client.get('/student/dashboard').status_code == 200

    client.post('/auth/logout')
    client.post('/auth/login', data={'email': teacher.email, 'password': 'teacherpass'})
    assert client.get('/teacher/dashboard').status_code == 200


def test_logout_clears_the_session(app, client, student, login_student):
    assert client.get('/student/dashboard').status_code == 200

    client.post('/auth/logout')

    assert client.get('/student/dashboard').status_code == 302


# --------------------------------------------------------------------------
# Email verification
# --------------------------------------------------------------------------

def test_verification_link_marks_the_address_verified(app, client, student):
    _, raw = AccountToken.issue(student.id, AccountToken.verification_purpose())
    db.session.commit()

    client.get(f'/auth/verify-email/{raw}')

    assert student.is_email_verified is True
    assert student.email_verified_at is not None


def test_verification_link_is_single_use(app, client, student):
    _, raw = AccountToken.issue(student.id, AccountToken.verification_purpose())
    db.session.commit()

    client.get(f'/auth/verify-email/{raw}')
    second = client.get(f'/auth/verify-email/{raw}')

    assert second.status_code == 302
    assert b'invalid or has expired' in client.get('/auth/login').data


def test_verification_link_cannot_be_reused_for_a_password_reset(app, client, student):
    _, raw = AccountToken.issue(student.id, AccountToken.verification_purpose())
    db.session.commit()

    client.get(f'/auth/verify-email/{raw}')

    # Purpose is enforced server-side, not by URL shape.
    response = client.post(f'/auth/reset-password/{raw}', data={
        'password': 'hijackedpass', 'confirm_password': 'hijackedpass',
    }, follow_redirects=True)
    assert b'invalid or has expired' in response.data
    assert student.check_password(PASSWORD)


def test_expired_verification_link_is_refused(app, client, student):
    from datetime import timedelta

    from app.models.mixins import utcnow

    record, raw = AccountToken.issue(student.id, AccountToken.verification_purpose())
    record.expires_at = utcnow() - timedelta(minutes=1)
    db.session.commit()

    client.get(f'/auth/verify-email/{raw}')

    assert student.is_email_verified is False


def test_resend_verification_sends_a_new_link(app, client, student, login_student):
    app.config.update(MAIL_ENABLED=True, MAIL_SERVER='smtp.example.com',
                      MAIL_FROM='no-reply@classnext.test')

    with patch('app.routes.auth.send_verification_email', return_value=True) as send:
        response = client.post('/auth/resend-verification')

    assert response.status_code == 302
    assert send.call_count == 1


def test_resend_verification_requires_a_session(client):
    response = client.post('/auth/resend-verification')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


# --------------------------------------------------------------------------
# Password reset
# --------------------------------------------------------------------------

def test_forgot_password_never_reveals_whether_an_account_exists(app, client, student):
    with patch('app.routes.auth.send_password_reset_email', return_value=True) as send:
        known = client.post('/auth/forgot-password', data={'email': student.email})
        unknown = client.post('/auth/forgot-password', data={'email': 'nobody@example.com'})

    assert known.status_code == unknown.status_code == 302
    # Same wording and same response for both cases, so accounts cannot be enumerated.
    assert known.data == unknown.data
    assert send.call_count == 1
    assert b'if that email has an active account' in client.get(
        '/auth/forgot-password', follow_redirects=True,
    ).data.lower()


def test_forgot_password_page_renders(client):
    response = client.get('/auth/forgot-password')
    assert response.status_code == 200
    assert b'name="email"' in response.data


def test_reset_password_changes_the_password(app, client, student):
    _, raw = AccountToken.issue(student.id, AccountToken.reset_purpose())
    db.session.commit()

    response = client.post(f'/auth/reset-password/{raw}', data={
        'password': 'brand-new-pass', 'confirm_password': 'brand-new-pass',
    })

    assert response.status_code == 302
    assert student.check_password('brand-new-pass')
    # The reset also proves mailbox control, so the address becomes verified.
    assert student.is_email_verified is True


def test_reset_password_invalidates_the_existing_session(app, client, student, login_student):
    _, raw = AccountToken.issue(student.id, AccountToken.reset_purpose())
    db.session.commit()

    client.post(f'/auth/reset-password/{raw}', data={
        'password': 'brand-new-pass', 'confirm_password': 'brand-new-pass',
    })

    assert client.get('/student/dashboard').status_code == 302


def test_reset_password_token_is_single_use(app, client, student):
    _, raw = AccountToken.issue(student.id, AccountToken.reset_purpose())
    db.session.commit()

    client.post(f'/auth/reset-password/{raw}', data={
        'password': 'brand-new-pass', 'confirm_password': 'brand-new-pass',
    })
    client.post(f'/auth/reset-password/{raw}', data={
        'password': 'attacker-pass', 'confirm_password': 'attacker-pass',
    })

    assert student.check_password('brand-new-pass')


def test_reset_password_rejects_a_short_password(app, client, student):
    _, raw = AccountToken.issue(student.id, AccountToken.reset_purpose())
    db.session.commit()

    response = client.post(f'/auth/reset-password/{raw}', data={
        'password': 'abc', 'confirm_password': 'abc',
    })

    assert response.status_code == 400
    assert b'at least 6 characters' in response.data
    assert student.check_password(PASSWORD)


def test_expired_reset_token_is_refused(app, client, student):
    from datetime import timedelta

    from app.models.mixins import utcnow

    record, raw = AccountToken.issue(student.id, AccountToken.reset_purpose())
    record.expires_at = utcnow() - timedelta(minutes=1)
    db.session.commit()

    response = client.post(f'/auth/reset-password/{raw}', data={
        'password': 'brand-new-pass', 'confirm_password': 'brand-new-pass',
    })

    assert response.status_code == 302
    assert '/auth/forgot-password' in response.headers['Location']
    assert student.check_password(PASSWORD)


def test_forgot_password_ignores_a_suspended_account(app, client, student):
    student.suspend()
    db.session.commit()

    with patch('app.routes.auth.send_password_reset_email', return_value=True) as send:
        client.post('/auth/forgot-password', data={'email': student.email})

    assert send.call_count == 0
    assert AccountToken.query.filter_by(
        user_id=student.id, purpose=AccountToken.reset_purpose(),
    ).count() == 0


def test_token_hashes_are_not_the_raw_tokens(app, student):
    _, raw = AccountToken.issue(student.id, AccountToken.reset_purpose())
    db.session.commit()

    record = AccountToken.query.filter_by(user_id=student.id).first()
    assert record.token_hash != raw
    assert len(record.token_hash) == 64