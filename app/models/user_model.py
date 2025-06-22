from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import mongo

class User:
    @staticmethod
<<<<<<< HEAD
    def create(username, password, role='student'):
        hashed_password = generate_password_hash(password)
        return mongo.db.users.insert_one({
            'username': username,
            'password': hashed_password,
            'role': role
=======
    def create(username, password, email):
        hashed_password = generate_password_hash(password)
        return mongo.db.users.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password
>>>>>>> b7b4b2b9d38e110421f1f0807531b9b5524ceb48
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