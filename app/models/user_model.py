from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import mongo
from datetime import datetime

class User:
    @staticmethod
    def create(username, email, password, role='student'):
        hashed_password = generate_password_hash(password)
        return mongo.db.users.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password,
            'role': role,
            'full_name': '',
            'phone': '',
            'bio': '',
            'avatar': '',
            'hometown': '',
            'birth_date': None,
            'two_factor_enabled': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
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

    # Profile Management Methods
    @staticmethod
    def update_profile(username, update_data):
        """Cập nhật thông tin hồ sơ cá nhân"""
        try:
            # Thêm updated_at vào dữ liệu cập nhật
            update_data['updated_at'] = datetime.utcnow()
            
            result = mongo.db.users.update_one(
                {'username': username},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False

    @staticmethod
    def update_avatar(username, avatar_path):
        """Cập nhật avatar cho người dùng"""
        try:
            result = mongo.db.users.update_one(
                {'username': username},
                {
                    '$set': {
                        'avatar': avatar_path,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating avatar: {e}")
            return False

    @staticmethod
    def update_password(username, new_password):
        """Cập nhật mật khẩu mới"""
        try:
            hashed_password = generate_password_hash(new_password)
            result = mongo.db.users.update_one(
                {'username': username},
                {
                    '$set': {
                        'password': hashed_password,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating password: {e}")
            return False

    @staticmethod
    def update_security_settings(username, security_data):
        """Cập nhật cài đặt bảo mật"""
        try:
            result = mongo.db.users.update_one(
                {'username': username},
                {'$set': security_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating security settings: {e}")
            return False