from flask_wtf import FlaskForm
<<<<<<< HEAD
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Tên người dùng', 
                         validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Mật khẩu', 
                           validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu',
                                  validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Vai trò', 
                      choices=[('student', 'Sinh viên'), ('lecture', 'Giảng viên')],
                      default='student')
=======
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email

class RegistrationForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu', 
                                   validators=[DataRequired(), EqualTo('password')])
>>>>>>> b7b4b2b9d38e110421f1f0807531b9b5524ceb48
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