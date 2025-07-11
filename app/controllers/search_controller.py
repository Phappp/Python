from flask import Blueprint, request, jsonify
from app.models.course_model import Course
from app.models.exercise_model import Exercise
from app.models.user_model import User

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('q', '').lower() if request.args.get('q') else ''
    category = request.args.get('type')  # lecture, exercise, user
    created_by = request.args.get('created_by')
    difficulty = request.args.get('difficulty')
    level = request.args.get('level')
    results = []

    # Tìm kiếm bài giảng
    if category == 'lecture':
        query = {'name': {'$regex': keyword, '$options': 'i'}}
        if created_by:
            query['created_by'] = created_by
        if level:
            query['level'] = level
        courses = Course.get_all()
        for course in courses:
            if keyword in course.get('name', '').lower() or keyword in course.get('description', '').lower():
                if (not created_by or course.get('created_by') == created_by) and (not level or course.get('level') == level):
                    results.append({
                        'type': 'lecture',
                        'id': str(course.get('_id')),
                        'name': course.get('name'),
                        'description': course.get('description'),
                        'created_by': course.get('created_by')
                    })
    # Tìm kiếm bài tập
    elif category == 'exercise':
        exercises = Exercise.get_all()
        for ex in exercises:
            if keyword in ex.get('title', '').lower() or keyword in ex.get('description', '').lower():
                if (not created_by or ex.get('created_by') == created_by) and (not difficulty or ex.get('difficulty', '') == difficulty):
                    results.append({
                        'type': 'exercise',
                        'id': str(ex.get('_id')),
                        'title': ex.get('title'),
                        'description': ex.get('description'),
                        'created_by': ex.get('created_by')
                    })
    # Tìm kiếm người dùng
    elif category == 'user':
        users = User.get_all()
        for user in users:
            if keyword in user.get('username', '').lower() or keyword in user.get('full_name', '').lower():
                results.append({
                    'type': 'user',
                    'id': str(user.get('_id')),
                    'username': user.get('username'),
                    'full_name': user.get('full_name'),
                    'role': user.get('role')
                })
    # Tìm tất cả
    else:
        # Bài giảng
        courses = Course.get_all()
        for course in courses:
            if keyword in course.get('name', '').lower() or keyword in course.get('description', '').lower():
                results.append({
                    'type': 'lecture',
                    'id': str(course.get('_id')),
                    'name': course.get('name'),
                    'description': course.get('description'),
                    'created_by': course.get('created_by')
                })
        # Bài tập
        exercises = Exercise.get_all()
        for ex in exercises:
            if keyword in ex.get('title', '').lower() or keyword in ex.get('description', '').lower():
                results.append({
                    'type': 'exercise',
                    'id': str(ex.get('_id')),
                    'title': ex.get('title'),
                    'description': ex.get('description'),
                    'created_by': ex.get('created_by')
                })
        # Người dùng
        users = User.get_all()
        for user in users:
            if keyword in user.get('username', '').lower() or keyword in user.get('full_name', '').lower():
                results.append({
                    'type': 'user',
                    'id': str(user.get('_id')),
                    'username': user.get('username'),
                    'full_name': user.get('full_name'),
                    'role': user.get('role')
                })
    return jsonify(results) 