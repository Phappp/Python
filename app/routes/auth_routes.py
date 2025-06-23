from flask import flash, Blueprint, render_template, request,session,redirect,url_for, jsonify
from app.forms import RegistrationForm, LoginForm, OTPForm, ProfileEditForm, ChangePasswordRequestForm, SecuritySettingsForm
from app.controllers.auth_controller import AuthController
from app.models.user_model import User
from app.utils.decorators import login_required
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    response = AuthController.register(form)
    return response or render_template('auth/register.html', form=form)

@auth_bp.route('/verify-register-otp', methods=['GET', 'POST'])
def verify_register_otp():
    """Xác thực OTP cho quá trình đăng ký"""
    form = OTPForm()
    if form.validate_on_submit():
        if AuthController.verify_register_otp(form.otp.data):
            return redirect(url_for('auth.login'))
        else:
            flash('Mã OTP không đúng hoặc đã hết hạn!', 'danger')
    return render_template('auth/verify_register_otp.html', form=form)

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

# Profile Management Routes
@auth_bp.route('/profile')
@login_required
def profile():
    """Hiển thị hồ sơ cá nhân của người dùng"""
    user = AuthController.get_current_user()
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Chỉnh sửa thông tin hồ sơ cá nhân"""
    form = ProfileEditForm()
    user = AuthController.get_current_user()
    
    if form.validate_on_submit():
        response = AuthController.update_profile(form)
        if response:
            return response
    elif request.method == 'GET':
        # Pre-populate form with current user data
        if user:
            form.full_name.data = user.get('full_name', '')
            form.email.data = user.get('email', '')
            form.hometown.data = user.get('hometown', '')
            form.birth_date.data = user.get('birth_date')
            form.phone.data = user.get('phone', '')
            form.bio.data = user.get('bio', '')
    
    return render_template('auth/edit_profile.html', form=form, user=user)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Bắt đầu quá trình đổi mật khẩu"""
    form = ChangePasswordRequestForm()
    if form.validate_on_submit():
        response = AuthController.request_password_change(form)
        if response:
            return response
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/verify-password-change', methods=['GET', 'POST'])
@login_required
def verify_password_change():
    """Xác thực OTP để hoàn tất đổi mật khẩu"""
    if 'change_password_otp' not in session:
        flash('Yêu cầu không hợp lệ. Vui lòng bắt đầu lại.', 'warning')
        return redirect(url_for('auth.change_password'))
        
    form = OTPForm()
    if form.validate_on_submit():
        response = AuthController.verify_password_change(form)
        if response:
            return response

    return render_template('auth/verify_password_change.html', form=form)

@auth_bp.route('/send-change-password-otp', methods=['POST'])
@login_required
def send_change_password_otp():
    """Gửi OTP để xác thực thay đổi mật khẩu"""
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'success': False, 'message': 'Thiếu thông tin cần thiết'})
        
        response = AuthController.send_change_password_otp(current_password, new_password)
        return jsonify(response)
    except Exception as e:
        return jsonify({'success': False, 'message': 'Có lỗi xảy ra'})

@auth_bp.route('/security-settings', methods=['GET', 'POST'])
@login_required
def security_settings():
    """Cấu hình bảo mật 2FA"""
    form = SecuritySettingsForm()
    user = AuthController.get_current_user()
    
    if form.validate_on_submit():
        response = AuthController.update_security_settings(form)
        if response:
            return response
    
    # Pre-populate form with current security settings
    if user:
        form.two_factor_enabled.data = user.get('two_factor_enabled', False)
    
    return render_template('auth/security_settings.html', form=form, user=user)