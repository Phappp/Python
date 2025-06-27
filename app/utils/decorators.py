from functools import wraps
from flask import session, flash, redirect, url_for

def login_required(f):
    """
    Decorator yêu cầu người dùng phải đăng nhập.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Vui lòng đăng nhập để truy cập trang này!', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    """
    Decorator yêu cầu người dùng phải có một vai trò cụ thể.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session:
                flash('Vui lòng đăng nhập để truy cập trang này!', 'warning')
                return redirect(url_for('auth.login'))
            if session['role'] != required_role:
                flash('Bạn không có quyền truy cập trang này!', 'danger')
                return redirect(url_for('main.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def saved_credentials_status():
    """Kiểm tra trạng thái saved credentials của session hiện tại"""
    if 'username' in session:
        # Kiểm tra xem có thông tin đăng nhập đã lưu không
        from flask import session as flask_session
        return {
            'is_logged_in': True,
            'saved_credentials': session.get('save_credentials', False),
            'username': session.get('username'),
            'role': session.get('role')
        }
    return {
        'is_logged_in': False,
        'saved_credentials': False,
        'username': None,
        'role': None
    }

def custom_permission_required(permission):
    """
    Decorator yêu cầu người dùng phải có quyền riêng cụ thể.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('Vui lòng đăng nhập để truy cập trang này!', 'warning')
                return redirect(url_for('auth.login'))
            
            from app.models.user_model import User
            if not User.has_custom_permission(session['username'], permission):
                flash('Bạn không có quyền truy cập tính năng này!', 'danger')
                return redirect(url_for('main.home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def has_custom_permission(permission):
    """
    Helper function để kiểm tra quyền riêng trong template
    """
    if 'username' not in session:
        return False
    
    from app.models.user_model import User
    return User.has_custom_permission(session['username'], permission)

def has_any_custom_permission():
    """
    Helper function để kiểm tra có bất kỳ quyền riêng nào không
    """
    if 'username' not in session:
        return False
    
    from app.models.user_model import User
    return User.has_any_custom_permission(session['username'])

def get_custom_permissions_count():
    """
    Helper function để lấy số lượng quyền riêng
    """
    if 'username' not in session:
        return 0
    
    from app.models.user_model import User
    return len(User.get_custom_permissions(session['username'])) 