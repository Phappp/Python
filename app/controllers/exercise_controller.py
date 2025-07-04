import os
from flask import Blueprint, request, redirect, url_for, render_template, flash, current_app, session
from werkzeug.utils import secure_filename
from app.extensions import mongo
from datetime import datetime
from bson.objectid import ObjectId

exercise_bp = Blueprint('exercise', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'png', 'jpg', 'jpeg', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@exercise_bp.route('/upload_exercise/<course_id>', methods=['GET', 'POST'])
def upload_exercise(course_id):
    from bson.objectid import ObjectId
    # Kiểm tra quyền: chỉ lecture mới được upload bài tập
    if session.get('role') != 'lecture':
        flash('Chỉ giảng viên mới được upload bài tập!', 'danger')
        return redirect(url_for('main.home'))
    
    course = mongo.db.courses.find_one({'_id': ObjectId(course_id)})
    if not course:
        flash('Không tìm thấy khóa học!', 'danger')
        return redirect(url_for('exercise.manage_exercises'))
    
    # Kiểm tra quyền: lecture chỉ có thể upload bài tập cho khóa học do mình tạo hoặc do admin tạo
    if course.get('created_by') != session.get('username') and session.get('role') != 'admin':
        flash('Bạn không có quyền upload bài tập cho khóa học này!', 'danger')
        return redirect(url_for('exercise.manage_exercises'))
    
    chapters = []
    for chapter in course.get('chapters', []):
        chapters.append({
            'chapter_id': str(chapter['_id']),
            'chapter_title': chapter.get('title', '')
        })
    if request.method == 'POST':
        title = request.form.get('title')
        chapter_id = request.form.get('chapter_id')
        due_date = request.form.get('due_date')
        due_time = request.form.get('due_time')
        due_datetime = None
        if due_date and due_time:
            due_datetime = f"{due_date} {due_time}"
        else:
            due_datetime = due_date or ''
        if not title or not chapter_id or not due_datetime:
            flash('Vui lòng nhập đầy đủ thông tin!')
            return render_template('exercises/upload_exercise.html', chapters=chapters)
        if 'file' not in request.files:
            flash('No file part')
            return render_template('exercises/upload_exercise.html', chapters=chapters)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return render_template('exercises/upload_exercise.html', chapters=chapters)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'exercises')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            rel_path = os.path.relpath(filepath, current_app.root_path)
            filetype = filename.rsplit('.', 1)[1].lower()
            mongo.db.exercises.insert_one({
                'title': title,
                'chapter_id': ObjectId(chapter_id),
                'filename': filename,
                'filepath': rel_path,
                'filetype': filetype,
                'due_date': due_datetime,
                'upload_date': datetime.utcnow(),
                'status': 'Chờ'
            })
            flash('Upload thành công!')
            return redirect(url_for('exercise.manage_exercises', course_id=course_id))
        else:
            flash('Định dạng file không hợp lệ!')
            return render_template('exercises/upload_exercise.html', chapters=chapters)
    return render_template('exercises/upload_exercise.html', chapters=chapters)

@exercise_bp.route('/manage_exercises', defaults={'course_id': None})
@exercise_bp.route('/manage_exercises/<course_id>')
def manage_exercises(course_id):
    from flask import session
    # Kiểm tra quyền: chỉ lecture mới được quản lý bài tập
    if session.get('role') != 'lecture':
        flash('Chỉ giảng viên mới được quản lý bài tập!', 'danger')
        return redirect(url_for('main.home'))
    
    # Nếu chưa chọn khóa học, hiển thị danh sách tất cả khóa học (bao gồm cả admin tạo)
    if not course_id:
        courses = list(mongo.db.courses.find())
        return render_template('exercises/select_course.html', courses=courses)
    
    # Nếu đã chọn khóa học, hiển thị bài tập của khóa học đó
    course = mongo.db.courses.find_one({'_id': ObjectId(course_id)})
    if not course:
        flash('Không tìm thấy khóa học!', 'danger')
        return redirect(url_for('exercise.manage_exercises'))
    
    # Kiểm tra quyền: lecture chỉ có thể quản lý bài tập của khóa học do mình tạo hoặc do admin tạo
    if course.get('created_by') != session.get('username') and session.get('role') != 'admin':
        flash('Bạn không có quyền quản lý bài tập của khóa học này!', 'danger')
        return redirect(url_for('exercise.manage_exercises'))
    
    # Lấy tất cả chương của khóa học
    chapter_ids = [chapter['_id'] for chapter in course.get('chapters', [])]
    # Lấy tất cả bài tập thuộc các chương này
    waiting = list(mongo.db.exercises.find({'status': 'Chờ', 'chapter_id': {'$in': chapter_ids}}))
    deployed = list(mongo.db.exercises.find({'status': 'Đang triển khai', 'chapter_id': {'$in': chapter_ids}}))
    # Lấy mapping chapter_id -> tên chương
    chapter_map = {str(ch['_id']): ch.get('title', '') for ch in course.get('chapters', [])}
    for ex in waiting + deployed:
        ex['chapter_name'] = chapter_map.get(str(ex['chapter_id']), str(ex['chapter_id']))
    return render_template('exercises/manage_exercises.html', waiting=waiting, deployed=deployed, course=course)

