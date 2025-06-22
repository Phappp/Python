from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email

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
    submit = SubmitField('Đăng nhập')

class OTPForm(FlaskForm):
    otp = StringField('Mã OTP', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Xác thực')

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
    icon_class = StringField('Lớp icon (ví dụ: fas fa-crown)', 
                             default='fas fa-crown',
                             validators=[DataRequired()])
    submit = SubmitField('Tạo khóa học')

class ChapterForm(FlaskForm):
    title = StringField('Tiêu đề chương', validators=[DataRequired(), Length(min=5, max=100)])
    video_url = StringField('URL Video', validators=[DataRequired()])
    submit = SubmitField('Lưu chương')