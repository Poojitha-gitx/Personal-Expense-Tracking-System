"""
Vercel Serverless Function Entry Point
Exposes the Flask WSGI application callable for Vercel's Python runtime.
Includes WSGI path translation to handle Vercel rewrites and static assets seamlessly.
"""

import sys
import os

# Ensure the root project directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app

class VercelPathFix:
    """
    WSGI Middleware to fix Vercel rewrite paths.
    Resolves client requested routes regardless of whether Vercel passes
    the original URL or the rewritten destination.
    Guarantees static assets are never rewritten to HTML endpoints.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')

        # 1. Preserve static files immediately - never rewrite static asset requests
        if path.startswith('/static/'):
            return self.wsgi_app(environ, start_response)

        raw_uri = (
            environ.get('HTTP_X_FORWARDED_URI') or 
            environ.get('RAW_URI') or 
            environ.get('REQUEST_URI') or 
            ''
        )
        if raw_uri:
            raw_path = raw_uri.split('?')[0]
            if raw_path.startswith('/static/'):
                environ['PATH_INFO'] = raw_path
                return self.wsgi_app(environ, start_response)
            if raw_path and not raw_path.startswith('/api/index'):
                environ['PATH_INFO'] = raw_path
                return self.wsgi_app(environ, start_response)

        # 2. Handle /api/index rewrite aliases
        if path.startswith('/api/index.py'):
            remainder = path[len('/api/index.py'):]
            environ['PATH_INFO'] = remainder if remainder else '/'
        elif path.startswith('/api/index'):
            remainder = path[len('/api/index'):]
            environ['PATH_INFO'] = remainder if remainder else '/'
        elif path == '/api' or path == '/api/':
            environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

# Vercel looks for the WSGI application callable named 'app'
app = VercelPathFix(flask_app)
