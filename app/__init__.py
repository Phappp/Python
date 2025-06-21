from flask import Flask, session
from config import Config
from .extensions import mongo

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Khởi tạo extensions
    mongo.init_app(app)
    
    # Đăng ký blueprints
    from .routes.auth_routes import auth_bp
    from .routes.main_routes import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    return app