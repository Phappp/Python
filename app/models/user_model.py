from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import mongo

class User:
    @staticmethod
    def create(username, password):
        hashed_password = generate_password_hash(password)
        return mongo.db.users.insert_one({
            'username': username,
            'password': hashed_password
        })
    
    @staticmethod
    def find_by_username(username):
        return mongo.db.users.find_one({'username': username})
    
    @staticmethod
    def check_password(user, password):
        return check_password_hash(user['password'], password)