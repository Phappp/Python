from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import mongo

class User:
    @staticmethod
    def create(username, password, role='student'):
        hashed_password = generate_password_hash(password)
        return mongo.db.users.insert_one({
            'username': username,
            'password': hashed_password,
            'role': role

        })
    
    @staticmethod
    def find_by_username(username):
        return mongo.db.users.find_one({'username': username})
    
    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({'email': email})
    
    @staticmethod
    def check_password(user, password):
        return check_password_hash(user['password'], password)
    
    @staticmethod
    def get_role(username):
        user = User.find_by_username(username)
        return user['role'] if user else None