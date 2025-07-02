import os
import uuid
from datetime import datetime
from flask import request, flash, redirect, url_for, send_file, current_app
from werkzeug.utils import secure_filename
from app.models.document_model import Document
from app.models.user_model import User
from config import Config

class DocumentController:
    ALLOWED_EXTENSIONS = Config.ALLOWED_DOCUMENT_EXTENSIONS
    MAX_FILE_SIZE = Config.MAX_CONTENT_LENGTH

    @staticmethod
    def allowed_file(filename):
        """Kiểm tra file có được phép upload không"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in DocumentController.ALLOWED_EXTENSIONS

    @staticmethod
    def get_file_size_mb(file_size_bytes):
        """Chuyển đổi kích thước file từ bytes sang MB"""
        return round(file_size_bytes / (1024 * 1024), 2)

    @staticmethod
    def upload_document():
        """Upload tài liệu mới"""
        try:
            if 'document_file' not in request.files:
                flash('Không có file được chọn!', 'error')
                return False, 'Không có file được chọn'

            file = request.files['document_file']
            if file.filename == '':
                flash('Không có file được chọn!', 'error')
                return False, 'Không có file được chọn'

            if not DocumentController.allowed_file(file.filename):
                flash('Định dạng file không được hỗ trợ!', 'error')
                return False, 'Định dạng file không được hỗ trợ'

            # Kiểm tra kích thước file
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > DocumentController.MAX_FILE_SIZE:
                flash('File quá lớn! Kích thước tối đa là 50MB', 'error')
                return False, 'File quá lớn'

            # Lấy thông tin từ form
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            is_visible = request.form.get('is_visible') == 'on'
            uploaded_by = request.form.get('uploaded_by')

            if not title:
                flash('Tiêu đề không được để trống!', 'error')
                return False, 'Tiêu đề không được để trống'

            # Tạo tên file an toàn
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            
            # Tạo tên file unique
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Tạo thư mục uploads/documents nếu chưa có
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Lưu file
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)

            # Lưu thông tin vào database
            document_data = {
                'title': title,
                'description': description,
                'file_path': file_path,
                'file_name': filename,
                'file_size': file_size,
                'file_type': file_extension,
                'uploaded_by': uploaded_by,
                'is_visible': is_visible
            }

            result = Document.create(**document_data)
            
            if result.inserted_id:
                flash('Tài liệu đã được tải lên thành công!', 'success')
                return True, 'Tài liệu đã được tải lên thành công'
            else:
                flash('Có lỗi xảy ra khi tải lên tài liệu!', 'error')
                return False, 'Có lỗi xảy ra khi tải lên tài liệu'

        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
            return False, str(e)

    @staticmethod
    def update_document(document_id):
        """Cập nhật thông tin tài liệu"""
        try:
            document = Document.find_by_id(document_id)
            if not document:
                flash('Tài liệu không tồn tại!', 'error')
                return False, 'Tài liệu không tồn tại'

            # Lấy thông tin từ form
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            is_visible = request.form.get('is_visible') == 'on'

            if not title:
                flash('Tiêu đề không được để trống!', 'error')
                return False, 'Tiêu đề không được để trống'

            # Cập nhật thông tin cơ bản
            update_data = {
                'title': title,
                'description': description,
                'is_visible': is_visible
            }

            # Kiểm tra có upload file mới không
            if 'document_file' in request.files:
                file = request.files['document_file']
                if file.filename != '':
                    if not DocumentController.allowed_file(file.filename):
                        flash('Định dạng file không được hỗ trợ!', 'error')
                        return False, 'Định dạng file không được hỗ trợ'

                    # Kiểm tra kích thước file
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    
                    if file_size > DocumentController.MAX_FILE_SIZE:
                        flash('File quá lớn! Kích thước tối đa là 50MB', 'error')
                        return False, 'File quá lớn'

                    # Xóa file cũ
                    old_file_path = document.get('file_path')
                    if old_file_path and os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                        except Exception as e:
                            print(f"Error deleting old file: {e}")

                    # Lưu file mới
                    filename = secure_filename(file.filename)
                    file_extension = filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    
                    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    file_path = os.path.join(upload_folder, unique_filename)
                    file.save(file_path)

                    # Cập nhật thông tin file
                    update_data.update({
                        'file_path': file_path,
                        'file_name': filename,
                        'file_size': file_size,
                        'file_type': file_extension
                    })

            result = Document.update(document_id, update_data)
            
            if result.modified_count > 0:
                flash('Tài liệu đã được cập nhật thành công!', 'success')
                return True, 'Tài liệu đã được cập nhật thành công'
            else:
                flash('Không có thay đổi nào được lưu!', 'info')
                return True, 'Không có thay đổi nào được lưu'

        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
            return False, str(e)

    @staticmethod
    def delete_document(document_id):
        """Xóa tài liệu"""
        try:
            document = Document.find_by_id(document_id)
            if not document:
                flash('Tài liệu không tồn tại!', 'error')
                return False, 'Tài liệu không tồn tại'

            result = Document.delete(document_id)
            
            if result.deleted_count > 0:
                flash('Tài liệu đã được xóa thành công!', 'success')
                return True, 'Tài liệu đã được xóa thành công'
            else:
                flash('Có lỗi xảy ra khi xóa tài liệu!', 'error')
                return False, 'Có lỗi xảy ra khi xóa tài liệu'

        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
            return False, str(e)

    @staticmethod
    def download_document(document_id):
        """Tải xuống tài liệu"""
        try:
            document = Document.find_by_id(document_id)
            if not document:
                flash('Tài liệu không tồn tại!', 'error')
                return None

            file_path = document.get('file_path')
            if not file_path or not os.path.exists(file_path):
                flash('File không tồn tại!', 'error')
                return None

            # Tăng số lượt tải xuống
            Document.increment_download_count(document_id)

            # Trả về file để download
            return send_file(
                file_path,
                as_attachment=True,
                download_name=document.get('file_name', 'document')
            )

        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
            return None

    @staticmethod
    def toggle_document_visibility(document_id):
        """Bật/tắt hiển thị tài liệu"""
        try:
            document = Document.find_by_id(document_id)
            if not document:
                flash('Tài liệu không tồn tại!', 'error')
                return False, 'Tài liệu không tồn tại'

            result = Document.toggle_visibility(document_id)
            
            if result.modified_count > 0:
                new_status = not document.get('is_visible', True)
                status_text = 'hiển thị' if new_status else 'ẩn'
                flash(f'Tài liệu đã được {status_text}!', 'success')
                return True, f'Tài liệu đã được {status_text}'
            else:
                flash('Có lỗi xảy ra!', 'error')
                return False, 'Có lỗi xảy ra'

        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
            return False, str(e)

    @staticmethod
    def search_documents(query, user_role='student'):
        """Tìm kiếm tài liệu"""
        try:
            if not query.strip():
                return Document.get_visible() if user_role == 'student' else Document.get_all()
            
            return Document.search_documents(query.strip(), user_role)
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    @staticmethod
    def get_document_statistics():
        """Lấy thống kê tài liệu"""
        try:
            return Document.get_statistics()
        except Exception as e:
            print(f"Error getting document statistics: {e}")
            return {
                'total_documents': 0,
                'total_downloads': 0,
                'visible_documents': 0,
                'hidden_documents': 0
            } 