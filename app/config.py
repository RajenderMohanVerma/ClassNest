import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

    # Supabase and other managed PostgreSQL providers may return postgres://.
    db_url = os.environ.get('DATABASE_URL', '').strip()
    if db_url.startswith('postgres://'):
        db_url = f'postgresql://{db_url[len("postgres://"):]}'
    if not db_url.startswith(('postgresql://', 'postgresql+psycopg2://')):
        raise RuntimeError(
            'DATABASE_URL must be a PostgreSQL connection string. '
            'Set it to the Supabase connection pooler URL.'
        )
    SQLALCHEMY_DATABASE_URI = db_url
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # Uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'app/static/uploads')
    MAX_UPLOAD_MB = int(os.environ.get('MAX_UPLOAD_MB', 16))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024

    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt',
                          'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}

    # Branding
    APP_NAME = os.environ.get('APP_NAME', 'ClassNest')
    APP_TAGLINE = os.environ.get('APP_TAGLINE', 'Teacher & Student Learning Portal')


class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    FLASK_DEBUG = False


class DevelopmentConfig(Config):
    SESSION_COOKIE_SECURE = False
    FLASK_DEBUG = True
