"""
Vercel Serverless Function Entry Point
Exposes the Flask WSGI application callable for Vercel's Python runtime.
Includes WSGI path translation to handle Vercel rewrites seamlessly.
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
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        
        # Check if Vercel provided the original requested path in headers
        raw_uri = (
            environ.get('HTTP_X_FORWARDED_URI') or 
            environ.get('HTTP_X_MATCHED_PATH') or 
            environ.get('REQUEST_URI')
        )
        if raw_uri:
            # Strip query parameters if present
            raw_path = raw_uri.split('?')[0]
            if raw_path and not raw_path.startswith('/api/index'):
                environ['PATH_INFO'] = raw_path
        elif path.startswith('/api/index.py'):
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
