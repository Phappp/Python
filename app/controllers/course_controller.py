from flask import redirect, url_for, flash, session, request
from app.models.course_model import Course
from app.forms import CourseForm, ChapterForm

class CourseController:
    @staticmethod
    def create_course(form):
        """
        Xử lý việc tạo khóa học từ form.
        """
        if form.validate_on_submit():
            try:
                Course.create(
                    name=form.name.data,
                    description=form.description.data,
                    original_price=form.original_price.data,
                    discounted_price=form.discounted_price.data,
                    created_by=session.get('username'),
                    color=form.color.data,
                    icon_class=form.icon_class.data,
                    course_type=form.course_type.data
                )
                flash('Khóa học đã được tạo thành công!', 'success')
                return redirect(url_for('main.home'))
            except Exception as e:
                flash(f'Đã có lỗi xảy ra: {e}', 'danger')
        return None
        
    @staticmethod
    def add_chapter(course_id, form):
        if form.validate_on_submit():
            try:
                Course.add_chapter(
                    course_id=course_id,
                    title=form.title.data,
                    video_url=form.video_url.data
                )
                flash('Chương đã được thêm thành công!', 'success')
                return redirect(url_for('course.manage_chapters', course_id=course_id))
            except Exception as e:
                flash(f'Đã có lỗi xảy ra khi thêm chương: {e}', 'danger')
        return None

    @staticmethod
    def update_course(course_id, form):
        if form.validate_on_submit():
            try:
                Course.update(course_id, {
                    'name': form.name.data,
                    'description': form.description.data,
                    'original_price': form.original_price.data,
                    'discounted_price': form.discounted_price.data,
                    'color': form.color.data,
                    'icon_class': form.icon_class.data,
                    'course_type': form.course_type.data
                })
                flash('Cập nhật khóa học thành công!', 'success')
                return redirect(url_for('course.manage_courses'))
            except Exception as e:
                flash(f'Lỗi khi cập nhật khóa học: {e}', 'danger')
        return None

    @staticmethod
    def delete_course(course_id):
        try:
            Course.delete(course_id)
            flash('Xóa khóa học thành công!', 'success')
        except Exception as e:
            flash(f'Lỗi khi xóa khóa học: {e}', 'danger')
        return redirect(url_for('course.manage_courses'))

    @staticmethod
    def update_chapter(course_id, chapter_id, form):
        if form.validate_on_submit():
            try:
                Course.update_chapter(
                    course_id=course_id,
                    chapter_id=chapter_id,
                    title=form.title.data,
                    video_url=form.video_url.data
                )
                flash('Cập nhật chương thành công!', 'success')
                return redirect(url_for('course.manage_chapters', course_id=course_id))
            except Exception as e:
                flash(f'Đã có lỗi xảy ra khi cập nhật chương: {e}', 'danger')
        return None 