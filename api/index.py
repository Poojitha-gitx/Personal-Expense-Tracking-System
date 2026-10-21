"""
Vercel Serverless Function Entry Point
Exposes the Flask WSGI application callable for Vercel's Python runtime.
"""

import sys
import os

# Ensure the root project directory is on sys.path for importing app, config, database, analytics
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel looks for the WSGI application callable named 'app'
