from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.controllers.document_controller import DocumentController
from app.models.document_model import Document
from app.models.user_model import User
from app.utils.decorators import login_required, role_required, custom_permission_required
from bson.objectid import ObjectId

document_bp = Blueprint('document', __name__)

# Routes cho giảng viên
@document_bp.route('/manage-documents')
@login_required
@role_required('lecture')
def manage_documents():
    """Trang quản lý tài liệu cho giảng viên"""
    try:
        # Lấy danh sách tài liệu của giảng viên
        documents = Document.find_by_uploader(session['username'])
        documents = list(documents)
        
        # Lấy thống kê
        stats = Document.get_statistics()
        
        return render_template('documents/manage_documents.html', 
                             documents=documents, 
                             stats=stats)
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('main.home'))

@document_bp.route('/upload-document', methods=['GET', 'POST'])
@login_required
@role_required('lecture')
def upload_document():
    """Trang upload tài liệu mới"""
    if request.method == 'POST':
        # Thêm thông tin người upload
        request.form = request.form.copy()
        request.form['uploaded_by'] = session['username']
        
        success, message = DocumentController.upload_document()
        if success:
            return redirect(url_for('document.manage_documents'))
        else:
            flash(message, 'error')
    
    return render_template('documents/upload_document.html')

@document_bp.route('/edit-document/<document_id>', methods=['GET', 'POST'])
@login_required
@role_required('lecture')
def edit_document(document_id):
    """Trang chỉnh sửa tài liệu"""
    try:
        document = Document.find_by_id(document_id)
        if not document:
            flash('Tài liệu không tồn tại!', 'error')
            return redirect(url_for('document.manage_documents'))
        
        # Kiểm tra quyền sở hữu
        if document.get('uploaded_by') != session['username']:
            flash('Bạn không có quyền chỉnh sửa tài liệu này!', 'error')
            return redirect(url_for('document.manage_documents'))
        
        if request.method == 'POST':
            success, message = DocumentController.update_document(document_id)
            if success:
                return redirect(url_for('document.manage_documents'))
            else:
                flash(message, 'error')
        
        return render_template('documents/edit_document.html', document=document)
    
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('document.manage_documents'))

@document_bp.route('/delete-document/<document_id>', methods=['POST'])
@login_required
@role_required('lecture')
def delete_document(document_id):
    """Xóa tài liệu"""
    try:
        document = Document.find_by_id(document_id)
        if not document:
            flash('Tài liệu không tồn tại!', 'error')
            return redirect(url_for('document.manage_documents'))
        
        # Kiểm tra quyền sở hữu
        if document.get('uploaded_by') != session['username']:
            flash('Bạn không có quyền xóa tài liệu này!', 'error')
            return redirect(url_for('document.manage_documents'))
        
        success, message = DocumentController.delete_document(document_id)
        if not success:
            flash(message, 'error')
        
        return redirect(url_for('document.manage_documents'))
    
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('document.manage_documents'))

@document_bp.route('/toggle-document-visibility/<document_id>', methods=['POST'])
@login_required
@role_required('lecture')
def toggle_document_visibility(document_id):
    """Bật/tắt hiển thị tài liệu"""
    try:
        document = Document.find_by_id(document_id)
        if not document:
            flash('Tài liệu không tồn tại!', 'error')
            return redirect(url_for('document.manage_documents'))
        
        # Kiểm tra quyền sở hữu
        if document.get('uploaded_by') != session['username']:
            flash('Bạn không có quyền thay đổi tài liệu này!', 'error')
            return redirect(url_for('document.manage_documents'))
        
        success, message = DocumentController.toggle_document_visibility(document_id)
        if not success:
            flash(message, 'error')
        
        return redirect(url_for('document.manage_documents'))
    
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('document.manage_documents'))

# Routes cho sinh viên
@document_bp.route('/view-documents')
@login_required
def view_documents():
    """Trang xem tài liệu cho sinh viên"""
    try:
        # Lấy query tìm kiếm
        search_query = request.args.get('search', '').strip()
        
        # Lấy danh sách tài liệu visible
        if search_query:
            documents = DocumentController.search_documents(search_query, 'student')
        else:
            documents = Document.get_visible()
        
        documents = list(documents)
        
        # Lấy thống kê
        stats = Document.get_statistics()
        
        # Lấy tài liệu phổ biến
        popular_documents = list(Document.get_popular_documents(5))
        
        # Lấy tài liệu mới nhất
        recent_documents = list(Document.get_recent_documents(5))
        
        return render_template('documents/view_documents.html', 
                             documents=documents, 
                             stats=stats,
                             popular_documents=popular_documents,
                             recent_documents=recent_documents,
                             search_query=search_query)
    
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('main.home'))

@document_bp.route('/download-document/<document_id>')
@login_required
def download_document(document_id):
    """Tải xuống tài liệu"""
    try:
        document = Document.find_by_id(document_id)
        if not document:
            flash('Tài liệu không tồn tại!', 'error')
            return redirect(url_for('document.view_documents'))
        
        # Kiểm tra tài liệu có visible không (cho sinh viên)
        if session.get('role') == 'student' and not document.get('is_visible', True):
            flash('Tài liệu không khả dụng!', 'error')
            return redirect(url_for('document.view_documents'))
        
        return DocumentController.download_document(document_id)
    
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('document.view_documents'))

@document_bp.route('/document-details/<document_id>')
@login_required
def document_details(document_id):
    """Trang chi tiết tài liệu"""
    try:
        document = Document.find_by_id(document_id)
        if not document:
            flash('Tài liệu không tồn tại!', 'error')
            return redirect(url_for('document.view_documents'))
        
        # Kiểm tra quyền xem (sinh viên chỉ thấy tài liệu visible)
        if session.get('role') == 'student' and not document.get('is_visible', True):
            flash('Tài liệu không khả dụng!', 'error')
            return redirect(url_for('document.view_documents'))
        
        # Lấy thông tin người upload
        uploader = User.find_by_username(document.get('uploaded_by'))
        
        return render_template('documents/document_details.html', 
                             document=document, 
                             uploader=uploader)
    
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('document.view_documents'))

# API Routes
@document_bp.route('/api/search-documents')
@login_required
def api_search_documents():
    """API tìm kiếm tài liệu"""
    try:
        query = request.args.get('q', '').strip()
        user_role = session.get('role', 'student')
        
        if not query:
            return jsonify({'documents': []})
        
        documents = DocumentController.search_documents(query, user_role)
        documents = list(documents)
        
        # Chuyển đổi ObjectId thành string
        for doc in documents:
            doc['_id'] = str(doc['_id'])
            doc['created_at'] = doc['created_at'].isoformat() if doc.get('created_at') else None
            doc['updated_at'] = doc['updated_at'].isoformat() if doc.get('updated_at') else None
        
        return jsonify({'documents': documents})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/api/document-statistics')
@login_required
def api_document_statistics():
    """API lấy thống kê tài liệu"""
    try:
        stats = DocumentController.get_document_statistics()
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 