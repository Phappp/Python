from flask import Blueprint, render_template, session, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if 'username' in session:
<<<<<<< HEAD
        username = session['username']
        role = session.get('role', 'student')
        role_display = 'Sinh viên' if role == 'student' else 'Giảng viên'
        return render_template('home.html', username=username, role=role, role_display=role_display)
    return render_template('home.html')
=======
        return render_template('home.html', username=session['username'])
    return redirect(url_for('auth.login'))
>>>>>>> b7b4b2b9d38e110421f1f0807531b9b5524ceb48
