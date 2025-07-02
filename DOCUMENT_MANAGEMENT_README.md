# Hướng dẫn sử dụng chức năng Quản lý Tài liệu

## Tổng quan
Chức năng Quản lý Tài liệu cho phép giảng viên upload, quản lý và chia sẻ tài liệu học tập với sinh viên. Sinh viên có thể xem và tải xuống các tài liệu được chia sẻ.

## Tính năng chính

### Cho Giảng viên (Role: 'lecture')

#### 1. Quản lý tài liệu
- **Xem danh sách**: Tất cả tài liệu đã upload
- **Thống kê**: Số lượng tài liệu, lượt tải xuống, trạng thái hiển thị
- **Bộ lọc**: Theo trạng thái, ngày tạo, loại file

#### 2. Upload tài liệu mới
- **Tiêu đề**: Tên tài liệu (bắt buộc)
- **Mô tả**: Thông tin chi tiết về nội dung
- **File**: Hỗ trợ PDF, DOCX, DOC, TXT, PPT, PPTX, XLS, XLSX
- **Kích thước**: Tối đa 50MB
- **Trạng thái**: Hiển thị/ẩn cho sinh viên

#### 3. Chỉnh sửa tài liệu
- **Cập nhật thông tin**: Tiêu đề, mô tả, trạng thái
- **Thay đổi file**: Upload file mới thay thế file cũ
- **Giữ nguyên**: Số lượt tải xuống và thông tin khác

#### 4. Quản lý trạng thái
- **Bật/tắt hiển thị**: Ẩn tài liệu khỏi sinh viên
- **Xóa tài liệu**: Xóa hoàn toàn khỏi hệ thống

### Cho Sinh viên (Role: 'student')

#### 1. Xem tài liệu
- **Danh sách tài liệu**: Chỉ hiển thị tài liệu được phép
- **Tìm kiếm**: Theo tiêu đề và mô tả
- **Thống kê**: Số lượng tài liệu và lượt tải

#### 2. Tài liệu phổ biến và mới nhất
- **Phổ biến**: Top 5 tài liệu được tải nhiều nhất
- **Mới nhất**: 5 tài liệu mới được upload

#### 3. Chi tiết tài liệu
- **Thông tin đầy đủ**: Tiêu đề, mô tả, kích thước, loại file
- **Người upload**: Thông tin giảng viên chia sẻ
- **Lượt tải xuống**: Số lần được tải

#### 4. Tải xuống tài liệu
- **Tải xuống**: File gốc với tên ban đầu
- **Theo dõi**: Số lượt tải được cập nhật tự động

## Cách sử dụng

### Giảng viên

#### Upload tài liệu mới
1. Đăng nhập với tài khoản giảng viên
2. Vào menu "Quản lý tài liệu"
3. Click "Thêm Tài liệu"
4. Điền thông tin:
   - **Tiêu đề**: Tên tài liệu (bắt buộc)
   - **Mô tả**: Mô tả nội dung (tùy chọn)
   - **File**: Chọn file từ máy tính
   - **Hiển thị**: Tích để hiển thị cho sinh viên
5. Click "Tải lên"

#### Quản lý tài liệu
1. Vào trang "Quản lý tài liệu"
2. Xem danh sách tài liệu đã upload
3. Sử dụng các nút thao tác:
   - **Tải xuống**: Tải file về máy
   - **Chỉnh sửa**: Cập nhật thông tin
   - **Bật/tắt hiển thị**: Ẩn/hiện cho sinh viên
   - **Xóa**: Xóa tài liệu

#### Chỉnh sửa tài liệu
1. Click "Chỉnh sửa" trên tài liệu
2. Cập nhật thông tin cần thiết
3. Upload file mới (nếu cần)
4. Click "Lưu thay đổi"

### Sinh viên

#### Xem tài liệu
1. Đăng nhập với tài khoản sinh viên
2. Vào menu "Tài liệu học tập"
3. Xem danh sách tài liệu có sẵn
4. Sử dụng thanh tìm kiếm để tìm tài liệu

