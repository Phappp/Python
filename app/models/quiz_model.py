from app.extensions import mongo
from bson.objectid import ObjectId
from datetime import datetime

class Quiz:
    @staticmethod
    def create(title, content, difficulty, created_by, questions, status='pending'):
        quiz_data = {
            'title': title,
            'content': content,  # Nội dung bài học để sinh câu hỏi
            'difficulty': difficulty,  # 'easy', 'medium', 'hard'
            'created_by': created_by,
            'questions': questions,  # Danh sách ObjectId của câu hỏi
            'status': status,  # 'pending', 'active'
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        return mongo.db.quizzes.insert_one(quiz_data)

    @staticmethod
    def get_all():
        return mongo.db.quizzes.find().sort('created_at', -1)

    @staticmethod
    def find_by_id(quiz_id):
        try:
            return mongo.db.quizzes.find_one({'_id': ObjectId(quiz_id)})
        except Exception:
            return None

    @staticmethod
    def update(quiz_id, data):
        data['updated_at'] = datetime.utcnow()
        return mongo.db.quizzes.update_one({'_id': ObjectId(quiz_id)}, {'$set': data})

    @staticmethod
    def set_status(quiz_id, status):
        return Quiz.update(quiz_id, {'status': status})

    @staticmethod
    def find_by_creator(username):
        return mongo.db.quizzes.find({'created_by': username}).sort('created_at', -1)

    @staticmethod
    def get_active():
        return mongo.db.quizzes.find({'status': 'active'}).sort('created_at', -1)

    @staticmethod
    def delete(quiz_id):
        return mongo.db.quizzes.delete_one({'_id': ObjectId(quiz_id)})

class QuizQuestion:
    @staticmethod
    def create(quiz_id, question_text, options, correct_answer, explanation=None):
        question_data = {
            'quiz_id': ObjectId(quiz_id),
            'question_text': question_text,
            'options': options,  # List các đáp án
            'correct_answer': correct_answer,  # Đáp án đúng
            'explanation': explanation,  # Giải thích (nếu có)
            'created_at': datetime.utcnow()
        }
        return mongo.db.quiz_questions.insert_one(question_data)

    @staticmethod
    def find_by_quiz(quiz_id):
        return mongo.db.quiz_questions.find({'quiz_id': ObjectId(quiz_id)})

class QuizSubmission:
    @staticmethod
    def create(quiz_id, student_id, answers, score=None):
        submission_data = {
            'quiz_id': ObjectId(quiz_id),
            'student_id': student_id,
            'answers': answers,  # Dict các đáp án sinh viên chọn
            'score': score,  # Điểm tự động chấm
            'submitted_at': datetime.utcnow()
        }
        return mongo.db.quiz_submissions.insert_one(submission_data)

    @staticmethod
    def find_by_quiz(quiz_id):
        return mongo.db.quiz_submissions.find({'quiz_id': ObjectId(quiz_id)}).sort('submitted_at', -1)

    @staticmethod
    def find_by_student(student_id):
        return mongo.db.quiz_submissions.find({'student_id': student_id}).sort('submitted_at', -1)

    @staticmethod
    def find_by_id(submission_id):
        try:
            return mongo.db.quiz_submissions.find_one({'_id': ObjectId(submission_id)})
        except Exception:
            return None

    @staticmethod
    def get_score_statistics(quiz_id):
        pipeline = [
            {'$match': {'quiz_id': ObjectId(quiz_id)}},
            {'$group': {
                '_id': None,
                'total_submissions': {'$sum': 1},
                'avg_score': {'$avg': '$score'},
                'max_score': {'$max': '$score'},
                'min_score': {'$min': '$score'}
            }}
        ]
        result = list(mongo.db.quiz_submissions.aggregate(pipeline))
        return result[0] if result else None 