from flask import Blueprint, render_template
from app.forms import RegistrationForm, LoginForm
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    response = AuthController.register(form)
    return response or render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    response = AuthController.login(form)
    return response or render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    return AuthController.logout()