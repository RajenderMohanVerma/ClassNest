#!/usr/bin/env python
"""Initialize the ClassNest PostgreSQL database."""

from app import create_app, db
from app.models.user import User
from app.models.subject import Subject
from app.models.content import Content
from app.models.announcement import Announcement
from app.models.uploaded_file import UploadedFile

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        print("[OK] PostgreSQL tables created successfully")
        print("[OK] Models: User, Subject, Content, Announcement, UploadedFile")
        print("\nNext: Run 'python create_teacher.py' to create a teacher account")
