import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'super-secret-key'
    MONGO_URI = os.getenv('MONGO_URI') or 'mongodb://localhost:27017/flask_auth'
    # Thêm các cấu hình email
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'mynamephap@gmail.com'  # Thay bằng email của bạn
    MAIL_PASSWORD = 'pxzsynupypepdwhs'     # Thay bằng mật khẩu ứng dụng
    MAIL_DEFAULT_SENDER = 'mynamephap@gmail.com'  # Thay bằng email của bạn
    
    # Cấu hình session
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)