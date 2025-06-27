from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from app.controllers.admin_controller import AdminController, PermissionUserController
from app.forms import RegistrationForm, ProfileEditForm, CourseForm
from app.models.course_model import Course
from app.models.user_model import User
from app.utils.decorators import role_required, custom_permission_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/users')
@role_required('admin')
def list_users():
    return AdminController.list_users()

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@role_required('admin')
def add_user():
    form = RegistrationForm()
    return AdminController.add_user(form)

@admin_bp.route('/users/edit/<username>', methods=['GET', 'POST'])
@role_required('admin')
def edit_user(username):
    form = ProfileEditForm()
    return AdminController.edit_user(username, form)

@admin_bp.route('/users/delete/<username>', methods=['POST'])
@role_required('admin')
def delete_user(username):
    return AdminController.delete_user(username)

@admin_bp.route('/users/change-role/<username>', methods=['POST'])
@role_required('admin')
def change_role(username):
    new_role = request.form.get('role')
    return AdminController.change_role(username, new_role)

@admin_bp.route('/users/reset-password/<username>', methods=['POST'])
@role_required('admin')
def reset_password(username):
    new_password = request.form.get('new_password')
    return AdminController.reset_password(username, new_password)

@admin_bp.route('/users/toggle-active/<username>', methods=['POST'])
@role_required('admin')
def toggle_active(username):
    active = request.form.get('active', 'true') == 'true'
    return AdminController.toggle_active(username, active)

@admin_bp.route('/courses')
@role_required('admin')
def list_courses():
    return AdminController.list_courses()

@admin_bp.route('/courses/add', methods=['GET', 'POST'])
@role_required('admin')
def add_course():
    form = CourseForm()
    return AdminController.add_course(form)

@admin_bp.route('/courses/edit/<course_id>', methods=['GET', 'POST'])
@role_required('admin')
def edit_course(course_id):
    form = CourseForm()
    return AdminController.edit_course(course_id, form)

@admin_bp.route('/courses/delete/<course_id>', methods=['POST'])
@role_required('admin')
def delete_course(course_id):
    return AdminController.delete_course(course_id)

@admin_bp.route('/courses/<course_id>/students')
@role_required('admin')
def view_course_students(course_id):
    return AdminController.view_course_students(course_id)

@admin_bp.route('/stats')
@role_required('admin')
def stats():
    return AdminController.stats()

@admin_bp.route('/export/excel')
@role_required('admin')
def export_excel():
    return AdminController.export_excel()

@admin_bp.route('/roles')
@role_required('admin')
def roles():
    return AdminController.roles()

@admin_bp.route('/roles/<role_name>/users')
@role_required('admin')
def users_by_role(role_name):
    return PermissionUserController.users_by_role(role_name)

@admin_bp.route('/users/<username>/permissions', methods=['GET', 'POST'])
@role_required('admin')
def view_user_permissions(username):
    if request.method == 'POST':
        return PermissionUserController.update_user_permissions(username)
    return PermissionUserController.view_user_permissions(username)

@admin_bp.route('/my-permissions')
def view_my_permissions():
    """Route cho lecture và student xem quyền riêng của mình"""
    if 'username' not in session:
        flash('Vui lòng đăng nhập để truy cập trang này!', 'warning')
        return redirect(url_for('auth.login'))
    
    username = session['username']
    user = User.find_by_username(username)
    if not user:
        flash('Không tìm thấy thông tin người dùng!', 'danger')
        return redirect(url_for('main.home'))
    
    role = user.get('role')
    user_permissions = user.get('permissions', [])
    
    # Quyền mặc định từ role
    if role == 'admin':
        default_permissions = ['manage_users', 'manage_courses', 'manage_exercises', 'view_stats', 'config_system']
    elif role == 'lecture':
        default_permissions = ['manage_courses', 'manage_exercises']
    elif role == 'student':
        default_permissions = ['view_courses', 'do_exercises']
    else:
        default_permissions = []
    
    # Tạo mapping tên hiển thị cho các quyền
    permission_display_names = {
        'manage_users': 'Quản lý người dùng',
        'manage_courses': 'Quản lý khóa học',
        'manage_exercises': 'Quản lý bài tập',
        'view_stats': 'Xem thống kê',
        'config_system': 'Cấu hình hệ thống',
        'export_data': 'Xuất dữ liệu',
        'manage_roles': 'Quản lý vai trò',
        'view_logs': 'Xem nhật ký hệ thống',
        'manage_backups': 'Quản lý sao lưu',
        'system_monitoring': 'Giám sát hệ thống'
    }
    
    return render_template('admin/my_permissions.html', 
                         user=user, 
                         role=role, 
                         user_permissions=user_permissions,
                         default_permissions=default_permissions,
                         permission_display_names=permission_display_names)

# Demo routes cho các quyền riêng
@admin_bp.route('/demo/view-stats')
@custom_permission_required('view_stats')
def demo_view_stats():
    """Demo route cho quyền xem thống kê"""
    return render_template('admin/demo_view_stats.html')

@admin_bp.route('/demo/export-data')
@custom_permission_required('export_data')
def demo_export_data():
    """Demo route cho quyền xuất dữ liệu"""
    return render_template('admin/demo_export_data.html')

@admin_bp.route('/demo/system-monitoring')
@custom_permission_required('system_monitoring')
def demo_system_monitoring():
    """Demo route cho quyền giám sát hệ thống"""
    return render_template('admin/demo_system_monitoring.html')

@admin_bp.route('/demo/view-logs')
@custom_permission_required('view_logs')
def demo_view_logs():
    """Demo route cho quyền xem nhật ký"""
    return render_template('admin/demo_view_logs.html')

@admin_bp.route('/dashboard')
@role_required('admin')
def admin_dashboard():
    return AdminController.admin_dashboard() 