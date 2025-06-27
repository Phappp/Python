from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, BooleanField, DateField, IntegerField, FloatField, FieldList, FormField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Optional, ValidationError
from wtforms.widgets import TextArea
import re

class RegistrationForm(FlaskForm):
    username = StringField('Tên người dùng', 
                         validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', 
                           validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu',
                                  validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Vai trò', 
                      choices=[('student', 'Sinh viên'), ('lecture', 'Giảng viên')],
                      default='student')

    submit = SubmitField('Đăng ký')

class LoginForm(FlaskForm):
    username = StringField('Tên người dùng', 
                         validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Mật khẩu', 
                           validators=[DataRequired()])
    save_credentials = BooleanField('Lưu tài khoản và mật khẩu')
    submit = SubmitField('Đăng nhập')

class OTPForm(FlaskForm):
    otp = StringField('Mã OTP', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Xác thực')

# Profile Management Forms
class ProfileEditForm(FlaskForm):
    avatar = FileField('Ảnh đại diện', 
                      validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Chỉ cho phép file ảnh!')])
    full_name = StringField('Họ và tên', 
                           validators=[Optional(), Length(min=2, max=100)])
    hometown = StringField('Quê quán', 
                          validators=[Optional(), Length(max=100)])
    birth_date = DateField('Ngày sinh', 
                          validators=[Optional()], 
                          format='%Y-%m-%d')
    phone = StringField('Số điện thoại', 
                       validators=[Optional(), Length(min=10, max=15)])
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    bio = TextAreaField('Giới thiệu bản thân', 
                       validators=[Optional(), Length(max=500)])
    submit = SubmitField('Cập nhật thông tin')

class ChangePasswordRequestForm(FlaskForm):
    current_password = PasswordField('Mật khẩu hiện tại', 
                                   validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới', 
                               validators=[DataRequired(), Length(min=6, message='Mật khẩu phải có ít nhất 6 ký tự')])
    confirm_new_password = PasswordField('Xác nhận mật khẩu mới',
                                       validators=[DataRequired(), EqualTo('new_password', message='Mật khẩu xác nhận không khớp')])
    submit = SubmitField('Gửi mã OTP')

class ChangePasswordWithOTPForm(FlaskForm):
    current_password = PasswordField('Mật khẩu hiện tại', 
                                   validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới', 
                               validators=[DataRequired(), Length(min=6, message='Mật khẩu phải có ít nhất 6 ký tự')])
    confirm_new_password = PasswordField('Xác nhận mật khẩu mới',
                                       validators=[DataRequired(), EqualTo('new_password', message='Mật khẩu xác nhận không khớp')])
    send_otp = SubmitField('Gửi mã OTP')
    submit = SubmitField('Xác nhận thay đổi')

class SecuritySettingsForm(FlaskForm):
    two_factor_enabled = BooleanField('Bật xác thực 2 yếu tố (2FA)')
    current_password = PasswordField('Mật khẩu hiện tại (để xác nhận thay đổi)')
    submit = SubmitField('Cập nhật cài đặt bảo mật')

class CourseForm(FlaskForm):
    name = StringField('Tên khóa học', validators=[DataRequired(), Length(min=5, max=100)])
    description = StringField('Mô tả', validators=[DataRequired(), Length(min=10, max=200)])
    original_price = StringField('Giá gốc (ví dụ: 2.500.000)', validators=[DataRequired()])
    discounted_price = StringField('Giá khuyến mãi (ví dụ: 1.299.000)', validators=[DataRequired()])
    color = SelectField('Màu nền', 
                      choices=[
                          ('purple', 'Tím'), 
                          ('yellow', 'Vàng'), 
                          ('red', 'Đỏ'),
                          ('blue', 'Xanh dương'),
                          ('green', 'Xanh lá')
                      ],
                      default='purple',
                      validators=[DataRequired()])
    course_type = SelectField('Loại khóa học', choices=[('basic', 'Cơ bản'), ('advanced', 'Nâng cao')], default='basic', validators=[DataRequired()])
    icon_class = StringField('Lớp icon (ví dụ: fas fa-crown)', 
                             default='fas fa-crown',
                             validators=[DataRequired()])
    submit = SubmitField('Tạo khóa học')

class ChapterForm(FlaskForm):
    title = StringField('Tiêu đề chương', validators=[DataRequired(), Length(min=5, max=100)])
    video_url = StringField('URL Video', validators=[DataRequired()])
    submit = SubmitField('Lưu chương')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Gửi liên kết đặt lại mật khẩu')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Mật khẩu mới', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu mới', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đặt lại mật khẩu')

class TestCaseForm(FlaskForm):
    """Form cho test case"""
    input_data = TextAreaField('Input', validators=[DataRequired()], widget=TextArea())
    expected_output = TextAreaField('Expected Output', validators=[DataRequired()], widget=TextArea())
    description = StringField('Mô tả (tùy chọn)', validators=[Optional()])
    is_hidden = BooleanField('Test case ẩn')

class ProgrammingExerciseForm(FlaskForm):
    """Form cho bài tập lập trình"""
    title = StringField('Tiêu đề bài tập', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Mô tả chi tiết', validators=[DataRequired(), Length(min=20)], widget=TextArea())
    language_supported = SelectField('Ngôn ngữ lập trình', 
                                   choices=[
                                       ('python', 'Python'),
                                       ('java', 'Java'),
                                       ('cpp', 'C++'),
                                       ('javascript', 'JavaScript'),
                                       ('csharp', 'C#'),
                                       ('php', 'PHP'),
                                       ('ruby', 'Ruby'),
                                       ('go', 'Go'),
                                       ('rust', 'Rust'),
                                       ('swift', 'Swift')
                                   ],
                                   validators=[DataRequired()])
    time_limit = IntegerField('Giới hạn thời gian (giây)', validators=[Optional()], default=5)
    memory_limit = IntegerField('Giới hạn bộ nhớ (MB)', validators=[Optional()], default=128)
    is_visible = BooleanField('Hiển thị cho sinh viên', default=True)
    
    # Test cases sẽ được xử lý riêng trong controller
    test_cases_json = TextAreaField('Test Cases (JSON)', widget=TextArea())

class CodeSubmissionForm(FlaskForm):
    """Form cho nộp bài code"""
    code = TextAreaField('Mã nguồn', validators=[DataRequired()], widget=TextArea())
    language = SelectField('Ngôn ngữ', 
                          choices=[
                              ('python', 'Python'),
                              ('java', 'Java'),
                              ('cpp', 'C++'),
                              ('javascript', 'JavaScript'),
                              ('csharp', 'C#'),
                              ('php', 'PHP'),
                              ('ruby', 'Ruby'),
                              ('go', 'Go'),
                              ('rust', 'Rust'),
                              ('swift', 'Swift')
                          ],
                          validators=[DataRequired()])

class ExerciseFilterForm(FlaskForm):
    """Form lọc bài tập"""
    language = SelectField('Ngôn ngữ', 
                          choices=[
                              ('', 'Tất cả'),
                              ('python', 'Python'),
                              ('java', 'Java'),
                              ('cpp', 'C++'),
                              ('javascript', 'JavaScript'),
                              ('csharp', 'C#'),
                              ('php', 'PHP'),
                              ('ruby', 'Ruby'),
                              ('go', 'Go'),
                              ('rust', 'Rust'),
                              ('swift', 'Swift')
                          ])
    status = SelectField('Trạng thái',
                        choices=[
                            ('', 'Tất cả'),
                            ('visible', 'Đang hiển thị'),
                            ('hidden', 'Đang ẩn')
                        ])
    search = StringField('Tìm kiếm theo tên')

class ManualFeedbackForm(FlaskForm):
    """Form cho phản hồi thủ công của giảng viên"""
    manual_feedback = TextAreaField('Phản hồi thủ công', widget=TextArea())
    score_adjustment = FloatField('Điều chỉnh điểm (±)', validators=[Optional()])