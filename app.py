import os
from flask import Flask, send_from_directory
from config import Config
from backend.database import init_db
from backend.routes import api, main_views

def create_app(config_class=Config):
    """Application factory for InvisiFace Flask application."""
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'frontend', 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'frontend', 'static'),
        static_url_path='/static'
    )
    
    app.config.from_object(config_class)
    config_class.init_app()

    # Initialize Database
    init_db(app)

    # Register Blueprints
    app.register_blueprint(main_views)
    app.register_blueprint(api, url_prefix='/api')

    # Serve static assets from uploads, outputs, and encrypted directories for frontend display
    @app.route('/media/uploads/<path:filename>')
    def serve_uploads(filename):
        return send_from_directory(str(Config.UPLOAD_FOLDER), filename)

    @app.route('/media/outputs/<path:filename>')
    def serve_outputs(filename):
        return send_from_directory(str(Config.OUTPUT_FOLDER), filename)

    @app.route('/media/encrypted/<path:filename>')
    def serve_encrypted(filename):
        return send_from_directory(str(Config.ENCRYPTED_FOLDER), filename)

    # Wrap WSGI app with Vercel subpath rewrite handler
    class VercelWSGIMiddleware:
        def __init__(self, wsgi_app):
            self.wsgi_app = wsgi_app

        def __call__(self, environ, start_response):
            query_string = environ.get('QUERY_STRING', '')
            if 'path=' in query_string:
                import urllib.parse
                params = urllib.parse.parse_qs(query_string)
                subpath = params.get('path', [None])[0]
                if subpath:
                    clean = subpath if subpath.startswith('/') else f"/{subpath}"
                    environ['PATH_INFO'] = clean
                    environ['SCRIPT_NAME'] = ''
            return self.wsgi_app(environ, start_response)

    app.wsgi_app = VercelWSGIMiddleware(app.wsgi_app)
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"\n=======================================================")
    print(f"   InvisiFace Quantum Anonymization Engine Server")
    print(f"   Status: ONLINE")
    print(f"   Local URL: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
