import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'super-secret-key'
    MONGO_URI = os.getenv('MONGO_URI') or 'mongodb://localhost:27017/flask_auth'
    
    # Cấu hình email
    MAIL_SERVER = os.getenv('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.getenv('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME') or 'mynamephap@gmail.com'
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') or 'pxzsynupypepdwhs'
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER') or 'mynamephap@gmail.com'
    
    # Cấu hình session
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Cấu hình upload file
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Cấu hình OTP
    OTP_EXPIRATION = 300  # 5 minutes in seconds