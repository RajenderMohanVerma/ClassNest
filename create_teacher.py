"""Create the initial teacher/admin account securely.

Usage:
    python create_teacher.py

Optional environment overrides:
    TEACHER_NAME, TEACHER_EMAIL  — skip the prompts for those fields.
The password is always entered through a hidden prompt and never stored in
source control, logs, or the shell history.
"""

import getpass
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_validator import EmailNotValidError, validate_email  # noqa: E402

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models.user import User  # noqa: E402

MIN_PASSWORD_LENGTH = 8


def main():
    app = create_app()
    with app.app_context():
        db.create_all()

        print('\n=== ClassNext - Create Teacher Account ===\n')

        name = os.environ.get('TEACHER_NAME', '').strip() or input('Teacher name: ').strip()
        email = os.environ.get('TEACHER_EMAIL', '').strip().lower()
        if not email:
            email = input('Teacher email: ').strip().lower()

        if len(name) < 2:
            print('Name must be at least 2 characters.')
            sys.exit(1)

        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            print('Please enter a valid email address.')
            sys.exit(1)

        if User.query.filter_by(email=email).first():
            print(f"A user with email '{email}' already exists.")
            sys.exit(1)

        password = getpass.getpass(f'Password (min {MIN_PASSWORD_LENGTH} chars): ')
        if len(password) < MIN_PASSWORD_LENGTH:
            print(f'Password must be at least {MIN_PASSWORD_LENGTH} characters.')
            sys.exit(1)

        confirm = getpass.getpass('Confirm password: ')
        if password != confirm:
            print('Passwords do not match.')
            sys.exit(1)

        teacher = User(name=name, email=email, role='teacher')
        teacher.set_password(password)
        db.session.add(teacher)
        db.session.commit()

        print(f'\nTeacher account created: {email}')
        print('Sign in at /auth/login and change the password after the first login.')


if __name__ == '__main__':
    try:
        main()
    except RuntimeError as error:
        print(f'[ERROR] {error}')
        sys.exit(1)
