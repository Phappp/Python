# Hướng dẫn sử dụng chức năng "Lưu tài khoản và mật khẩu"

## Tổng quan
Chức năng "Lưu tài khoản và mật khẩu" đã thay thế chức năng "Remember Me" cũ để cung cấp trải nghiệm đăng nhập thuận tiện hơn cho người dùng.

## Cách hoạt động

### 1. Lưu thông tin đăng nhập
- Khi đăng nhập, người dùng có thể chọn checkbox "Lưu tài khoản và mật khẩu"
- Thông tin đăng nhập (username và password) sẽ được lưu vào localStorage của trình duyệt
- Dữ liệu được mã hóa và chỉ lưu trữ trên thiết bị của người dùng

### 2. Tự động điền thông tin
- Khi người dùng quay lại trang đăng nhập, thông tin sẽ được tự động điền vào form
- Checkbox "Lưu tài khoản và mật khẩu" sẽ được tự động tích
- Người dùng chỉ cần nhấn nút "Đăng nhập" để tiếp tục

### 3. Xóa thông tin đã lưu
- Người dùng có thể nhấn nút "Xóa thông tin đã lưu" để xóa dữ liệu
- Hoặc bỏ tích checkbox "Lưu tài khoản và mật khẩu" khi đăng nhập
- Thông tin sẽ bị xóa khỏi localStorage

## Ưu điểm so với chức năng cũ

### Remember Me (cũ)
- Lưu session trên server trong 30 ngày
- Tốn tài nguyên server
- Có thể gây ra vấn đề bảo mật nếu session bị lộ
- Không thể kiểm soát từ phía client

### Lưu thông tin đăng nhập (mới)
- Lưu trữ hoàn toàn trên client (localStorage)
- Tiết kiệm tài nguyên server
- Người dùng có thể kiểm soát hoàn toàn
- Tự động điền form đăng nhập
- Giao diện thân thiện hơn

## Bảo mật

### Lưu ý quan trọng
- Thông tin được lưu trong localStorage của trình duyệt
- Chỉ an toàn trên thiết bị cá nhân
- Không nên sử dụng trên thiết bị công cộng
- Người dùng có thể xóa thông tin bất cứ lúc nào

### Khuyến nghị
- Chỉ sử dụng trên thiết bị cá nhân
- Thường xuyên thay đổi mật khẩu
- Sử dụng mật khẩu mạnh
- Đăng xuất khi sử dụng xong

## Cách sử dụng

### Đăng nhập lần đầu
1. Nhập username và password
2. Tích vào checkbox "Lưu tài khoản và mật khẩu"
3. Nhấn "Đăng nhập"

### Đăng nhập lần sau
1. Truy cập trang đăng nhập
2. Thông tin sẽ được tự động điền
3. Nhấn "Đăng nhập"

### Xóa thông tin đã lưu
1. Nhấn nút "Xóa thông tin đã lưu" trên form đăng nhập
2. Hoặc bỏ tích checkbox khi đăng nhập

## Hỗ trợ kỹ thuật

### Trình duyệt hỗ trợ
- Chrome (khuyến nghị)
- Firefox
- Safari
- Edge

### Yêu cầu
- Trình duyệt phải hỗ trợ localStorage
- JavaScript phải được bật
- Không sử dụng chế độ ẩn danh (incognito)

### Xử lý sự cố
- Nếu thông tin không được lưu: Kiểm tra cài đặt JavaScript
- Nếu không tự động điền: Xóa cache và thử lại
- Nếu gặp lỗi: Liên hệ admin để được hỗ trợ 