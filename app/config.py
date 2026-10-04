import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

DEFAULT_SECRET_KEY = 'dev-secret-change-me'


def _env_flag(name, default='0'):
    return os.environ.get(name, default).strip().lower() in {'1', 'true', 'yes', 'on'}


def normalize_database_url(url):
    """Normalize any supported PostgreSQL URL to the psycopg2 driver form.

    Vercel and Supabase hand out ``postgres://`` and ``postgresql+psycopg://``
    URLs; SQLAlchemy 2.x with psycopg2 needs ``postgresql+psycopg2://``.
    """
    url = (url or '').strip()
    if not url:
        return ''
    if url.startswith('postgres://'):
        url = f'postgresql://{url[len("postgres://"):]}'
    if url.startswith('postgresql+psycopg://'):
        return f'postgresql+psycopg2://{url[len("postgresql+psycopg://"):]}'
    if url.startswith('postgresql://'):
        return f'postgresql+psycopg2://{url[len("postgresql://"):]}'
    return url


class Config:
    ENV_NAME = os.environ.get('FLASK_ENV', 'development')
    IS_PRODUCTION = ENV_NAME == 'production'

    SECRET_KEY = os.environ.get('SECRET_KEY') or DEFAULT_SECRET_KEY

    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    SQLALCHEMY_DATABASE_URI = normalize_database_url(DATABASE_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }

    # Session security
    SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME', 'classnest_session')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.environ.get('SESSION_HOURS', 8))
    )
    SESSION_REFRESH_EACH_REQUEST = False

    # Uploads live outside app/static so files cannot be read without auth.
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join('instance', 'uploads'))
    LEGACY_UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    MAX_UPLOAD_MB = int(os.environ.get('MAX_UPLOAD_MB', 16))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024

    # svg is deliberately excluded: it can carry scripts.
    ALLOWED_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx',
        'txt', 'md', 'csv', 'rtf',
        'png', 'jpg', 'jpeg', 'gif', 'webp',
    }

    # Content types and publication states (mirrored by DB CHECK constraints)
    CONTENT_TYPES = (
        'notes', 'study_material', 'pdf_resource',
        'video_lesson', 'announcement', 'reference_link',
    )
    CONTENT_STATUSES = ('draft', 'published')

    # Rate limiting (in-memory unless a Redis/memcached URI is supplied)
    RATELIMIT_STORAGE_URI = os.environ.get('RATE_LIMIT_STORAGE_URI') or 'memory://'
    RATELIMIT_DEFAULT = os.environ.get('RATE_LIMIT_DEFAULT', '300 per hour')
    RATELIMIT_HEADERS_ENABLED = True

    # Security headers
    SECURITY_HEADERS_ENABLED = _env_flag('SECURITY_HEADERS_ENABLED', '1')
    CONTENT_SECURITY_POLICY = os.environ.get('CONTENT_SECURITY_POLICY') or (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net "
        "https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net data:; "
        "img-src 'self' data: blob:; "
        "media-src 'self' https:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "object-src 'none'"
    )

    # Branding
    APP_NAME = os.environ.get('APP_NAME', 'ClassNest')
    APP_TAGLINE = os.environ.get('APP_TAGLINE', 'Teacher & Student Learning Portal')
    APP_DESCRIPTION = os.environ.get(
        'APP_DESCRIPTION',
        'ClassNest - Your Smart Learning Companion',
    )
    THEME_COLOR = os.environ.get('THEME_COLOR', '#4f35e8')

    DEBUG = _env_flag('FLASK_DEBUG', '0')

    @classmethod
    def validate(cls, app_config):
        """Fail fast with an actionable message instead of a driver error."""
        uri = app_config.get('SQLALCHEMY_DATABASE_URI', '')
        if app_config.get('TESTING') and uri.startswith('sqlite:'):
            return
        if not uri:
            raise RuntimeError(
                'DATABASE_URL is not set. Copy .env.example to .env and set the '
                'Supabase PostgreSQL connection string before starting the app.'
            )
        if not uri.startswith('postgresql+psycopg2://'):
            raise RuntimeError(
                'DATABASE_URL must be a PostgreSQL connection string '
                '(postgresql://user:password@host:5432/dbname). Set it to the '
                'Supabase Session Pooler URL before starting the app.'
            )
        if (
            app_config.get('IS_PRODUCTION')
            and app_config.get('SECRET_KEY') == DEFAULT_SECRET_KEY
        ):
            raise RuntimeError(
                'SECRET_KEY must be set to a unique random value in production. '
                'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
            )


class ProductionConfig(Config):
    ENV_NAME = 'production'
    IS_PRODUCTION = True
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    DEBUG = False


class DevelopmentConfig(Config):
    ENV_NAME = 'development'
    IS_PRODUCTION = False
    SESSION_COOKIE_SECURE = False
    DEBUG = Config.DEBUG


class TestingConfig(Config):
    """Isolated configuration for the automated test-suite.

    Tests run against an in-memory SQLite database so they never touch the
    PostgreSQL instance used for development or production.
    """

    ENV_NAME = 'testing'
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite://')
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    SESSION_COOKIE_SECURE = False
    UPLOAD_FOLDER = os.environ.get(
        'TEST_UPLOAD_FOLDER',
        os.path.join('instance', 'test-uploads'),
    )