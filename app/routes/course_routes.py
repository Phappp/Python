from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.forms import CourseForm, ChapterForm
from app.controllers.course_controller import CourseController
from app.utils.decorators import role_required, login_required
from app.models.course_model import Course

course_bp = Blueprint('course', __name__, url_prefix='/courses')

@course_bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required('lecture')
def create_course():
    """
    Route để hiển thị form và xử lý việc tạo khóa học mới.
    Chỉ cho phép giảng viên truy cập.
    """
    form = CourseForm()
    response = CourseController.create_course(form)
    # Nếu form không hợp lệ hoặc có lỗi, render lại template với form
    return response or render_template('courses/create.html', form=form, title="Tạo khóa học")

@course_bp.route('/manage')
@login_required
@role_required('lecture')
def manage_courses():
    courses = list(Course.find_by_creator(session['username']))
    return render_template('courses/manage_courses.html', courses=courses, title="Quản lý khóa học")

@course_bp.route('/<course_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('lecture')
def edit_course(course_id):
    course = Course.find_by_id(course_id)
    if not course or course['created_by'] != session['username']:
        flash('Khóa học không tồn tại hoặc bạn không có quyền chỉnh sửa.', 'danger')
        return redirect(url_for('course.manage_courses'))
        
    form = CourseForm(data=course)
    response = CourseController.update_course(course_id, form)
    return response or render_template('courses/create.html', form=form, title="Chỉnh sửa khóa học")

@course_bp.route('/<course_id>/delete', methods=['POST'])
@login_required
@role_required('lecture')
def delete_course(course_id):
    course = Course.find_by_id(course_id)
    if not course or course['created_by'] != session['username']:
        flash('Khóa học không tồn tại hoặc bạn không có quyền xóa.', 'danger')
        return redirect(url_for('course.manage_courses'))
    
    return CourseController.delete_course(course_id)
    
@course_bp.route('/<course_id>/chapters', methods=['GET', 'POST'])
@login_required
@role_required('lecture')
def manage_chapters(course_id):
    course = Course.find_by_id(course_id)
    if not course or course['created_by'] != session['username']:
        flash('Khóa học không tồn tại hoặc bạn không có quyền quản lý.', 'danger')
        return redirect(url_for('course.manage_courses'))

    form = ChapterForm()
    response = CourseController.add_chapter(course_id, form)
    
    # Lấy lại thông tin khóa học để hiển thị các chương đã có
    updated_course = Course.find_by_id(course_id)
    chapters = updated_course.get('chapters', [])
    
    return response or render_template(
        'courses/manage_chapters.html', 
        form=form, 
        course=updated_course, 
        chapters=chapters,
        title="Quản lý chương"
    )

@course_bp.route('/<course_id>/chapters/<chapter_id>/delete', methods=['POST'])
@login_required
@role_required('lecture')
def delete_chapter(course_id, chapter_id):
    course = Course.find_by_id(course_id)
    if not course or course['created_by'] != session['username']:
        flash('Bạn không có quyền thực hiện hành động này.', 'danger')
        return redirect(url_for('course.manage_courses'))
        
    Course.delete_chapter(course_id, chapter_id)
    flash('Đã xóa chương thành công!', 'success')
    return redirect(url_for('course.manage_chapters', course_id=course_id))

def get_embed_url(youtube_url):
    """
    Chuyển đổi URL YouTube tiêu chuẩn thành URL có thể nhúng được.
    Ví dụ: https://www.youtube.com/watch?v=... -> https://www.youtube.com/embed/...
    """
    if not isinstance(youtube_url, str):
        return ""
        
    video_id = None
    if "watch?v=" in youtube_url:
        video_id = youtube_url.split("watch?v=")[1].split('&')[0]
    elif "youtu.be/" in youtube_url:
        video_id = youtube_url.split("youtu.be/")[1].split('?')[0]
    
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}"
    return youtube_url # Trả về URL gốc nếu không nhận dạng được

@course_bp.route('/<course_id>/view')
@login_required
def view_course(course_id):
    if session.get('role') != 'student':
        flash('Chỉ sinh viên mới có thể xem khóa học.', 'warning')
        return redirect(url_for('main.home'))

    course = Course.find_by_id(course_id)
    if not course:
        flash('Khóa học không tồn tại.', 'danger')
        return redirect(url_for('main.home'))
    
    # Chuẩn bị URL nhúng cho mỗi chương
    chapters = course.get('chapters', [])
    for chapter in chapters:
        chapter['video_url_embed'] = get_embed_url(chapter['video_url'])

    return render_template(
        'courses/view_course.html', 
        course=course,
        chapters=chapters,
        title=course['name']
    ) 