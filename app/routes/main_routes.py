from flask import Blueprint, render_template, session

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if 'username' in session:
        username = session['username']
        role = session.get('role', 'student')
        role_display = 'Sinh viên' if role == 'student' else 'Giảng viên'
        return render_template('home.html', username=username, role=role, role_display=role_display)
    return render_template('home.html')