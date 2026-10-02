import os
import sys
import urllib.parse

# Ensure project root directory is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

class VercelWSGIMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        query_string = environ.get('QUERY_STRING', '')
        params = urllib.parse.parse_qs(query_string)
        subpath = params.get('path', [None])[0]
        
        if subpath:
            clean = subpath if subpath.startswith('/') else f"/{subpath}"
            environ['PATH_INFO'] = clean
        elif environ.get('PATH_INFO') in ['/api/index.py', '/api/index', '/api', '']:
            environ['PATH_INFO'] = '/'
            
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelWSGIMiddleware(app.wsgi_app)
handler = app
