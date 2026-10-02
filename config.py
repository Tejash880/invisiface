import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if available
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

IS_VERCEL = bool(os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'))
STORAGE_DIR = Path('/tmp') if IS_VERCEL else BASE_DIR

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    
    # Folders
    BASE_DIR = BASE_DIR
    UPLOAD_FOLDER = STORAGE_DIR / 'uploads'
    OUTPUT_FOLDER = STORAGE_DIR / 'outputs'
    ENCRYPTED_FOLDER = STORAGE_DIR / 'encrypted'
    DEMO_FOLDER = BASE_DIR / 'demo_images'
    INSTANCE_FOLDER = STORAGE_DIR / 'instance'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f"sqlite:///{INSTANCE_FOLDER / 'invisiface.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload Constraints
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
    
    # Quantum Settings
    QUANTUM_MODE = os.getenv('QUANTUM_MODE', 'simulation')  # 'simulation', 'classical', 'ibm'
    IBM_QUANTUM_TOKEN = os.getenv('IBM_QUANTUM_TOKEN', '')
    
    # Security Settings
    # AES-256 key (32 bytes)
    AES_KEY_BASE64 = os.getenv('AES_KEY_BASE64', '')
    
    @classmethod
    def init_app(cls):
        """Ensure all required runtime directories exist."""
        folders = [cls.UPLOAD_FOLDER, cls.OUTPUT_FOLDER, cls.ENCRYPTED_FOLDER, cls.INSTANCE_FOLDER]
        if not IS_VERCEL:
            folders.append(cls.DEMO_FOLDER)
        for folder in folders:
            try:
                folder.mkdir(parents=True, exist_ok=True)
                gitkeep = folder / '.gitkeep'
                if not gitkeep.exists():
                    gitkeep.touch()
            except Exception as e:
                print(f"Directory initialization notice for {folder}: {e}")
