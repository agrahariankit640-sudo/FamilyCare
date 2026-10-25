import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'familycare-dev-secret-key-2026')
    _db_path = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'database', 'familycare.db'))
    DATABASE_PATH = _db_path if os.path.isabs(_db_path) else os.path.join(BASE_DIR, _db_path)
    
    _upload_folder = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads'))
    UPLOAD_FOLDER = _upload_folder if os.path.isabs(_upload_folder) else os.path.join(BASE_DIR, _upload_folder)
    
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 10485760)) # 10MB default
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
    
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