#### Tải xuống tài liệu
1. Từ danh sách tài liệu, click "Tải xuống"
2. Hoặc vào "Chi tiết" rồi click "Tải xuống"
3. File sẽ được tải về thư mục Downloads

## Cấu trúc dữ liệu

### Document Collection
```json
{
  "_id": "ObjectId",
  "title": "Tiêu đề tài liệu",
  "description": "Mô tả nội dung",
  "file_path": "/path/to/file",
  "file_name": "original_filename.pdf",
  "file_size": 1024000,
  "file_type": "pdf",
  "uploaded_by": "lecture_username",
  "is_visible": true,
  "download_count": 15,
  "created_at": "2025-01-02T10:00:00Z",
  "updated_at": "2025-01-02T10:00:00Z"
}
```

## Bảo mật

### Phân quyền
- **Giảng viên**: Upload, edit, delete, toggle visibility
- **Sinh viên**: View, download (chỉ tài liệu visible)
- **Kiểm tra quyền sở hữu**: Chỉ người upload mới được edit/delete

### File Upload
- **Validation**: Kiểm tra định dạng và kích thước
- **Sanitization**: Tên file được làm sạch
- **Unique naming**: Tên file unique để tránh conflict
- **Storage**: Lưu trong thư mục riêng biệt

### Download Tracking
- **Counter**: Tăng số lượt tải mỗi lần download
- **Security**: Kiểm tra quyền trước khi cho phép download

## API Endpoints

### Giảng viên
- `GET /manage-documents` - Quản lý tài liệu
- `GET/POST /upload-document` - Upload tài liệu mới
- `GET/POST /edit-document/<id>` - Chỉnh sửa tài liệu
- `POST /delete-document/<id>` - Xóa tài liệu
- `POST /toggle-document-visibility/<id>` - Bật/tắt hiển thị

### Sinh viên
- `GET /view-documents` - Xem danh sách tài liệu
- `GET /download-document/<id>` - Tải xuống tài liệu
- `GET /document-details/<id>` - Chi tiết tài liệu

### API
- `GET /api/search-documents` - Tìm kiếm tài liệu
- `GET /api/document-statistics` - Thống kê tài liệu

## Cấu hình

### File Upload
```python
# config.py
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt', 'ppt', 'pptx', 'xls', 'xlsx'}
UPLOAD_FOLDER = 'app/static/uploads'
```

### Thư mục lưu trữ
```
app/static/uploads/
├── avatars/          # Avatar người dùng
├── documents/        # Tài liệu học tập
├── exercises/        # File bài tập
└── submissions/      # Bài nộp của sinh viên
```

## Troubleshooting

### Lỗi thường gặp

1. **File không upload được**
   - Kiểm tra định dạng file (PDF, DOCX, etc.)
   - Kiểm tra kích thước file (tối đa 50MB)
   - Đảm bảo thư mục upload có quyền ghi

2. **Không tải xuống được**
   - Kiểm tra file có tồn tại không
   - Kiểm tra quyền truy cập file
   - Đảm bảo tài liệu đang hiển thị (cho sinh viên)

3. **Lỗi hiển thị**
   - Kiểm tra database connection
   - Kiểm tra quyền người dùng
   - Xem log lỗi trong console

### Bảo trì

1. **Dọn dẹp file**
   - Xóa file không sử dụng định kỳ
   - Backup tài liệu quan trọng
   - Monitor dung lượng ổ đĩa

2. **Cập nhật**
   - Cập nhật danh sách định dạng file hỗ trợ
   - Tăng giới hạn kích thước file nếu cần
   - Cải thiện giao diện người dùng

## Mở rộng

### Tính năng có thể thêm
- **Preview**: Xem trước nội dung file
- **Version control**: Quản lý phiên bản tài liệu
- **Categories**: Phân loại tài liệu
- **Comments**: Bình luận cho tài liệu
- **Analytics**: Thống kê chi tiết sử dụng
- **Bulk upload**: Upload nhiều file cùng lúc
- **Search advanced**: Tìm kiếm nâng cao
- **Export**: Xuất danh sách tài liệu 