@exercise_bp.route('/deploy_exercise/<exercise_id>', methods=['POST'])
def deploy_exercise(exercise_id):
    mongo.db.exercises.update_one({'_id': ObjectId(exercise_id)}, {'$set': {'status': 'Đang triển khai'}})
    flash('Bài tập đã được triển khai!')
    return redirect(url_for('exercise.manage_exercises'))

@exercise_bp.route('/view_submissions/<exercise_id>')
def view_submissions(exercise_id):
    from bson.objectid import ObjectId
    exercise = mongo.db.exercises.find_one({'_id': ObjectId(exercise_id)})
    # Lấy course_id từ chapter chứa bài tập
    course = None
    course_id = None
    if exercise:
        chapter = None
        for c in mongo.db.courses.find():
            for ch in c.get('chapters', []):
                if ch['_id'] == exercise['chapter_id']:
                    course = c
                    chapter = ch
                    break
            if course:
                break
        if course:
            course_id = str(course['_id'])
    submissions = list(mongo.db.submissions.find({'exercise_id': ObjectId(exercise_id)}))
    return render_template('exercises/view_submissions.html', exercise=exercise, submissions=submissions, course_id=course_id)

@exercise_bp.route('/grade_submission/<submission_id>', methods=['POST'])
def grade_submission(submission_id):
    score = request.form.get('score')
    try:
        score = float(score)
        if not (0 <= score <= 10):
            raise ValueError
    except:
        flash('Điểm phải từ 0 đến 10!')
        return redirect(request.referrer)
    mongo.db.submissions.update_one({'_id': ObjectId(submission_id)}, {'$set': {'score': score}})
    flash('Chấm điểm thành công!')
    return redirect(request.referrer)

@exercise_bp.route('/courses/<course_id>/chapters/<chapter_id>/exercises', methods=['GET', 'POST'])
def student_chapter_exercises(course_id, chapter_id):
    # Chỉ cho phép sinh viên
    if session.get('role') != 'student':
        flash('Chỉ sinh viên mới được truy cập!', 'danger')
        return redirect(url_for('main.home'))
    from bson.objectid import ObjectId
    # Lấy danh sách bài tập đang triển khai của chương này
    exercises = list(mongo.db.exercises.find({
        'chapter_id': ObjectId(chapter_id),
        'status': 'Đang triển khai'
    }))
    # Lấy các bài nộp của sinh viên hiện tại
    submissions = {str(sub['exercise_id']): sub for sub in mongo.db.submissions.find({
        'student_username': session.get('username')
    })}
    if request.method == 'POST':
        exercise_id = request.form.get('exercise_id')
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('Vui lòng chọn file!', 'warning')
            return redirect(request.url)
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'submissions')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        rel_path = os.path.relpath(filepath, current_app.root_path)
        # Lưu submission
        mongo.db.submissions.insert_one({
            'exercise_id': ObjectId(exercise_id),
            'student_username': session.get('username'),
            'filename': filename,
            'filepath': rel_path,
            'submit_date': datetime.utcnow(),
            'score': None
        })
        flash('Nộp bài thành công!')
        return redirect(request.url)
    return render_template('exercises/student_chapter_exercises.html', exercises=exercises, submissions=submissions)

