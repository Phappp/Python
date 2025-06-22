from flask import flash, redirect, url_for, session
from app.models.user_model import User
from app.forms import RegistrationForm, LoginForm

class AuthController:
    @staticmethod
    def register(form):
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            role = form.role.data
            
            if User.find_by_username(username) is None:
                User.create(username, password, role)
                flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
                return redirect(url_for('auth.login'))
            
            flash('Tên người dùng đã tồn tại!', 'danger')
        return None
    
    @staticmethod
    def login(form):
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = User.find_by_username(username)
            
            if user and User.check_password(user, password):
                session['username'] = username
                session['role'] = user['role']
                flash('Đăng nhập thành công!', 'success')
                return redirect(url_for('main.home'))
            
            flash('Tên người dùng hoặc mật khẩu không đúng!', 'danger')
        return None
    
    @staticmethod
    def logout():
        session.pop('username', None)
        session.pop('role', None)
        flash('Bạn đã đăng xuất thành công!', 'success')
        return redirect(url_for('main.home'))