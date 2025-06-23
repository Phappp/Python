import random
import string
import time
import os
from datetime import datetime, date
from flask import flash, redirect, url_for, session, current_app, request
from flask_mail import Message
from werkzeug.utils import secure_filename
from app.extensions import mail
from app.models.user_model import User

class AuthController:
    OTP_EXPIRATION = 300  # 5 minutes in seconds

    @staticmethod
    def _send_otp_email(recipient, otp, subject="Mã OTP xác thực của bạn"):
        try:
            msg = Message(subject,
                          sender=current_app.config['MAIL_DEFAULT_SENDER'],
                          recipients=[recipient])
            msg.body = f"Mã OTP của bạn là: {otp}. Mã này sẽ hết hạn sau 5 phút."
            mail.send(msg)
            current_app.logger.info(f"Đã gửi OTP tới {recipient}")
            return True
        except Exception as e:
            current_app.logger.error(f"Lỗi gửi email: {e}")
            return False

    @staticmethod
    def _save_avatar(file):
        """Lưu file avatar và trả về đường dẫn"""
        if file and file.filename:
            # Tạo thư mục uploads nếu chưa tồn tại
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Tạo tên file an toàn
            filename = secure_filename(file.filename)
            # Thêm timestamp để tránh trùng tên
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{int(time.time())}{ext}"
            
            # Lưu file
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Trả về đường dẫn tương đối
            return f'/static/uploads/avatars/{filename}'
        return None

    @staticmethod
    def register(form):
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data
            role = form.role.data
            
            if User.find_by_username(username) is None:
                if User.find_by_email(email) is None:
                    # Tạo OTP cho xác thực email đăng ký
                    otp = ''.join(random.choices(string.digits, k=6))
                    
                    if AuthController._send_otp_email(email, otp, "Mã OTP xác thực đăng ký tài khoản"):
                        # Lưu thông tin đăng ký vào session để xác thực sau
                        session['register_otp'] = otp
                        session['register_otp_time'] = int(time.time())
                        session['register_data'] = {
                            'username': username,
                            'email': email,
                            'password': password,
                            'role': role
                        }
                        
                        flash('Một mã OTP đã được gửi đến email của bạn để xác thực đăng ký.', 'info')
                        return redirect(url_for('auth.verify_register_otp'))
                    else:
                        flash('Không thể gửi email OTP. Vui lòng thử lại sau.', 'danger')
                else:
                    flash('Email đã tồn tại!', 'danger')
            else:
                flash('Tên người dùng đã tồn tại!', 'danger')
        return None

    @staticmethod
    def verify_register_otp(otp):
        """Xác thực OTP cho quá trình đăng ký"""
        session_data = dict(session)
        current_app.logger.debug(f"[REGISTER VERIFY] Full session: {session_data}")
    
        required_keys = ['register_otp', 'register_otp_time', 'register_data']
        missing_keys = [key for key in required_keys if key not in session]
    
        if missing_keys:
            current_app.logger.error(
                f"[REGISTER VERIFY] Missing keys: {missing_keys}. Session contents: {session_data}"
            )
            flash('Phiên đăng ký không hợp lệ hoặc đã hết hạn. Vui lòng đăng ký lại!', 'danger')
            return False

        verification_time = int(time.time())
        created_time = int(session['register_otp_time'])
        time_delta = verification_time - created_time
        
        if time_delta > AuthController.OTP_EXPIRATION:
            session.clear()
            flash('Mã OTP đã hết hạn. Vui lòng đăng ký lại!', 'danger')
            return False

        if str(session['register_otp']) != str(otp):
            flash('Mã OTP không đúng!', 'danger')
            return False

        # Tạo tài khoản sau khi xác thực OTP thành công
        register_data = session['register_data']
        User.create(
            register_data['username'], 
            register_data['email'], 
            register_data['password'], 
            register_data['role']
        )
        
        # Cleanup session data
        session.pop('register_otp', None)
        session.pop('register_otp_time', None)
        session.pop('register_data', None)
        
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return True

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
                # Kiểm tra xem người dùng có bật 2FA không
                if user.get('two_factor_enabled', False):
                    # Nếu bật 2FA, gửi OTP
                    otp = ''.join(random.choices(string.digits, k=6))

                    if AuthController._send_otp_email(user['email'], otp, "Mã OTP đăng nhập - Xác thực 2 yếu tố"):
                        session['auth_otp'] = otp
                        session['auth_otp_time'] = int(time.time())
                        session['auth_otp_username'] = user['username']
                        session['role'] = user['role']

                        flash('Mã OTP đã được gửi đến email của bạn để xác thực 2 yếu tố.', 'info')
                        return redirect(url_for('auth.verify_otp'))
                    else:
                        flash('Không thể gửi email OTP. Vui lòng thử lại sau.', 'danger')
                else:
                    # Nếu không bật 2FA, đăng nhập trực tiếp
                    session['username'] = user['username']
                    session['role'] = user['role']
                    session.permanent = True
                    session.modified = True
                    
                    flash('Đăng nhập thành công!', 'success')
                    return redirect(url_for('main.home'))
            else:
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
        session.pop('username', None)
        session.pop('role', None)

        flash('Bạn đã đăng xuất thành công!', 'success')
        return redirect(url_for('main.home'))

    # Profile Management Methods
    @staticmethod
    def get_current_user():
        """Lấy thông tin người dùng hiện tại"""
        if 'username' in session:
            return User.find_by_username(session['username'])
        return None

    @staticmethod
    def update_profile(form):
        """Cập nhật thông tin hồ sơ cá nhân"""
        username = session.get('username')
        if not username:
            flash('Phiên làm việc không hợp lệ!', 'danger')
            return redirect(url_for('auth.login'))
        
        user = User.find_by_username(username)
        if not user:
            flash('Không tìm thấy thông tin người dùng!', 'danger')
            return redirect(url_for('auth.login'))
        
        # Kiểm tra email có bị trùng với người dùng khác không
        new_email = form.email.data
        if new_email != user.get('email'):
            existing_user = User.find_by_email(new_email)
            if existing_user and existing_user['username'] != username:
                flash('Email này đã được sử dụng bởi tài khoản khác!', 'danger')
                return None
        
        # Chuẩn bị dữ liệu cập nhật
        update_data = {
            'full_name': form.full_name.data,
            'email': new_email,
            'hometown': form.hometown.data or '',
            'phone': form.phone.data or '',
            'bio': form.bio.data or '',
        }
        
        # Chuyển đổi date thành datetime để tương thích với MongoDB
        birth_date_obj = form.birth_date.data
        if birth_date_obj:
            update_data['birth_date'] = datetime.combine(birth_date_obj, datetime.min.time())
        else:
            update_data['birth_date'] = None

        # Xử lý upload avatar nếu có
        if form.avatar.data:
            avatar_path = AuthController._save_avatar(form.avatar.data)
            if avatar_path:
                update_data['avatar'] = avatar_path
            else:
                flash('Có lỗi xảy ra khi tải lên ảnh đại diện!', 'danger')
                return None
        
        if User.update_profile(username, update_data):
            flash('Cập nhật thông tin thành công!', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Có lỗi xảy ra khi cập nhật thông tin!', 'danger')
            return None # Re-render form on failure

    @staticmethod
    def request_password_change(form):
        """Xử lý yêu cầu thay đổi mật khẩu, kiểm tra và gửi OTP"""
        username = session.get('username')
        if not username:
            flash('Phiên làm việc không hợp lệ!', 'danger')
            return redirect(url_for('auth.login'))

        user = User.find_by_username(username)
        if not user:
            flash('Không tìm thấy thông tin người dùng!', 'danger')
            return redirect(url_for('auth.login'))

        # Kiểm tra mật khẩu hiện tại
        if not User.check_password(user, form.current_password.data):
            flash('Mật khẩu hiện tại không đúng!', 'danger')
            return None  # Re-render the form with error

        # Mật khẩu đúng, gửi OTP
        otp = ''.join(random.choices(string.digits, k=6))
        if AuthController._send_otp_email(user['email'], otp, "Mã OTP xác thực thay đổi mật khẩu"):
            session['change_password_otp'] = otp
            session['change_password_otp_time'] = int(time.time())
            # Lưu mật khẩu mới vào session để sử dụng sau khi xác thực OTP
            session['change_password_new_password'] = form.new_password.data
            
            flash('Mã OTP đã được gửi đến email của bạn.', 'info')
            return redirect(url_for('auth.verify_password_change'))
        else:
            flash('Không thể gửi email OTP. Vui lòng thử lại sau.', 'danger')
            return None

    @staticmethod
    def verify_password_change(form):
        """Xác thực OTP và hoàn tất thay đổi mật khẩu"""
        username = session.get('username')
        if not username or 'change_password_otp' not in session:
            flash('Phiên làm việc không hợp lệ hoặc đã hết hạn. Vui lòng thử lại.', 'danger')
            return redirect(url_for('auth.change_password'))

        # Kiểm tra OTP
        verification_time = int(time.time())
        created_time = int(session.get('change_password_otp_time', 0))
        
        if verification_time - created_time > AuthController.OTP_EXPIRATION:
            # Xóa session OTP
            session.pop('change_password_otp', None)
            session.pop('change_password_otp_time', None)
            session.pop('change_password_new_password', None)
            flash('Mã OTP đã hết hạn. Vui lòng thử lại!', 'danger')
            return redirect(url_for('auth.change_password'))

        if str(session['change_password_otp']) != str(form.otp.data):
            flash('Mã OTP không đúng!', 'danger')
            return None # Re-render the OTP form with error

        # OTP đúng, cập nhật mật khẩu
        new_password = session.get('change_password_new_password')
        if User.update_password(username, new_password):
            flash('Đổi mật khẩu thành công!', 'success')
        else:
            flash('Có lỗi xảy ra khi đổi mật khẩu!', 'danger')

        # Xóa toàn bộ session OTP
        session.pop('change_password_otp', None)
        session.pop('change_password_otp_time', None)
        session.pop('change_password_new_password', None)

        return redirect(url_for('auth.profile'))

    @staticmethod
    def change_password(form):
        """Đổi mật khẩu"""
        if form.validate_on_submit():
            response = AuthController.change_password(form)
            if response:
                return response
        
        return None

    @staticmethod
    def send_change_password_otp(current_password, new_password):
        """Gửi OTP để xác thực thay đổi mật khẩu"""
        try:
            username = session.get('username')
            if not username:
                return {'success': False, 'message': 'Phiên làm việc không hợp lệ'}
            
            user = User.find_by_username(username)
            if not user:
                return {'success': False, 'message': 'Không tìm thấy thông tin người dùng'}
            
            # Kiểm tra mật khẩu hiện tại
            if not User.check_password(user, current_password):
                return {'success': False, 'message': 'Mật khẩu hiện tại không đúng'}
            
            # Tạo OTP
            otp = ''.join(random.choices(string.digits, k=6))
            
            # Gửi OTP qua email
            if AuthController._send_otp_email(user['email'], otp, "Mã OTP xác thực thay đổi mật khẩu"):
                # Lưu OTP vào session
                session['change_password_otp'] = otp
                session['change_password_otp_time'] = int(time.time())
                session['change_password_new_password'] = new_password
                
                return {'success': True, 'message': 'Mã OTP đã được gửi đến email của bạn'}
            else:
                return {'success': False, 'message': 'Không thể gửi email OTP'}
                
        except Exception as e:
            current_app.logger.error(f"Error sending change password OTP: {e}")
            return {'success': False, 'message': 'Có lỗi xảy ra khi gửi OTP'}

    @staticmethod
    def _verify_change_password_otp(otp):
        """Xác thực OTP cho thay đổi mật khẩu"""
        try:
            required_keys = ['change_password_otp', 'change_password_otp_time', 'change_password_new_password']
            missing_keys = [key for key in required_keys if key not in session]
            
            if missing_keys:
                return False

            verification_time = int(time.time())
            created_time = int(session['change_password_otp_time'])
            time_delta = verification_time - created_time
            
            if time_delta > AuthController.OTP_EXPIRATION:
                # Cleanup session
                session.pop('change_password_otp', None)
                session.pop('change_password_otp_time', None)
                session.pop('change_password_new_password', None)
                return False

            if str(session['change_password_otp']) != str(otp):
                return False

            # Cleanup session sau khi xác thực thành công
            session.pop('change_password_otp', None)
            session.pop('change_password_otp_time', None)
            session.pop('change_password_new_password', None)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error verifying change password OTP: {e}")
            return False

    @staticmethod
    def update_security_settings(form):
        """Cập nhật cài đặt bảo mật"""
        if form.validate_on_submit():
            username = session.get('username')
            if not username:
                flash('Phiên làm việc không hợp lệ!', 'danger')
                return redirect(url_for('auth.login'))
            
            user = User.find_by_username(username)
            if not user:
                flash('Không tìm thấy thông tin người dùng!', 'danger')
                return redirect(url_for('auth.login'))
            
            # Kiểm tra mật khẩu để xác nhận thay đổi
            if not User.check_password(user, form.current_password.data):
                flash('Mật khẩu không đúng!', 'danger')
                return None
            
            # Cập nhật cài đặt 2FA
            update_data = {
                'two_factor_enabled': form.two_factor_enabled.data,
                'updated_at': datetime.utcnow()
            }
            
            if User.update_security_settings(username, update_data):
                status = 'bật' if form.two_factor_enabled.data else 'tắt'
                flash(f'Đã {status} xác thực 2 yếu tố thành công!', 'success')
                return redirect(url_for('auth.security_settings'))
            else:
                flash('Có lỗi xảy ra khi cập nhật cài đặt bảo mật!', 'danger')
        
        return None