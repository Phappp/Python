import random
import string
import time
from datetime import datetime
from flask import flash, redirect, url_for, session, current_app
from flask_mail import Message
from app.extensions import mail
from app.models.user_model import User

class AuthController:
    OTP_EXPIRATION = 300  # 5 minutes in seconds

    @staticmethod
<<<<<<< HEAD
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
    
=======
    def generate_otp(length=6):
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def send_otp_email(email, otp):
        try:
            msg = Message(
                "Mã OTP đăng nhập",
                recipients=[email],
                body=f"Mã OTP của bạn: {otp} (Hiệu lực 5 phút)"
            )
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Lỗi gửi email: {str(e)}")
            flash('Hệ thống đang bận. Vui lòng thử lại sau!', 'danger')
            return False

>>>>>>> b7b4b2b9d38e110421f1f0807531b9b5524ceb48
    @staticmethod
    def login(form):
        if 'username' in session:  # Kiểm tra nếu đã đăng nhập
            return redirect(url_for('main.home'))
        if form.validate_on_submit():
            # Start with fresh session state
            session.clear()
            
            username = form.username.data
            password = form.password.data
            user = User.find_by_username(username)
            
            if user and User.check_password(user, password):
<<<<<<< HEAD
                session['username'] = username
                session['role'] = user['role']
                flash('Đăng nhập thành công!', 'success')
                return redirect(url_for('main.home'))
=======
                otp = AuthController.generate_otp()
                
                # Set ALL OTP-related data in a single operation
                session.update({
                    'auth_otp': otp,
                    'auth_otp_time': int(time.time()),
                    'auth_otp_username': username,
                    '_fresh': True,
                    '_permanent': False  # Will be True only after OTP verification
                })
                
                # Force session to save before redirect
                session.modified = True
                
                current_app.logger.debug(f"Session after OTP generation: {dict(session)}")
                
                if not AuthController.send_otp_email(user['email'], otp):
                    return redirect(url_for('auth.login'))
                
                # Create response object to ensure session is committed
                response = redirect(url_for('auth.verify_otp'))
                return response
>>>>>>> b7b4b2b9d38e110421f1f0807531b9b5524ceb48
            
            flash('Tên người dùng hoặc mật khẩu không đúng!', 'danger')
        return None
    
    @staticmethod
    def verify_otp(otp):
        session_data = dict(session)
        current_app.logger.debug(f"[VERIFY] Full session: {session_data}")
    
        required_keys = ['auth_otp', 'auth_otp_time', 'auth_otp_username']
        missing_keys = [key for key in required_keys if key not in session]
    
        if missing_keys:
            current_app.logger.error(
                f"[VERIFY] Missing keys: {missing_keys}. Session contents: {session_data}"
            )
            flash('Phiên làm việc không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại!', 'danger')
            return False

        verification_time = int(time.time())
        created_time = int(session['auth_otp_time'])
        time_delta = verification_time - created_time
        
        current_app.logger.debug(
            f"OTP Verification - Created: {datetime.fromtimestamp(created_time)}, "
            f"Current: {datetime.fromtimestamp(verification_time)}, "
            f"Delta: {time_delta}s"
        )

        if time_delta > AuthController.OTP_EXPIRATION:
            session.clear()
            flash('Mã OTP đã hết hạn. Vui lòng yêu cầu mã mới!', 'danger')
            return False

        if str(session['auth_otp']) != str(otp):
            flash('Mã OTP không đúng!', 'danger')
            return False

        # Convert to authenticated session
        session['username'] = session.pop('auth_otp_username')
        session.permanent = True
        session.modified = True
        
        # Cleanup OTP-related session data
        session.pop('auth_otp', None)
        session.pop('auth_otp_time', None)
        
        return True

    @staticmethod
    def logout():
<<<<<<< HEAD
        session.pop('username', None)
        session.pop('role', None)
=======
        session.clear()
>>>>>>> b7b4b2b9d38e110421f1f0807531b9b5524ceb48
        flash('Bạn đã đăng xuất thành công!', 'success')
        return redirect(url_for('main.home'))