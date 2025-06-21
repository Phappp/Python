import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'super-secret-key'
    MONGO_URI = os.getenv('MONGO_URI') or 'mongodb://localhost:27017/flask_auth'