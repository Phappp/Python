from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.models.course_model import Course
from app.models.notification_model import Notification
from app.controllers.search_controller import search_bp

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if 'username' in session:
        role = session.get('role', 'student')
        if role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        elif role == 'lecture':
            # Redirect lecture về dashboard thống kê
            return redirect(url_for('statistics.lecture_dashboard'))
        
        username = session['username']
        role_display = 'Sinh viên' if role == 'student' else 'Giảng viên'
        courses = None
        notifications = []
        unread_notifications = []
        if role == 'student':
            courses = list(Course.get_all())
            # Chỉ lấy các thông báo chưa đọc
            notifications = Notification.get_unread(username)
            # Lấy các thông báo mới nhất cho mỗi bài tập (không trùng lặp)
            unread_notifications = Notification.get_latest_per_exercise(username, limit=5)
        return render_template('home.html', 
                               username=username, 
                               role=role, 
                               role_display=role_display,
                               courses=courses,
                               notifications=notifications,
                               unread_notifications=unread_notifications)
    return render_template('home.html')

@main_bp.route('/notifications/mark_all_read', methods=['POST'])
def mark_all_notifications_read():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    Notification.mark_all_read(session['username'])
    return jsonify({'success': True})

@main_bp.route('/notifications/mark_read/<notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    from app.models.notification_model import Notification
    Notification.mark_read(notification_id, session['username'])
    return jsonify({'success': True})

# API for paginated notifications (for bell dropdown)
@main_bp.route('/notifications/paginated')
def notifications_paginated():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 5))
    notifications = Notification.get_paginated(session['username'], skip=skip, limit=limit)
    # Convert ObjectId and datetime to string for JSON
    for n in notifications:
        n['_id'] = str(n['_id'])
        if 'created_at' in n:
            n['created_at'] = n['created_at'].strftime('%d/%m/%Y %H:%M')
    return jsonify({'success': True, 'notifications': notifications})

