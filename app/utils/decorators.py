from functools import wraps
from flask import session, flash, redirect, url_for

def login_required(f):
    """
    Decorator yêu cầu người dùng phải đăng nhập.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Vui lòng đăng nhập để truy cập trang này.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role_name):
    """
    Decorator yêu cầu người dùng phải có một vai trò cụ thể.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('Vui lòng đăng nhập để truy cập trang này.', 'warning')
                return redirect(url_for('auth.login'))
            if session.get('role') != role_name:
                flash('Bạn không có quyền truy cập trang này!', 'danger')
                return redirect(url_for('main.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator 