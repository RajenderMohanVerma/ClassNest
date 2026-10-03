import os

from flask import Flask

from app.config import Config, DevelopmentConfig, ProductionConfig
from app.extensions import db, migrate, csrf, limiter


def create_app(config_class=None):
    app = Flask(__name__, static_folder='static', template_folder='templates')

    if config_class is None:
        env = os.environ.get('FLASK_ENV', 'development')
        config_class = ProductionConfig if env == 'production' else DevelopmentConfig

    app.config.from_object(config_class)

    # Vercel's deployment filesystem is read-only; only /tmp is writable.
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_VERSION'):
        app.config['UPLOAD_FOLDER'] = '/tmp/classnest-uploads'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

    # Ensure uploads use a writable directory in serverless environments.
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except OSError:
        if app.config['UPLOAD_FOLDER'] == '/tmp/classnest-uploads':
            raise
        app.config['UPLOAD_FOLDER'] = '/tmp/classnest-uploads'
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.teacher import teacher_bp
    from app.routes.student import student_bp
    from app.routes.api import api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Context processor — inject branding & user into all templates
    @app.context_processor
    def inject_globals():
        from flask import session
        from app.models.user import User
        user = None
        if 'user_id' in session:
            user = db.session.get(User, session['user_id'])
        return {
            'app_name': app.config['APP_NAME'],
            'app_tagline': app.config['APP_TAGLINE'],
            'current_user': user,
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template('errors/403.html'), 403

    # Serve manifest.json and sw.js from project root
    @app.route('/manifest.json')
    def manifest():
        from flask import send_from_directory
        return send_from_directory(os.path.join(app.root_path, '..'), 'manifest.json')

    @app.route('/sw.js')
    def service_worker():
        from flask import send_from_directory, make_response
        resp = make_response(
            send_from_directory(os.path.join(app.root_path, '..'), 'sw.js')
        )
        resp.headers['Service-Worker-Allowed'] = '/'
        resp.headers['Content-Type'] = 'application/javascript'
        return resp

    return app
