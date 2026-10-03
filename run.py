"""Local and production entry points.

Usage:
    python run.py          # development server on http://127.0.0.1:5000
    gunicorn run:app       # production WSGI server
"""

import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        debug=app.config.get('DEBUG', False),
        host=os.environ.get('HOST', '127.0.0.1'),
        port=int(os.environ.get('PORT', 5000)),
    )