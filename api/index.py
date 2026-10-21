"""
Vercel Serverless Function Entry Point
Exposes the Flask WSGI application callable for Vercel's Python runtime.
Includes WSGI path translation to handle Vercel rewrites and static assets seamlessly.
"""

import sys
import os
import urllib.parse

# Ensure the root project directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app

class VercelPathFix:
    """
    WSGI Middleware to fix Vercel rewrite paths.
    Ensures that /expenses, /analytics, /reports, /categories, and /static/...
    reach Flask with their exact, intended route paths.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        query_string = environ.get('QUERY_STRING', '')

        # 1. Preserve static files immediately
        if path.startswith('/static/'):
            return self.wsgi_app(environ, start_response)

        # 2. Check for explicit __vercel_route__ parameter injected by vercel.json
        resolved_path = None
        if '__vercel_route__=' in query_string:
            params = urllib.parse.parse_qs(query_string, keep_blank_values=True)
            if '__vercel_route__' in params:
                route_val = params.pop('__vercel_route__')[0]
                if route_val:
                    if not route_val.startswith('/'):
                        route_val = '/' + route_val
                    resolved_path = route_val
                # Clean up query string so Flask request.args stays clean
                environ['QUERY_STRING'] = urllib.parse.urlencode(params, doseq=True)

        # 3. If __vercel_route__ was not present, inspect headers provided by Vercel
        if not resolved_path:
            raw_uri = (
                environ.get('HTTP_X_FORWARDED_URI') or 
                environ.get('HTTP_X_FORWARDED_URL') or 
                environ.get('HTTP_X_ORIGINAL_URI') or 
                environ.get('HTTP_X_REWRITE_URL') or 
                ''
            )
            if raw_uri:
                clean_path = raw_uri.split('?')[0]
                if clean_path.startswith('http://') or clean_path.startswith('https://'):
                    parsed = urllib.parse.urlparse(clean_path)
                    clean_path = parsed.path
                if clean_path and not clean_path.startswith('/api/index'):
                    resolved_path = clean_path

        # 4. If path had /api/index prefix with a real subpath, strip the prefix
        if not resolved_path:
            if path.startswith('/api/index.py/'):
                resolved_path = path[len('/api/index.py'):]
            elif path.startswith('/api/index/'):
                resolved_path = path[len('/api/index'):]
            elif path.startswith('/api/'):
                resolved_path = path[len('/api'):]
            elif path not in ('/api/index.py', '/api/index', '/api', ''):
                resolved_path = path

        # Set resolved path (default to root '/' only if path is completely empty)
        environ['PATH_INFO'] = resolved_path if resolved_path else '/'

        return self.wsgi_app(environ, start_response)

# Vercel looks for the WSGI application callable named 'app'
app = VercelPathFix(flask_app)
