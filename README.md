# models -> cpntrollers -> routes -> init.py->config.py->
# Hệ thống Quản lý Khóa học Online

## Mô tả
Hệ thống quản lý khóa học online được xây dựng bằng Flask, cho phép người dùng đăng ký, đăng nhập, quản lý thông tin cá nhân và tham gia các khóa học.

## Tính năng chính

### 1. Quản lý tài khoản
- Đăng ký tài khoản với xác thực email OTP
- Đăng nhập với xác thực 2 yếu tố (2FA)
- Quản lý thông tin cá nhân
- Thay đổi mật khẩu với xác thực OTP

### 2. Thông tin cá nhân
Người dùng có thể quản lý thông tin cá nhân với các trường:

#### Thông tin cơ bản:
- **Avatar**: Tải lên ảnh đại diện (JPG, PNG, JPEG, GIF)
- **Họ và tên**: Nhập họ và tên đầy đủ
- **Quê quán**: Thông tin về quê quán
- **Ngày sinh**: Chọn ngày, tháng, năm sinh
- **Số điện thoại**: Số điện thoại liên lạc
- **Email**: Email liên lạc
- **Giới thiệu bản thân**: Mô tả ngắn gọn về bản thân

#### Bảo mật:
- **Xác thực 2 yếu tố (2FA)**: Bật/tắt xác thực qua email
- **Thay đổi mật khẩu**: Với xác thực OTP

### 3. Quy trình thay đổi mật khẩu
1. **Nhập mật khẩu cũ**: Xác nhận mật khẩu hiện tại
2. **Nhập mật khẩu mới**: Mật khẩu mới (tối thiểu 6 ký tự)
3. **Xác nhận mật khẩu mới**: Nhập lại mật khẩu mới
4. **Gửi mã OTP**: Hệ thống gửi mã OTP đến email
5. **Nhập mã OTP**: Xác thực mã OTP 6 số
6. **Thành công**: Mật khẩu được thay đổi

### 4. Quản lý khóa học
- Tạo và quản lý khóa học (dành cho giảng viên)
- Xem danh sách khóa học
- Quản lý chương học

## Cài đặt và chạy

### Yêu cầu hệ thống
- Python 3.8+
- MongoDB
- SMTP server (cho gửi email)

### Cài đặt
1. Clone repository:
```bash
git clone <repository-url>
cd Python
```

2. Tạo virtual environment:
```bash
python -m venv venv
```

3. Kích hoạt virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

5. Cấu hình môi trường:
Tạo file `.env` với các thông tin:
```
MONGODB_URI=mongodb://localhost:27017/your_database
SECRET_KEY=your_secret_key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

6. Chạy ứng dụng:
```bash
python run.py
```

## Cấu trúc thư mục
```
Python/
├── app/
│   ├── controllers/          # Controllers xử lý logic
│   ├── models/              # Models dữ liệu
│   ├── routes/              # Routes định tuyến
│   ├── templates/           # Templates HTML
│   ├── static/              # Static files (CSS, JS, images)
│   │   └── uploads/
│   │       └── avatars/     # Thư mục lưu avatar
│   ├── utils/               # Utilities và decorators
│   ├── forms.py             # Forms validation
│   └── extensions.py        # Flask extensions
├── config.py                # Cấu hình ứng dụng
├── run.py                   # Entry point
└── requirements.txt         # Dependencies
```

## Tính năng bảo mật
- Xác thực 2 yếu tố (2FA) qua email
- Mã hóa mật khẩu với bcrypt
- Session management
- CSRF protection
- File upload validation
- OTP expiration (5 phút)

## API Endpoints

### Authentication
- `POST /auth/register` - Đăng ký tài khoản
- `POST /auth/verify-register-otp` - Xác thực OTP đăng ký
- `POST /auth/login` - Đăng nhập
- `POST /auth/verify-otp` - Xác thực OTP đăng nhập
- `GET /auth/logout` - Đăng xuất

### Profile Management
- `GET /auth/profile` - Xem thông tin cá nhân
- `GET/POST /auth/edit-profile` - Chỉnh sửa thông tin cá nhân
- `GET/POST /auth/change-password` - Thay đổi mật khẩu
- `POST /auth/send-change-password-otp` - Gửi OTP thay đổi mật khẩu
- `GET/POST /auth/security-settings` - Cài đặt bảo mật

### Course Management
- `GET /course/manage-courses` - Quản lý khóa học
- `GET/POST /course/create` - Tạo khóa học mới
- `GET/POST /course/<id>/manage-chapters` - Quản lý chương học

## Lưu ý
- Đảm bảo MongoDB đang chạy trước khi khởi động ứng dụng
- Cấu hình email SMTP để sử dụng tính năng OTP
- Tạo thư mục `app/static/uploads/avatars` để lưu trữ avatar
- Backup dữ liệu thường xuyên

## Đóng góp
Mọi đóng góp đều được chào đón. Vui lòng tạo issue hoặc pull request để đóng góp vào dự án.
