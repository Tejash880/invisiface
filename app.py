import os
from flask import Flask, send_from_directory
from config import Config
from backend.database import init_db
from backend.routes import api, main_views

def create_app(config_class=Config):
    """Application factory for InvisiFace Flask application."""
    app = Flask(
        __name__,
        template_folder='frontend/templates',
        static_folder='frontend/static'
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
        return send_from_directory(Config.UPLOAD_FOLDER, filename)

    @app.route('/media/outputs/<path:filename>')
    def serve_outputs(filename):
        return send_from_directory(Config.OUTPUT_FOLDER, filename)

    @app.route('/media/encrypted/<path:filename>')
    def serve_encrypted(filename):
        return send_from_directory(Config.ENCRYPTED_FOLDER, filename)

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
