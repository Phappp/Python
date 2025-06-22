from flask import flash, Blueprint, render_template, request,session,redirect,url_for
from app.forms import RegistrationForm, LoginForm, OTPForm
from app.controllers.auth_controller import AuthController
from app.models.user_model import User
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    response = AuthController.register(form)
    return response or render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:  # Kiểm tra nếu đã đăng nhập
        return redirect(url_for('main.home'))  # Chuyển hướng đến trang home
    form = LoginForm()
    response = AuthController.login(form)
    return response or render_template('auth/login.html', form=form)

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    form = OTPForm()
    if form.validate_on_submit():
        if AuthController.verify_otp(form.otp.data):
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Mã OTP không đúng hoặc đã hết hạn!', 'danger')
    return render_template('auth/verify_otp.html', form=form)

@auth_bp.route('/logout')
def logout():
    return AuthController.logout()