from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from app.forms import ProgrammingExerciseForm, CodeSubmissionForm, ManualFeedbackForm, ExerciseFilterForm
from app.controllers.programming_exercise_controller import ProgrammingExerciseController
from app.models.exercise_model import Exercise, Submission
from app.utils.decorators import role_required, login_required
from bson.objectid import ObjectId
import json

programming_exercise_bp = Blueprint('programming_exercise', __name__, url_prefix='/programming-exercises')

@programming_exercise_bp.route('/')
@login_required
@role_required('lecture')
def manage_exercises():
    """
    Quản lý danh sách bài tập lập trình (cho giảng viên)
    """
    form = ExerciseFilterForm()
    
    # Lấy tham số lọc
    language = request.args.get('language', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    
    # Lấy bài tập của giảng viên
    exercises = list(Exercise.find_by_creator(session['username']))
    
    # Áp dụng bộ lọc
    if language:
        exercises = [ex for ex in exercises if language in ex.get('language_supported', [])]
    
    if status == 'visible':
        exercises = [ex for ex in exercises if ex.get('is_visible', True)]
    elif status == 'hidden':
        exercises = [ex for ex in exercises if not ex.get('is_visible', True)]
    
    if search:
        exercises = [ex for ex in exercises if search.lower() in ex.get('title', '').lower()]
    
    # Đếm số lượng bài tập Python
    python_count = sum('python' in ex.get('language_supported', []) for ex in exercises)
    
    return render_template('programming_exercises/manage_exercises.html', 
                         exercises=exercises, form=form, title="Quản lý bài tập lập trình", python_count=python_count)

@programming_exercise_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('lecture')
def create_exercise():
    """
    Tạo bài tập lập trình mới
    """
    form = ProgrammingExerciseForm()
    response = ProgrammingExerciseController.create_exercise(form)
    
    return response or render_template('programming_exercises/create_exercise.html', 
                                     form=form, title="Tạo bài tập lập trình")

@programming_exercise_bp.route('/<exercise_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('lecture')
def edit_exercise(exercise_id):
    """
    Chỉnh sửa bài tập lập trình
    """
    exercise = Exercise.find_by_id(exercise_id)
    if not exercise or exercise['created_by'] != session['username']:
        flash('Bạn không có quyền chỉnh sửa bài tập này.', 'danger')
        return redirect(url_for('programming_exercise.manage_exercises'))
    
    form = ProgrammingExerciseForm(data=exercise)
    
    # Chuyển test cases thành JSON
    if exercise.get('test_cases'):
        form.test_cases_json.data = json.dumps(exercise['test_cases'], indent=2, ensure_ascii=False)
    
    response = ProgrammingExerciseController.update_exercise(exercise_id, form)
    
    return response or render_template('programming_exercises/edit_exercise.html', 
                                     form=form, exercise=exercise, title="Chỉnh sửa bài tập")

@programming_exercise_bp.route('/<exercise_id>/delete', methods=['POST'])
@login_required
@role_required('lecture')
def delete_exercise(exercise_id):
    """
    Xóa bài tập lập trình
    """
    exercise = Exercise.find_by_id(exercise_id)
    if not exercise or exercise['created_by'] != session['username']:
        flash('Bạn không có quyền xóa bài tập này.', 'danger')
        return redirect(url_for('programming_exercise.manage_exercises'))
    
    Exercise.delete(exercise_id)
    flash('Đã xóa bài tập thành công!', 'success')
    return redirect(url_for('programming_exercise.manage_exercises'))

@programming_exercise_bp.route('/<exercise_id>/toggle-visibility', methods=['POST'])
@login_required
@role_required('lecture')
def toggle_visibility(exercise_id):
    """
    Bật/tắt hiển thị bài tập
    """
    exercise = Exercise.find_by_id(exercise_id)
    if not exercise or exercise['created_by'] != session['username']:
        flash('Bạn không có quyền thay đổi trạng thái bài tập này.', 'danger')
        return redirect(url_for('programming_exercise.manage_exercises'))
    
    Exercise.toggle_visibility(exercise_id)
    new_status = "hiển thị" if not exercise.get('is_visible', True) else "ẩn"
    flash(f'Đã {new_status} bài tập!', 'success')
    return redirect(url_for('programming_exercise.manage_exercises'))

@programming_exercise_bp.route('/<exercise_id>/submissions')
@login_required
@role_required('lecture')
def view_submissions(exercise_id):
    """
    Xem danh sách nộp bài của một bài tập
    """
    exercise = Exercise.find_by_id(exercise_id)
    if not exercise or exercise['created_by'] != session['username']:
        flash('Bạn không có quyền xem bài tập này.', 'danger')
        return redirect(url_for('programming_exercise.manage_exercises'))
    
    submissions = list(Submission.find_by_exercise(exercise_id))
    
    # Lấy thống kê
    stats = Submission.get_statistics(exercise_id)
    
    return render_template('programming_exercises/view_submissions.html', 
                         exercise=exercise, submissions=submissions, stats=stats,
                         title=f"Bài nộp - {exercise['title']}")

@programming_exercise_bp.route('/submission/<submission_id>')
@login_required
def view_submission(submission_id):
    """
    Xem chi tiết một bài nộp
    """
    submission = Submission.find_by_id(submission_id)
    if not submission:
        flash('Không tìm thấy bài nộp.', 'danger')
        return redirect(url_for('main.home'))
    # Kiểm tra quyền xem
    if session.get('role') == 'lecture':
        exercise = Exercise.find_by_id(submission['exercise_id'])
        if not exercise or exercise['created_by'] != session['username']:
            flash('Bạn không có quyền xem bài nộp này.', 'danger')
            return redirect(url_for('programming_exercise.manage_exercises'))
    elif session.get('role') == 'student':
        if submission['user_id'] != session['username']:
            flash('Bạn không có quyền xem bài nộp này.', 'danger')
            return redirect(url_for('programming_exercise.student_exercises'))
    exercise = Exercise.find_by_id(submission['exercise_id'])
    form = ManualFeedbackForm()
    # Lấy lịch sử các lần nộp của sinh viên cho bài tập này
    submission_history = list(Submission.find_by_user(session['username'])) if session.get('role') == 'student' else []
    # Lọc chỉ các submission cho bài tập này
    if submission_history:
        submission_history = [sub for sub in submission_history if str(sub['exercise_id']) == str(exercise['_id'])]
    return render_template('programming_exercises/view_submission.html', 
                         submission=submission, exercise=exercise, form=form,
                         submission_history=submission_history,
                         title="Chi tiết bài nộp")

@programming_exercise_bp.route('/submission/<submission_id>/feedback', methods=['POST'])
@login_required
@role_required('lecture')
def add_manual_feedback(submission_id):
    """
    Thêm phản hồi thủ công cho bài nộp
    """
    form = ManualFeedbackForm()
    response = ProgrammingExerciseController.add_manual_feedback(submission_id, form)
    
    return response or redirect(url_for('programming_exercise.view_submission', submission_id=submission_id))

# Routes cho sinh viên
@programming_exercise_bp.route('/student')
@login_required
def student_exercises():
    """
    Danh sách bài tập cho sinh viên
    """
    # Chỉ lấy bài tập đang hiển thị
    exercises = [ex for ex in Exercise.get_visible() if ex.get('is_visible', True)]
    # Rút gọn mô tả cho mỗi bài
    for ex in exercises:
        ex['short_description'] = ex.get('description', '')[:120] + ('...' if len(ex.get('description', '')) > 120 else '')
    # Lấy các bài nộp của sinh viên
    all_submissions = list(Submission.find_by_user(session['username']))
    submissions = {str(sub['exercise_id']): sub for sub in all_submissions}
    # Lấy điểm cao nhất cho từng bài
    best_scores = {str(ex['_id']): Submission.get_best_score(ex['_id'], session['username']) for ex in exercises}
    # Sắp xếp và giới hạn 5 bài nộp gần đây nhất
    recent_submissions = sorted(all_submissions, key=lambda x: x['submitted_at'], reverse=True)[:5]
    return render_template('programming_exercises/student_exercises.html', 
                         exercises=exercises, submissions=submissions, recent_submissions=recent_submissions,
                         best_scores=best_scores,
                         title="Bài tập lập trình")

@programming_exercise_bp.route('/<exercise_id>/submit', methods=['GET', 'POST'])
@login_required
def submit_exercise(exercise_id):
    """
    Nộp bài tập lập trình
    """
    exercise = Exercise.find_by_id(exercise_id)
    if not exercise or not exercise.get('is_visible', True):
        flash('Bài tập không tồn tại hoặc không khả dụng.', 'danger')
        return redirect(url_for('programming_exercise.student_exercises'))
    
    form = CodeSubmissionForm()
    response = ProgrammingExerciseController.submit_code(exercise_id, form)
    
    return response or render_template('programming_exercises/submit_exercise.html', 
                                     form=form, exercise=exercise,
                                     title=f"Nộp bài - {exercise['title']}")

@programming_exercise_bp.route('/<exercise_id>/preview')
@login_required
def preview_exercise(exercise_id):
    """
    Xem trước bài tập (cho sinh viên)
    """
    exercise = Exercise.find_by_id(exercise_id)
    if not exercise or not exercise.get('is_visible', True):
        flash('Bài tập không tồn tại hoặc không khả dụng.', 'danger')
        return redirect(url_for('programming_exercise.student_exercises'))
    
    return render_template('programming_exercises/preview_exercise.html', 
                         exercise=exercise, title=exercise['title'])

# API routes
@programming_exercise_bp.route('/api/test-code', methods=['POST'])
@login_required
def test_code():
    """
    API để test code trước khi nộp
    """
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        input_data = data.get('input', '')
        
        if not code:
            return jsonify({'error': 'Code không được để trống'}), 400
        
        # Chạy test code
        from app.controllers.programming_exercise_controller import ProgrammingExerciseController
        result = ProgrammingExerciseController._run_code(code, language, input_data, 5, 128)
        
        return jsonify({
            'output': result['output'],
            'error': result['error'],
            'execution_time': result['execution_time'],
            'memory_used': result['memory_used']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@programming_exercise_bp.route('/api/export-submissions/<exercise_id>')
@login_required
@role_required('lecture')
def export_submissions(exercise_id):
    """
    Export danh sách bài nộp thành CSV
    """
    exercise = Exercise.find_by_id(exercise_id)
    if not exercise or exercise['created_by'] != session['username']:
        flash('Bạn không có quyền export bài tập này.', 'danger')
        return redirect(url_for('programming_exercise.manage_exercises'))
    
    submissions = list(Submission.find_by_exercise(exercise_id))
    
    # Tạo CSV content
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Sinh viên', 'Thời gian nộp', 'Ngôn ngữ', 'Điểm', 'Thời gian chạy', 'Bộ nhớ sử dụng'])
    
    # Data
    for sub in submissions:
        writer.writerow([
            sub['user_id'],
            sub['submitted_at'].strftime('%Y-%m-%d %H:%M:%S'),
            sub['language'],
            sub.get('score', 'Chưa chấm'),
            sub.get('execution_time', 'N/A'),
            sub.get('memory_used', 'N/A')
        ])
    
    from flask import make_response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=submissions_{exercise_id}.csv'
    
    return response 