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
            'updated_at': datetime.utcnow(),
            'permissions': []
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

    @staticmethod
    def get_all():
        return mongo.db.users.find()

    @staticmethod
    def delete(username):
        return mongo.db.users.delete_one({'username': username})

    @staticmethod
    def get_permissions(username):
        user = User.find_by_username(username)
        return user.get('permissions', []) if user else []

    @staticmethod
    def set_permissions(username, permissions):
        return mongo.db.users.update_one(
            {'username': username},
            {'$set': {'permissions': permissions, 'updated_at': datetime.utcnow()}}
        )

    @staticmethod
    def add_permission(username, permission):
        user = User.find_by_username(username)
        if not user:
            return None
        perms = set(user.get('permissions', []))
        perms.add(permission)
        return User.set_permissions(username, list(perms))

    @staticmethod
    def remove_permission(username, permission):
        user = User.find_by_username(username)
        if not user:
            return None
        perms = set(user.get('permissions', []))
        perms.discard(permission)
        return User.set_permissions(username, list(perms))
    @staticmethod
    def has_custom_permission(username, permission):
        """Kiểm tra user có quyền riêng cụ thể không"""
        user = User.find_by_username(username)
        if not user:
            return False
        return permission in user.get('permissions', [])

    @staticmethod
    def get_custom_permissions(username):
        """Lấy danh sách quyền riêng của user"""
        user = User.find_by_username(username)
        if not user:
            return []
        return user.get('permissions', [])

    @staticmethod
    def has_any_custom_permission(username):
        """Kiểm tra user có bất kỳ quyền riêng nào không"""
        user = User.find_by_username(username)
        if not user:
            return False
        return len(user.get('permissions', [])) > 0

    @staticmethod
    def get_available_custom_permissions():
        """Lấy danh sách tất cả quyền riêng có thể cấp"""
        return [
            'manage_users',
            'manage_courses', 
            'manage_exercises',
            'view_stats',
            'config_system',
            'export_data',
            'manage_roles',
            'view_logs',
            'manage_backups',
            'system_monitoring'
        ]
