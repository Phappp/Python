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

def remember_me_status():
    """Kiểm tra trạng thái remember me của session hiện tại"""
    if 'username' in session:
        # Kiểm tra xem session có permanent không (remember me)
        from flask import session as flask_session
        return {
            'is_logged_in': True,
            'remember_me': flask_session.permanent,
            'username': session.get('username'),
            'role': session.get('role')
        }
    return {
        'is_logged_in': False,
        'remember_me': False,
        'username': None,
        'role': None
    } 