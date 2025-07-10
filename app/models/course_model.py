from app.extensions import mongo
from bson.objectid import ObjectId

class Course:
    @staticmethod
    def create(name, description, original_price, discounted_price, created_by, color, icon_class):
        """
        Tạo một khóa học mới và lưu vào cơ sở dữ liệu.
        """
        return mongo.db.courses.insert_one({
            'name': name,
            'description': description,
            'original_price': original_price,
            'discounted_price': discounted_price,
            'created_by': created_by,
            'color': color,
            'icon_class': icon_class,
            'chapters': []  # Khởi tạo mảng chapters rỗng
        })

    @staticmethod
    def get_all():
        """
        Lấy tất cả các khóa học từ cơ sở dữ liệu.
        """
        return mongo.db.courses.find()

    @staticmethod
    def find_by_id(course_id):
        """
        Tìm một khóa học bằng ID của nó.
        """
        try:
            return mongo.db.courses.find_one({'_id': ObjectId(course_id)})
        except Exception:
            return None

    @staticmethod
    def find_by_creator(username):
        """
        Tìm các khóa học được tạo bởi một giảng viên cụ thể.
        """
        return mongo.db.courses.find({'created_by': username})

    @staticmethod
    def update(course_id, data):
        """
        Cập nhật thông tin của một khóa học.
        """
        return mongo.db.courses.update_one(
            {'_id': ObjectId(course_id)},
            {'$set': data}
        )

    @staticmethod
    def delete(course_id):
        """
        Xóa một khóa học.
        """
        return mongo.db.courses.delete_one({'_id': ObjectId(course_id)})

    @staticmethod
    def add_chapter(course_id, title, video_url):
        """
        Thêm một chương mới vào khóa học.
        """
        chapter_data = {
            '_id': ObjectId(),
            'title': title,
            'video_url': video_url
        }
        return mongo.db.courses.update_one(
            {'_id': ObjectId(course_id)},
            {'$push': {'chapters': chapter_data}}
        )

    @staticmethod
    def find_chapter(course_id, chapter_id):
        """
        Tìm một chương cụ thể trong một khóa học.
        """
        return mongo.db.courses.find_one(
            {'_id': ObjectId(course_id), 'chapters._id': ObjectId(chapter_id)},
            {'chapters.$': 1}
        )
        
    @staticmethod
    def update_chapter(course_id, chapter_id, title, video_url):
        """
        Cập nhật thông tin của một chương.
        """
        return mongo.db.courses.update_one(
            {'_id': ObjectId(course_id), 'chapters._id': ObjectId(chapter_id)},
            {'$set': {
                'chapters.$.title': title,
                'chapters.$.video_url': video_url
            }}
        )
        
    @staticmethod
    def delete_chapter(course_id, chapter_id):
        """
        Xóa một chương khỏi khóa học.
        """
        return mongo.db.courses.update_one(
            {'_id': ObjectId(course_id)},
            {'$pull': {'chapters': {'_id': ObjectId(chapter_id)}}}
        ) 

class CourseReview:
    @staticmethod
    def add_review(course_id, username, rating, comment):
        from datetime import datetime
        from app.extensions import mongo
        return mongo.db.course_reviews.insert_one({
            'course_id': str(course_id),
            'username': username,
            'rating': int(rating),
            'comment': comment,
            'created_at': datetime.utcnow()
        })

    @staticmethod
    def get_reviews_by_course(course_id):
        from app.extensions import mongo
        return list(mongo.db.course_reviews.find({'course_id': str(course_id)}).sort('created_at', -1)) 