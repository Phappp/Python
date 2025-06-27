from flask import Blueprint, request
from app.controllers.admin_controller import AdminController, PermissionUserController
from app.forms import RegistrationForm, ProfileEditForm, CourseForm
from app.models.course_model import Course
from app.utils.decorators import role_required

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

@admin_bp.route('/dashboard')
@role_required('admin')
def admin_dashboard():
    return AdminController.admin_dashboard() 