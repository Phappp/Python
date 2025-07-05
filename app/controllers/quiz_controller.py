from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from app.models.quiz_model import Quiz, QuizQuestion, QuizSubmission
from app.utils.llm_gemini import generate_quiz_questions
from bson.objectid import ObjectId
from app.utils.decorators import login_required, role_required

quiz_bp = Blueprint('quiz', __name__)

# Trang hiển thị
@quiz_bp.route('/quiz/create-page', methods=['GET'])
@login_required
@role_required('lecture')
def create_quiz_page():
    """
    Trang tạo quiz mới
    """
    return render_template('quiz/create_quiz.html')

@quiz_bp.route('/quiz/list-page', methods=['GET'])
@login_required
def list_quizzes_page():
    """
    Trang hiển thị danh sách quiz
    """
    return render_template('quiz/list_quiz.html', 
                         role=session.get('role'), 
                         current_user=session.get('username'))

@quiz_bp.route('/quiz/do', methods=['GET'])
@login_required
@role_required('student')
def do_quiz_page():
    """
    Trang làm quiz cho sinh viên
    """
    return render_template('quiz/do_quiz.html')

@quiz_bp.route('/quiz/result', methods=['GET'])
@login_required
@role_required('student')
def quiz_result_page():
    """
    Trang xem kết quả quiz cho sinh viên
    """
    return render_template('quiz/my_quiz_result.html')

@quiz_bp.route('/quiz/my_quiz_result', methods=['GET'])
@login_required
@role_required('student')
def my_quiz_result_page():
    """
    Trang xem kết quả quiz cho sinh viên (alias)
    """
    return render_template('quiz/my_quiz_result.html')

@quiz_bp.route('/quiz/<quiz_id>/results-page', methods=['GET'])
@login_required
@role_required('lecture')
def quiz_results_page(quiz_id):
    """
    Trang xem kết quả quiz tổng hợp cho giảng viên
    """
    return render_template('quiz/quiz_results.html')

# API cho giảng viên
@quiz_bp.route('/quiz/create', methods=['POST'])
def create_quiz():
    """
    API cho giảng viên tạo Quiz mới, sử dụng AI để sinh câu hỏi.
    Body: {title, content, difficulty, created_by, num_questions}
    """
    data = request.json
    num_questions = data.get('num_questions', 5)
    # Gọi API AI sinh câu hỏi từ content và difficulty
    questions_data = generate_quiz_questions(data['content'], data['difficulty'], num_questions)
    # Tạo quiz trước để lấy quiz_id
    quiz = Quiz.create(
        title=data['title'],
        content=data['content'],
        difficulty=data['difficulty'],
        created_by=data['created_by'],
        questions=[],
        status='pending'
    )
    quiz_id = quiz.inserted_id
    # Lưu từng câu hỏi với quiz_id đúng, lấy ObjectId
    question_ids = []
    for q in questions_data:
        res = QuizQuestion.create(
            quiz_id=quiz_id,
            question_text=q['question_text'],
            options=q['options'],
            correct_answer=q['correct_answer'],
            explanation=q.get('explanation', None)
        )
        question_ids.append(res.inserted_id)
    # Cập nhật lại danh sách question_ids cho quiz
    Quiz.update(quiz_id, {'questions': question_ids})
    return jsonify({'quiz_id': str(quiz_id), 'message': 'Quiz created with questions.'})

@quiz_bp.route('/quiz/<quiz_id>/set_status', methods=['POST'])
def set_quiz_status(quiz_id):
    """
    Đổi trạng thái Quiz (pending/active)
    Body: {status}
    """
    data = request.json
    Quiz.set_status(quiz_id, data['status'])
    return jsonify({'message': 'Quiz status updated.'})

@quiz_bp.route('/quiz/<quiz_id>/results', methods=['GET'])
def get_quiz_results(quiz_id):
    """
    Xem kết quả nộp bài của sinh viên cho quiz này
    """
    submissions = list(QuizSubmission.find_by_quiz(quiz_id))
    for s in submissions:
        s['_id'] = str(s['_id'])
        s['student_id'] = str(s['student_id'])
    return jsonify({'submissions': submissions})

@quiz_bp.route('/quiz/<quiz_id>/student-submissions', methods=['GET'])
@login_required
@role_required('lecture')
def view_student_submissions(quiz_id):
    """
    Trang hiển thị danh sách sinh viên đã làm quiz
    """
    quiz = Quiz.find_by_id(quiz_id)
    if not quiz:
        flash('Không tìm thấy quiz.', 'danger')
        return redirect(url_for('quiz.list_quizzes'))
    
    # Lấy danh sách sinh viên đã làm quiz
    submissions = list(QuizSubmission.find_by_quiz(quiz_id))
    
    # Lấy thống kê
    stats = QuizSubmission.get_score_statistics(quiz_id)
    
    # Sắp xếp theo điểm từ cao xuống thấp
    submissions.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Chuyển đổi ObjectId thành string
    for s in submissions:
        s['_id'] = str(s['_id'])
        s['student_id'] = str(s['student_id'])
    
    return render_template('quiz/student_submissions.html', 
                         quiz=quiz, submissions=submissions, stats=stats)

