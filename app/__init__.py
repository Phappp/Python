from flask import Flask, session
from config import Config
from .extensions import mongo
from .extensions import mail
import smtplib
from datetime import datetime, timedelta, timezone

def datetimeformat(value):
    try:
        if isinstance(value, str):
            # value có thể là '2025-07-20 00:00' hoặc '2025-07-20'
            try:
                dt = datetime.strptime(value, '%Y-%m-%d %H:%M')
            except:
                try:
                    dt = datetime.strptime(value, '%Y-%m-%d')
                except:
                    return value
        else:
            dt = value
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return value

def create_app():
    app = Flask(__name__)
    smtplib.SMTP.debuglevel = 1
    app.config.from_object(Config)
    # Cấu hình Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'mynamephap@gmail.com'
    app.config['MAIL_PASSWORD'] = 'yzhiszynkvjjutnm'
    # Load cấu hình từ class Config
    app.config.update(
    # Critical session settings
        SECRET_KEY='your-very-strong-secret-key-here',
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        SESSION_REFRESH_EACH_REQUEST=True,
    
    # Cookie settings
        SESSION_COOKIE_NAME='app_session',
        SESSION_COOKIE_SECURE=False,  # True in production
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    
    # Ensure session consistency
        USE_X_SENDFILE=False,
        SEND_FILE_MAX_AGE_DEFAULT=0
    )
    # Khởi tạo extensions
    mongo.init_app(app)
    
    # Đăng ký blueprints
    from .routes.auth_routes import auth_bp
    from .routes.main_routes import main_bp
    from .routes.course_routes import course_bp
    from .routes.exercise_routes import register_exercise_routes
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(course_bp)
    register_exercise_routes(app)
    mail.init_app(app)

    app.jinja_env.filters['datetimeformat'] = datetimeformat

    @app.context_processor
    def inject_user_info():
        from app.models.user_model import User
        username = session.get('username')
        role = session.get('role')
        avatar = None
        if username:
            user = User.find_by_username(username)
            if user:
                avatar = user.get('avatar')
        return dict(username=username, role=role, avatar=avatar)

    return app