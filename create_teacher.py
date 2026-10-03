"""
Create the initial teacher/admin account securely.
Usage:  python create_teacher.py
"""
import getpass
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models.user import User


def main():
    app = create_app()
    with app.app_context():
        db.create_all()

        print("\n=== ClassNest — Create Teacher Account ===\n")
        name = input("Teacher name: ").strip()
        email = input("Teacher email: ").strip().lower()

        if not name or not email:
            print("Name and email are required.")
            sys.exit(1)

        existing = User.query.filter_by(email=email).first()
        if existing:
            print(f"A user with email '{email}' already exists.")
            sys.exit(1)

        password = getpass.getpass("Password (min 6 chars): ")
        if len(password) < 6:
            print("Password too short.")
            sys.exit(1)

        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match.")
            sys.exit(1)

        teacher = User(name=name, email=email, role='teacher')
        teacher.set_password(password)
        db.session.add(teacher)
        db.session.commit()

        print(f"\n✓ Teacher account created: {email}")
        print("  You can now log in at /auth/login")


if __name__ == '__main__':
    main()