@exercise_bp.route('/student_assignments', defaults={'course_id': None}, methods=['GET', 'POST'])
@exercise_bp.route('/student_assignments/<course_id>', methods=['GET', 'POST'])
def student_assignments(course_id):
    if session.get('role') != 'student':
        flash('Chỉ sinh viên mới được truy cập!', 'danger')
        return redirect(url_for('main.home'))
    from bson.objectid import ObjectId
    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    # Nếu chưa chọn khóa học, hiển thị danh sách khóa học sinh viên đã tham gia
    if not course_id:
        courses = list(mongo.db.courses.find())
        return render_template('exercises/select_course_student.html', courses=courses)
    # Nếu đã chọn khóa học, hiển thị bài tập của khóa học đó
    course = mongo.db.courses.find_one({'_id': ObjectId(course_id)})
    if not course:
        flash('Không tìm thấy khóa học!', 'danger')
        return redirect(url_for('exercise.student_assignments'))
    chapter_ids = [chapter['_id'] for chapter in course.get('chapters', [])]
    exercises = list(mongo.db.exercises.find({'status': 'Đang triển khai', 'chapter_id': {'$in': chapter_ids}}))
    submissions = {str(sub['exercise_id']): sub for sub in mongo.db.submissions.find({
        'student_username': session.get('username')
    })}
    if request.method == 'POST':
        exercise_id = request.form.get('exercise_id')
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('Vui lòng chọn file!', 'warning')
            return redirect(request.url)
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'submissions')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        rel_path = os.path.relpath(filepath, current_app.root_path)
        mongo.db.submissions.insert_one({
            'exercise_id': ObjectId(exercise_id),
            'student_username': session.get('username'),
            'filename': filename,
            'filepath': rel_path,
            'submit_date': datetime.utcnow(),
            'score': None
        })
        flash('Nộp bài thành công!')
        return redirect(request.url)
    return render_template('exercises/student_assignments.html', exercises=exercises, submissions=submissions, course=course, now=now)

@exercise_bp.route('/delete_exercise/<exercise_id>', methods=['POST'])
def delete_exercise(exercise_id):
    from bson.objectid import ObjectId
    mongo.db.exercises.delete_one({'_id': ObjectId(exercise_id)})
    flash('Đã xóa bài tập!')
    return redirect(url_for('exercise.manage_exercises'))

@exercise_bp.route('/edit_exercise/<exercise_id>', methods=['GET', 'POST'])
def edit_exercise(exercise_id):
    from bson.objectid import ObjectId
    exercise = mongo.db.exercises.find_one({'_id': ObjectId(exercise_id)})
    # Lấy danh sách chương
    courses = list(mongo.db.courses.find())
    chapters = []
    for course in courses:
        for chapter in course.get('chapters', []):
            chapters.append({
                'course_id': str(course['_id']),
                'chapter_id': str(chapter['_id']),
                'course_name': course.get('name', ''),
                'chapter_title': chapter.get('title', '')
            })
    if request.method == 'POST':
        title = request.form.get('title')
        chapter_id = request.form.get('chapter_id')
        due_date = request.form.get('due_date')
        due_time = request.form.get('due_time')
        due_datetime = None
        if due_date and due_time:
            due_datetime = f"{due_date} {due_time}"
        else:
            due_datetime = due_date or ''
        mongo.db.exercises.update_one({'_id': ObjectId(exercise_id)}, {'$set': {
            'title': title,
            'chapter_id': ObjectId(chapter_id),
            'due_date': due_datetime
        }})
        flash('Đã cập nhật bài tập!')
        return redirect(url_for('exercise.manage_exercises'))
    # Tách ngày và giờ cho form
    due_date = ''
    due_time = ''
    if exercise and exercise.get('due_date'):
        parts = exercise['due_date'].split()
        if len(parts) == 2:
            due_date, due_time = parts
        elif len(parts) == 1:
            due_date = parts[0]
    return render_template('exercises/edit_exercise.html', exercise=exercise, chapters=chapters, due_date=due_date, due_time=due_time) 