import os

from flask import Flask, abort, flash, g, jsonify, render_template

from app.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from app.extensions import csrf, db, limiter, migrate
from app.services.pagination import pagination_args


def create_app(config_class=None):
    app = Flask(__name__, static_folder='static', template_folder='templates')

    if config_class is None:
        env = os.environ.get('FLASK_ENV', 'development').strip().lower()
        config_class = {
            'production': ProductionConfig,
            'testing': TestingConfig,
        }.get(env, DevelopmentConfig)

    app.config.from_object(config_class)
    Config.validate(app.config)

    # Vercel's deployment filesystem is read-only; only /tmp is writable.
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_VERSION'):
        app.config['UPLOAD_FOLDER'] = '/tmp/classnext-uploads'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

    _ensure_upload_folder(app)

    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.teacher import teacher_bp
    from app.routes.student import student_bp
    from app.routes.api import api_bp
    from app.routes.files import files_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(files_bp, url_prefix='/files')

    app.jinja_env.globals['pagination_args'] = pagination_args

    # Context processor: inject branding & user into all templates
    @app.context_processor
    def inject_globals():
        from datetime import datetime

        from flask import session
        from app.models.content import CONTENT_TYPE_LABELS
        from app.models.enums import ACCESS_LEVEL_LABELS, CONTENT_STATUS_LABELS
        from app.models.user import User
        # Reuse the user loaded by the account-status check instead of
        # querying the same row again on every template render.
        user = getattr(g, 'current_user', None)
        if user is None and session.get('user_id'):
            user = db.session.get(User, session['user_id'])
        return {
            'app_name': app.config['APP_NAME'],
            'app_tagline': app.config['APP_TAGLINE'],
            'app_description': app.config['APP_DESCRIPTION'],
            'theme_color': app.config['THEME_COLOR'],
            'teacher_name': app.config['TEACHER_NAME'],
            'site_url': app.config['SITE_URL'],
            'premium_enabled': app.config['PREMIUM_ENABLED'],
            'current_year': datetime.now().year,
            'content_type_labels': CONTENT_TYPE_LABELS,
            'content_status_labels': CONTENT_STATUS_LABELS,
            'access_level_labels': ACCESS_LEVEL_LABELS,
            'current_user': user,
        }

    # Error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return _render_error('errors/400.html', 400, 'Bad request',
                             'The request could not be understood.')

    @app.errorhandler(403)
    def forbidden(e):
        return _render_error('errors/403.html', 403, 'Access denied',
                             "You don't have permission to view this resource.")

    @app.errorhandler(404)
    def not_found(e):
        return _render_error('errors/404.html', 404, 'Page not found',
                             "The page you're looking for doesn't exist or has moved.")

    @app.errorhandler(413)
    def request_too_large(e):
        max_mb = app.config['MAX_UPLOAD_MB']
        return _render_error(
            'errors/413.html', 413, 'File too large',
            f'Uploads are limited to {max_mb} MB.', status_message=None,
        )

    @app.errorhandler(429)
    def rate_limited(e):
        return _render_error(
            'errors/429.html', 429, 'Too many requests',
            'Please wait a moment and try again.', status_message=None,
        )

    @app.errorhandler(500)
    def server_error(e):
        return _render_error('errors/500.html', 500, 'Server error',
                             'Something went wrong on our side. Please try again.')

    def _render_error(template, status, title, message, status_message=True):
        from flask import session
        user = None
        if session.get('user_id'):
            from app.models.user import User
            user = db.session.get(User, session['user_id'])
        if status_message and request_wants_json():
            return jsonify({'error': title, 'message': message, 'status': status}), status
        return render_template(
            template,
            error_title=title,
            error_message=message,
            error_status=status,
            current_user=user,
        ), status

    def request_wants_json():
        from flask import request
        return request.path.startswith('/api/') or request.accept_mimetypes.best == 'application/json'

    @app.route('/favicon.ico')
    def favicon():
        """Browsers request /favicon.ico by default, outside the static route."""
        from flask import send_from_directory
        return send_from_directory(
            os.path.join(app.root_path, 'static'), 'favicon.ico', max_age=86400
        )

    # Serve PWA metadata and the service worker from the project root
    @app.route('/manifest.webmanifest')
    def web_manifest():
        """Web app manifest for installable PWAs."""
        from flask import make_response, send_from_directory
        response = make_response(
            send_from_directory(
                os.path.join(app.root_path, '..'),
                'manifest.webmanifest',
                mimetype='application/manifest+json',
            )
        )
        response.headers['Cache-Control'] = 'no-cache'
        return response

    @app.route('/manifest.json')
    def manifest():
        """Legacy alias so already-installed PWAs keep working."""
        from flask import make_response, send_from_directory
        response = make_response(
            send_from_directory(
                os.path.join(app.root_path, '..'),
                'manifest.webmanifest',
                mimetype='application/manifest+json',
            )
        )
        response.headers['Cache-Control'] = 'no-cache'
        return response

    @app.route('/sw.js')
    def service_worker():
        from flask import send_from_directory, make_response
        response = make_response(
            send_from_directory(os.path.join(app.root_path, '..'), 'sw.js')
        )
        response.headers['Service-Worker-Allowed'] = '/'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Content-Type'] = 'application/javascript'
        return response

    @app.route('/healthz')
    def healthz():
        """Deployment smoke-test endpoint: verifies the database is reachable."""
        from sqlalchemy import text
        try:
            db.session.execute(text('SELECT 1'))
            database = 'ok'
        except Exception:
            db.session.rollback()
            database = 'error'
        payload = {
            'status': 'ok' if database == 'ok' else 'degraded',
            'database': database,
            'app': app.config['APP_NAME'],
        }
        return jsonify(payload), 200 if database == 'ok' else 503

    @app.before_request
    def protect_legacy_uploads_and_cache():
        """Never serve uploads from the static tree, never cache app pages."""
        from flask import request, session

        if request.path.startswith('/static/uploads/'):
            abort(404)

        if (
            'user_id' in session
            and request.method == 'GET'
            and not request.path.startswith('/static/')
            and request.accept_mimetypes.best != 'application/json'
        ):
            g.no_store = True

    @app.before_request
    def enforce_account_status():
        """End the session as soon as an account is suspended or deleted.

        Checking only at login is not enough: an admin suspending a student must
        take effect on the student's very next request, not at their next login.
        """
        from flask import redirect, request, session, url_for

        user_id = session.get('user_id')
        if not user_id:
            return None

        if request.path.startswith('/static/') or request.path.startswith('/auth/logout'):
            return None

        from app.models.user import User
        user = db.session.get(User, user_id)

        if user is None:
            session.clear()
            flash('Your account is no longer available. Please contact the teacher.', 'error')
            return redirect(url_for('auth.login'))

        if not user.can_login:
            session.clear()
            flash(
                f'Your account has been {user.account_status_label.lower()}. '
                f'Please contact the teacher.',
                'error',
            )
            return redirect(url_for('auth.login'))

        # Keep the cached role and name honest even if they were changed.
        if session.get('user_role') != user.role or session.get('user_name') != user.name:
            session['user_role'] = user.role
            session['user_name'] = user.name

        g.current_user = user
        return None

    @app.after_request
    def no_store_authenticated_pages(response):
        if getattr(g, 'no_store', False):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        return response

    @app.after_request
    def security_headers(response):
        if not app.config.get('SECURITY_HEADERS_ENABLED', True):
            return response
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault('Permissions-Policy',
                                    'camera=(), microphone=(), geolocation=()')
        response.headers.setdefault('Content-Security-Policy',
                                    app.config['CONTENT_SECURITY_POLICY'])
        if app.config.get('IS_PRODUCTION'):
            response.headers.setdefault(
                'Strict-Transport-Security', 'max-age=31536000; includeSubDomains'
            )
        return response

    return app


def _ensure_upload_folder(app):
    """Guarantee a writable upload directory, including serverless runtimes."""
    folder = app.config['UPLOAD_FOLDER']
    try:
        os.makedirs(folder, exist_ok=True)
        return
    except OSError:
        pass
    if folder == '/tmp/classnext-uploads':
        raise
    app.config['UPLOAD_FOLDER'] = '/tmp/classnext-uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)