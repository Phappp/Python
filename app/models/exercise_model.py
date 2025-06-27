from app.extensions import mongo
from bson.objectid import ObjectId
from datetime import datetime
import json

class Exercise:
    @staticmethod
    def create(title, description, language_supported, test_cases, created_by, is_visible=True, time_limit=None, memory_limit=None):
        """
        Tạo một bài tập lập trình mới
        """
        exercise_data = {
            'title': title,
            'description': description,
            'language_supported': language_supported,
            'test_cases': test_cases,
            'created_by': created_by,
            'is_visible': is_visible,
            'time_limit': time_limit,
            'memory_limit': memory_limit,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        return mongo.db.exercises.insert_one(exercise_data)

    @staticmethod
    def get_all():
        """
        Lấy tất cả bài tập
        """
        return mongo.db.exercises.find().sort('created_at', -1)

    @staticmethod
    def get_visible():
        """
        Lấy các bài tập đang hiển thị cho sinh viên
        """
        return mongo.db.exercises.find({'is_visible': True}).sort('created_at', -1)

    @staticmethod
    def find_by_id(exercise_id):
        """
        Tìm bài tập theo ID
        """
        try:
            return mongo.db.exercises.find_one({'_id': ObjectId(exercise_id)})
        except Exception:
            return None

    @staticmethod
    def find_by_creator(username):
        """
        Tìm bài tập theo người tạo
        """
        return mongo.db.exercises.find({'created_by': username}).sort('created_at', -1)

    @staticmethod
    def update(exercise_id, data):
        """
        Cập nhật bài tập
        """
        data['updated_at'] = datetime.utcnow()
        return mongo.db.exercises.update_one(
            {'_id': ObjectId(exercise_id)},
            {'$set': data}
        )

    @staticmethod
    def delete(exercise_id):
        """
        Xóa bài tập
        """
        return mongo.db.exercises.delete_one({'_id': ObjectId(exercise_id)})

    @staticmethod
    def toggle_visibility(exercise_id):
        """
        Bật/tắt hiển thị bài tập
        """
        exercise = Exercise.find_by_id(exercise_id)
        if exercise:
            new_status = not exercise.get('is_visible', True)
            return Exercise.update(exercise_id, {'is_visible': new_status})
        return None

class Submission:
    @staticmethod
    def create(exercise_id, user_id, code, language):
        """
        Tạo một lượt nộp bài
        """
        submission_data = {
            'exercise_id': ObjectId(exercise_id),
            'user_id': user_id,
            'code': code,
            'language': language,
            'submitted_at': datetime.utcnow(),
            'score': None,
            'llm_feedback': None,
            'test_results': [],
            'execution_time': None,
            'memory_used': None
        }
        return mongo.db.submissions.insert_one(submission_data)

    @staticmethod
    def find_by_id(submission_id):
        """
        Tìm submission theo ID
        """
        try:
            return mongo.db.submissions.find_one({'_id': ObjectId(submission_id)})
        except Exception:
            return None

    @staticmethod
    def find_by_exercise(exercise_id):
        """
        Tìm tất cả submission của một bài tập
        """
        return mongo.db.submissions.find({'exercise_id': ObjectId(exercise_id)}).sort('submitted_at', -1)

    @staticmethod
    def find_by_user(user_id):
        """
        Tìm tất cả submission của một user
        """
        return mongo.db.submissions.find({'user_id': user_id}).sort('submitted_at', -1)

    @staticmethod
    def update_score(submission_id, score, llm_feedback=None, test_results=None):
        """
        Cập nhật điểm và phản hồi AI
        """
        update_data = {
            'score': score,
            'updated_at': datetime.utcnow()
        }
        if llm_feedback:
            update_data['llm_feedback'] = llm_feedback
        if test_results:
            update_data['test_results'] = test_results
        
        return mongo.db.submissions.update_one(
            {'_id': ObjectId(submission_id)},
            {'$set': update_data}
        )

    @staticmethod
    def get_statistics(exercise_id):
        """
        Lấy thống kê của bài tập
        """
        pipeline = [
            {'$match': {'exercise_id': ObjectId(exercise_id)}},
            {'$group': {
                '_id': None,
                'total_submissions': {'$sum': 1},
                'avg_score': {'$avg': '$score'},
                'max_score': {'$max': '$score'},
                'min_score': {'$min': '$score'}
            }}
        ]
        result = list(mongo.db.submissions.aggregate(pipeline))
        return result[0] if result else None

    @staticmethod
    def get_best_score(exercise_id, user_id):
        """
        Lấy điểm cao nhất của sinh viên cho một bài tập
        """
        best = mongo.db.submissions.find({
            'exercise_id': ObjectId(exercise_id),
            'user_id': user_id,
            'score': { '$ne': None }
        }).sort('score', -1).limit(1)
        best = list(best)
        return best[0]['score'] if best else None

class TestCase:
    @staticmethod
    def create(exercise_id, input_data, expected_output, description=None, is_hidden=False):
        """
        Tạo test case cho bài tập
        """
        test_case_data = {
            'exercise_id': ObjectId(exercise_id),
            'input': input_data,
            'expected_output': expected_output,
            'description': description,
            'is_hidden': is_hidden,
            'created_at': datetime.utcnow()
        }
        return mongo.db.test_cases.insert_one(test_case_data)

    @staticmethod
    def find_by_exercise(exercise_id, include_hidden=False):
        """
        Tìm test cases của bài tập
        """
        query = {'exercise_id': ObjectId(exercise_id)}
        if not include_hidden:
            query['is_hidden'] = False
        return mongo.db.test_cases.find(query).sort('created_at', 1)

    @staticmethod
    def delete_by_exercise(exercise_id):
        """
        Xóa tất cả test cases của bài tập
        """
        return mongo.db.test_cases.delete_many({'exercise_id': ObjectId(exercise_id)}) 