@quiz_bp.route('/quiz/list', methods=['GET'])
def list_quizzes():
    """
    Lấy danh sách tất cả quiz
    """
    quizzes = list(Quiz.get_all())
    for q in quizzes:
        q['_id'] = str(q['_id'])
    return jsonify({'quizzes': quizzes})

@quiz_bp.route('/quiz/<quiz_id>/delete', methods=['POST'])
def delete_quiz(quiz_id):
    """
    Xóa quiz theo quiz_id (chỉ cho giảng viên)
    """
    Quiz.delete(quiz_id)
    # Xóa luôn các câu hỏi và bài nộp liên quan
    mongo = QuizQuestion.__dict__['create'].__globals__['mongo']
    mongo.db.quiz_questions.delete_many({'quiz_id': ObjectId(quiz_id)})
    mongo.db.quiz_submissions.delete_many({'quiz_id': ObjectId(quiz_id)})
    return jsonify({'message': 'Quiz deleted'})

# API cho sinh viên
@quiz_bp.route('/quiz/active', methods=['GET'])
def get_active_quizzes():
    """
    Sinh viên lấy danh sách quiz đã triển khai (status=active)
    """
    quizzes = list(Quiz.get_active())
    for q in quizzes:
        q['_id'] = str(q['_id'])
    return jsonify({'quizzes': quizzes})

@quiz_bp.route('/quiz/<quiz_id>', methods=['GET'])
def get_quiz_detail(quiz_id):
    """
    Lấy chi tiết quiz (bao gồm danh sách câu hỏi)
    """
    quiz = Quiz.find_by_id(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    quiz['_id'] = str(quiz['_id'])
    # Lấy danh sách câu hỏi
    questions = list(QuizQuestion.find_by_quiz(quiz_id))
    for q in questions:
        q['_id'] = str(q['_id'])
    quiz['questions'] = questions
    return jsonify({'quiz': quiz})

@quiz_bp.route('/quiz/<quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    """
    Sinh viên nộp bài quiz. Body: {student_id, answers}
    Tự động chấm điểm dựa trên đáp án đúng.
    """
    data = request.json
    questions = list(QuizQuestion.find_by_quiz(quiz_id))
    correct = 0
    total = len(questions)
    # answers là dict: {question_id: answer}
    for q in questions:
        qid = str(q['_id'])
        if qid in data['answers'] and data['answers'][qid] == q['correct_answer']:
            correct += 1
    score = round(correct / total * 10, 2) if total > 0 else 0
    QuizSubmission.create(
        quiz_id=quiz_id,
        student_id=data['student_id'],
        answers=data['answers'],
        score=score
    )
    return jsonify({'score': score, 'message': 'Nộp bài thành công!'})

@quiz_bp.route('/quiz/<quiz_id>/my_submission', methods=['GET'])
def get_my_submission(quiz_id):
    """
    Lấy bài nộp và điểm của sinh viên cho quiz này (truyền student_id qua query param)
    """
    student_id = request.args.get('student_id')
    submissions = list(QuizSubmission.find_by_quiz(quiz_id))
    for s in submissions:
        if s['student_id'] == student_id:
            s['_id'] = str(s['_id'])
            return jsonify({'submission': s})
    return jsonify({'submission': None})

@quiz_bp.route('/quiz/my-submissions', methods=['GET'])
def get_my_all_submissions():
    """
    Lấy tất cả bài nộp của sinh viên (truyền student_id qua query param)
    """
    student_id = request.args.get('student_id')
    if not student_id:
        return jsonify({'submissions': []})
    
    submissions = list(QuizSubmission.find_by_student(student_id))
    for s in submissions:
        s['_id'] = str(s['_id'])
        s['quiz_id'] = str(s['quiz_id'])
    
    return jsonify({'submissions': submissions})

@quiz_bp.route('/quiz/submission/<submission_id>/details', methods=['GET'])
@login_required
@role_required('lecture')
def get_submission_details(submission_id):
    """
    Lấy chi tiết bài nộp của sinh viên
    """
    submission = QuizSubmission.find_by_id(submission_id)
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404
    
    submission['_id'] = str(submission['_id'])
    submission['student_id'] = str(submission['student_id'])
    
    return jsonify({'submission': submission}) 