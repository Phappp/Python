from flask import Blueprint, render_template, session, redirect, url_for
from app.models.course_model import Course

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if 'username' in session:
        role = session.get('role', 'student')
        if role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        username = session['username']
        role_display = 'Sinh viên' if role == 'student' else 'Giảng viên'
        
        # Nếu là sinh viên, hiển thị danh sách khóa học
        courses = None
        if role == 'student':
            courses = list(Course.get_all())
            
        return render_template('home.html', 
                               username=username, 
                               role=role, 
                               role_display=role_display,
                               courses=courses)

    # Nếu chưa đăng nhập, hiển thị trang chủ mặc định
    return render_template('home.html')

