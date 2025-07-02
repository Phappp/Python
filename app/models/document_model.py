from app.extensions import mongo
from bson.objectid import ObjectId
from datetime import datetime
import os

class Document:
    @staticmethod
    def create(title, description, file_path, file_name, file_size, file_type, uploaded_by, is_visible=True):
        """
        Tạo một tài liệu mới
        """
        document_data = {
            'title': title,
            'description': description,
            'file_path': file_path,
            'file_name': file_name,
            'file_size': file_size,
            'file_type': file_type,
            'uploaded_by': uploaded_by,
            'is_visible': is_visible,
            'download_count': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        return mongo.db.documents.insert_one(document_data)

    @staticmethod
    def get_all():
        """
        Lấy tất cả tài liệu
        """
        return mongo.db.documents.find().sort('created_at', -1)

    @staticmethod
    def get_visible():
        """
        Lấy các tài liệu đang hiển thị cho sinh viên
        """
        return mongo.db.documents.find({'is_visible': True}).sort('created_at', -1)

    @staticmethod
    def find_by_id(document_id):
        """
        Tìm tài liệu theo ID
        """
        try:
            return mongo.db.documents.find_one({'_id': ObjectId(document_id)})
        except Exception:
            return None

    @staticmethod
    def find_by_uploader(username):
        """
        Tìm tài liệu theo người upload
        """
        return mongo.db.documents.find({'uploaded_by': username}).sort('created_at', -1)

    @staticmethod
    def update(document_id, data):
        """
        Cập nhật tài liệu
        """
        data['updated_at'] = datetime.utcnow()
        return mongo.db.documents.update_one(
            {'_id': ObjectId(document_id)},
            {'$set': data}
        )

    @staticmethod
    def delete(document_id):
        """
        Xóa tài liệu
        """
        # Lấy thông tin file trước khi xóa
        document = Document.find_by_id(document_id)
        if document:
            # Xóa file vật lý
            file_path = document.get('file_path')
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file: {e}")
        
        return mongo.db.documents.delete_one({'_id': ObjectId(document_id)})

    @staticmethod
    def toggle_visibility(document_id):
        """
        Bật/tắt hiển thị tài liệu
        """
        document = Document.find_by_id(document_id)
        if document:
            new_status = not document.get('is_visible', True)
            return Document.update(document_id, {'is_visible': new_status})
        return None

    @staticmethod
    def increment_download_count(document_id):
        """
        Tăng số lượt tải xuống
        """
        return mongo.db.documents.update_one(
            {'_id': ObjectId(document_id)},
            {'$inc': {'download_count': 1}}
        )

    @staticmethod
    def search_documents(query, user_role='student'):
        """
        Tìm kiếm tài liệu
        """
        if user_role == 'student':
            # Sinh viên chỉ thấy tài liệu visible
            filter_query = {
                'is_visible': True,
                '$or': [
                    {'title': {'$regex': query, '$options': 'i'}},
                    {'description': {'$regex': query, '$options': 'i'}}
                ]
            }
        else:
            # Giảng viên thấy tất cả tài liệu
            filter_query = {
                '$or': [
                    {'title': {'$regex': query, '$options': 'i'}},
                    {'description': {'$regex': query, '$options': 'i'}}
                ]
            }
        
        return mongo.db.documents.find(filter_query).sort('created_at', -1)

    @staticmethod
    def get_statistics():
        """
        Lấy thống kê tài liệu
        """
        pipeline = [
            {'$group': {
                '_id': None,
                'total_documents': {'$sum': 1},
                'total_downloads': {'$sum': '$download_count'},
                'visible_documents': {'$sum': {'$cond': ['$is_visible', 1, 0]}},
                'hidden_documents': {'$sum': {'$cond': ['$is_visible', 0, 1]}}
            }}
        ]
        result = list(mongo.db.documents.aggregate(pipeline))
        return result[0] if result else {
            'total_documents': 0,
            'total_downloads': 0,
            'visible_documents': 0,
            'hidden_documents': 0
        }

    @staticmethod
    def get_popular_documents(limit=10):
        """
        Lấy tài liệu được tải nhiều nhất
        """
        return mongo.db.documents.find({'is_visible': True}).sort('download_count', -1).limit(limit)

    @staticmethod
    def get_recent_documents(limit=10):
        """
        Lấy tài liệu mới nhất
        """
        return mongo.db.documents.find({'is_visible': True}).sort('created_at', -1).limit(limit) 