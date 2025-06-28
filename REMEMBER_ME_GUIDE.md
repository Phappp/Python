# Hướng dẫn sử dụng chức năng "Ghi nhớ đăng nhập"

## Tổng quan
Chức năng "Ghi nhớ đăng nhập" (Remember Me) cho phép người dùng duy trì trạng thái đăng nhập trong 30 ngày mà không cần đăng nhập lại mỗi khi đóng trình duyệt.

## Cách hoạt động

### 1. Khi đăng nhập
- Người dùng tích vào checkbox "Ghi nhớ đăng nhập" khi đăng nhập
- Hệ thống sẽ tạo session có thời hạn 30 ngày thay vì 30 phút như bình thường
- Cookie session sẽ được lưu trữ trong trình duyệt

### 2. Trong quá trình sử dụng
- Session sẽ được tự động refresh mỗi khi người dùng thực hiện request
- Thời gian hết hạn sẽ được kéo dài thêm 30 ngày từ thời điểm request cuối cùng

### 3. Khi đăng xuất
- Toàn bộ session sẽ bị xóa, bao gồm cả remember me
- Người dùng sẽ cần đăng nhập lại

## Các tính năng

### 1. Hiển thị trạng thái
- Trang Profile hiển thị trạng thái remember me (đang hoạt động/không hoạt động)
- Trang Session Info hiển thị chi tiết về thời gian hết hạn và thông tin session

### 2. Quản lý remember me
- Người dùng có thể tắt remember me mà không cần đăng xuất
- Nút "Tắt" trong trang Profile để xóa remember me
- Xác nhận trước khi tắt để tránh thao tác nhầm

### 3. Bảo mật
- Session được mã hóa và bảo vệ
- Cookie có thuộc tính HttpOnly và SameSite để tăng bảo mật
- Session ID được tạo ngẫu nhiên

## Cấu hình

### 1. Thời gian session
```python
# config.py
PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # Session thường
REMEMBER_ME_DURATION = timedelta(days=30)          # Remember me session
```

### 2. Cookie settings
```python
# app/__init__.py
SESSION_COOKIE_NAME='app_session'
SESSION_COOKIE_SECURE=False  # True trong production
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='Lax'
SESSION_COOKIE_MAX_AGE=30*24*60*60  # 30 days
```

## API Endpoints

### 1. Đăng nhập với remember me
```
POST /auth/login
Body: {
    "username": "user",
    "password": "password", 
    "remember_me": true
}
```

### 2. Xóa remember me
```
POST /auth/clear-remember-me
```

### 3. Xem thông tin session
```
GET /auth/session-info
```

## Sử dụng trong code

### 1. Kiểm tra trạng thái remember me
```python
from app.utils.decorators import remember_me_status

status = remember_me_status()
if status['remember_me']:
    print("Remember me đang hoạt động")
```

### 2. Trong template
```html
{% if remember_me %}
    <span class="badge bg-success">Đang hoạt động</span>
{% else %}
    <span class="badge bg-secondary">Không hoạt động</span>
{% endif %}
```

## Lưu ý bảo mật

1. **Không sử dụng trên thiết bị công cộng**: Remember me có thể gây rủi ro bảo mật trên máy tính công cộng

2. **Đăng xuất khi không sử dụng**: Luôn đăng xuất khi sử dụng xong trên thiết bị không phải của mình

3. **Kiểm tra thường xuyên**: Người dùng nên kiểm tra trạng thái session trong trang Profile

4. **Tắt khi cần thiết**: Có thể tắt remember me bất cứ lúc nào mà không cần đăng xuất

## Troubleshooting

### 1. Remember me không hoạt động
- Kiểm tra cấu hình cookie trong trình duyệt
- Đảm bảo không có extension chặn cookie
- Kiểm tra cài đặt bảo mật trình duyệt

### 2. Session bị mất sớm
- Kiểm tra thời gian hệ thống
- Đảm bảo không có lỗi trong cấu hình session
- Kiểm tra log để tìm lỗi

### 3. Không thể tắt remember me
- Thử đăng xuất và đăng nhập lại
- Xóa cookie thủ công trong trình duyệt
- Kiểm tra quyền truy cập session

## Cập nhật và bảo trì

- Cập nhật thời gian session theo yêu cầu bảo mật
- Kiểm tra và cập nhật cấu hình cookie định kỳ
- Monitor log để phát hiện vấn đề bảo mật
- Backup cấu hình session trước khi thay đổi 
