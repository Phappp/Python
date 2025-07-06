from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from app.forms import CourseForm, ChapterForm
from app.controllers.course_controller import CourseController
from app.utils.decorators import role_required, login_required
from app.models.course_model import Course, CourseReview

course_bp = Blueprint('course', __name__, url_prefix='/courses')

@course_bp.route('/')
@login_required
def view_courses():
    """
    Route để hiển thị danh sách tất cả khóa học có sẵn cho sinh viên.
    """
    if session.get('role') != 'student':
        flash('Chỉ sinh viên mới có thể xem danh sách khóa học.', 'warning')
        return redirect(url_for('main.home'))
    
    courses = list(Course.get_all())
    basic_courses = [c for c in courses if c.get('course_type') == 'basic']
    advanced_courses = [c for c in courses if c.get('course_type') == 'advanced']
    return render_template('courses/view_courses.html', 
        basic_courses=basic_courses, 
        advanced_courses=advanced_courses, 
        title="Danh sách khóa học")

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
    # Hiển thị tất cả các khóa học cho lecture (bao gồm cả admin tạo và mình tạo)
    courses = list(Course.get_all())
    return render_template('courses/manage_courses.html', courses=courses, title="Quản lý khóa học")

@course_bp.route('/<course_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('lecture')
def edit_course(course_id):
    course = Course.find_by_id(course_id)
    if not course:
        flash('Khóa học không tồn tại.', 'danger')
        return redirect(url_for('course.manage_courses'))
    
    # Cho phép lecture chỉnh sửa khóa học do mình tạo hoặc do admin tạo
    if course['created_by'] != session['username'] and session.get('role') != 'admin':
        flash('Bạn không có quyền chỉnh sửa khóa học này.', 'danger')
        return redirect(url_for('course.manage_courses'))
        
    form = CourseForm(data=course)
    response = CourseController.update_course(course_id, form)
    return response or render_template('courses/create.html', form=form, title="Chỉnh sửa khóa học")

@course_bp.route('/<course_id>/delete', methods=['POST'])
@login_required
@role_required('lecture')
def delete_course(course_id):
    course = Course.find_by_id(course_id)
    if not course:
        flash('Khóa học không tồn tại.', 'danger')
        return redirect(url_for('course.manage_courses'))
    
    # Chỉ cho phép lecture xóa khóa học do chính mình tạo
    if course['created_by'] != session['username']:
        flash('Bạn chỉ có thể xóa khóa học do mình tạo.', 'warning')
        return redirect(url_for('course.manage_courses'))
    
    return CourseController.delete_course(course_id)
    
@course_bp.route('/<course_id>/chapters', methods=['GET', 'POST'])
@login_required
@role_required('lecture')
def manage_chapters(course_id):
    course = Course.find_by_id(course_id)
    if not course:
        flash('Khóa học không tồn tại.', 'danger')
        return redirect(url_for('course.manage_courses'))

    # Cho phép lecture quản lý chương của mọi khóa học (cả do mình tạo và do admin tạo)
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
    if not course:
        flash('Khóa học không tồn tại.', 'danger')
        return redirect(url_for('course.manage_courses'))

    # Cho phép lecture xóa chương của mọi khóa học (cả do mình tạo và do admin tạo)
    Course.delete_chapter(course_id, chapter_id)
    flash('Đã xóa chương thành công!', 'success')
    return redirect(url_for('course.manage_chapters', course_id=course_id))

@course_bp.route('/<course_id>/chapters/<chapter_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('lecture')
def edit_chapter(course_id, chapter_id):
    course = Course.find_by_id(course_id)
    if not course:
        flash('Khóa học không tồn tại.', 'danger')
        return redirect(url_for('course.manage_chapters', course_id=course_id))

    # Cho phép lecture chỉnh sửa chương của mọi khóa học (cả do mình tạo và do admin tạo)
    chapter_data = Course.find_chapter(course_id, chapter_id)
    if not chapter_data or not chapter_data.get('chapters'):
        flash('Chương không tồn tại.', 'danger')
        return redirect(url_for('course.manage_chapters', course_id=course_id))
    chapter = chapter_data['chapters'][0]
    form = ChapterForm(data=chapter)
    if form.validate_on_submit():
        response = CourseController.update_chapter(course_id, chapter_id, form)
        if response:
            return response
    return render_template('courses/edit_chapter.html', form=form, course=course, chapter=chapter, title='Chỉnh sửa chương')

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

@course_bp.route('/<course_id>/review', methods=['POST'])
@login_required
def submit_review(course_id):
    if session.get('role') != 'student':
        return jsonify({'success': False, 'message': 'Chỉ sinh viên mới được đánh giá.'}), 403
    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment', '')
    username = session.get('username')
    if not rating or int(rating) < 1 or int(rating) > 5:
        return jsonify({'success': False, 'message': 'Số sao không hợp lệ.'}), 400
    CourseReview.add_review(course_id, username, rating, comment)
    return jsonify({'success': True, 'message': 'Đã lưu đánh giá.'})

@course_bp.route('/<course_id>/reviews', methods=['GET'])
def get_reviews(course_id):
    reviews = CourseReview.get_reviews_by_course(course_id)
    # Ẩn _id, chỉ trả về thông tin cần thiết
    result = [{
        'username': r.get('username'),
        'rating': r.get('rating'),
        'comment': r.get('comment'),
        'created_at': r.get('created_at').strftime('%d/%m/%Y %H:%M') if r.get('created_at') else ''
    } for r in reviews]
    return jsonify({'reviews': result}) 