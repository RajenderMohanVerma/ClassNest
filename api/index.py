"""Vercel entry point for the ClassNext Flask application."""

import os


database_url = os.environ.get('DATABASE_URL', '')
if database_url.startswith('postgresql+psycopg://'):
    os.environ['DATABASE_URL'] = database_url.replace(
        'postgresql+psycopg://',
        'postgresql+psycopg2://',
        1,
    )

from app import create_app

app = create_app()
