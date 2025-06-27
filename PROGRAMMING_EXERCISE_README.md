# Hệ thống Bài tập Lập trình với AI Hỗ trợ

## Tổng quan

Hệ thống bài tập lập trình được xây dựng để giúp giảng viên tạo, quản lý và đánh giá bài tập lập trình một cách tự động với sự hỗ trợ của AI. Sinh viên có thể làm bài trực tuyến và nhận phản hồi chất lượng ngay lập tức.

## Tính năng chính

### Cho Giảng viên

#### 1. Tạo bài tập lập trình
- **Tiêu đề và mô tả**: Viết đề bài chi tiết với yêu cầu và ràng buộc
- **Ngôn ngữ hỗ trợ**: Python, Java, C++, JavaScript, C#, PHP, Ruby, Go, Rust, Swift
- **Test cases**: Tạo test cases công khai và ẩn để chấm điểm
- **Giới hạn**: Thiết lập giới hạn thời gian và bộ nhớ
- **Trạng thái**: Ẩn/hiện bài tập cho sinh viên

#### 2. Quản lý bài tập
- **Danh sách bài tập**: Xem tất cả bài tập đã tạo
- **Bộ lọc**: Lọc theo ngôn ngữ, trạng thái, tìm kiếm theo tên
- **Thống kê**: Số lượng bài tập, trạng thái hiển thị
- **Chỉnh sửa**: Cập nhật thông tin bài tập và test cases
- **Xóa**: Xóa bài tập không cần thiết

#### 3. Xem bài nộp và đánh giá
- **Danh sách bài nộp**: Xem tất cả bài nộp của sinh viên
- **Thống kê chi tiết**: Điểm trung bình, cao nhất, thấp nhất
- **Biểu đồ phân bố điểm**: Trực quan hóa kết quả
- **Export CSV**: Xuất dữ liệu để phân tích

#### 4. Chấm điểm tự động với AI
- **Test cases**: Chấm điểm dựa trên kết quả test (70%)
- **AI Analysis**: Phân tích code quality (30%)
- **Phản hồi AI**: Nhận xét về cấu trúc code, tên biến, comment
- **Phản hồi thủ công**: Giảng viên có thể thêm nhận xét và điều chỉnh điểm

### Cho Sinh viên

#### 1. Xem danh sách bài tập
- **Trạng thái**: Xem bài tập đã nộp/chưa nộp
- **Điểm số**: Xem điểm đã đạt được
- **Tiến độ**: Theo dõi tiến độ học tập

#### 2. Làm bài tập
- **Code editor**: Viết code trực tuyến với syntax highlighting
- **Test trước khi nộp**: Chạy thử code với input tùy chọn
- **Hỗ trợ ngôn ngữ**: Code mẫu cho từng ngôn ngữ
- **Nộp bài**: Nộp bài và nhận kết quả ngay lập tức

#### 3. Xem kết quả
- **Điểm số**: Điểm chi tiết với phân tích
- **Test results**: Kết quả từng test case
- **AI feedback**: Phản hồi từ AI về code quality
- **Cải thiện**: Gợi ý cách cải thiện code

## Cách sử dụng

### Giảng viên

#### Tạo bài tập mới
1. Đăng nhập với tài khoản giảng viên
2. Vào menu "Bài tập lập trình"
3. Click "Tạo bài tập mới"
4. Điền thông tin:
   - **Tiêu đề**: Tên bài tập
   - **Mô tả**: Yêu cầu chi tiết, ví dụ input/output
   - **Ngôn ngữ**: Chọn ngôn ngữ lập trình
   - **Test cases**: JSON format với input, expected output
   - **Giới hạn**: Thời gian và bộ nhớ
5. Click "Tạo bài tập"

#### Quản lý bài tập
1. Vào trang "Quản lý bài tập lập trình"
2. Sử dụng bộ lọc để tìm bài tập
3. Click "Sửa" để chỉnh sửa
4. Click "Xem bài nộp" để xem kết quả sinh viên

#### Xem bài nộp
1. Click "Xem bài nộp" trên bài tập
2. Xem danh sách sinh viên đã nộp
3. Click "Xem chi tiết" để xem code và kết quả
4. Thêm phản hồi thủ công nếu cần

### Sinh viên

#### Làm bài tập
1. Đăng nhập với tài khoản sinh viên
2. Vào menu "Lập trình" trong toolbar
3. Chọn bài tập muốn làm
4. Click "Làm bài" hoặc "Xem đề bài"
5. Viết code trong editor
6. Test code trước khi nộp
7. Click "Nộp bài"

#### Xem kết quả
1. Vào trang "Lập trình"
2. Click "Xem kết quả" trên bài đã nộp
3. Xem điểm số và phản hồi AI
4. Xem chi tiết test cases

## Cấu trúc dữ liệu

### Exercise (Bài tập)
```json
{
  "title": "Tính tổng dãy số",
  "description": "Viết chương trình tính tổng n số nguyên...",
  "language_supported": ["python"],
  "test_cases": [
    {
      "input": "5\n3 1 4 1 5",
      "expected_output": "14",
      "description": "Test case cơ bản",
      "is_hidden": false
    }
  ],
  "time_limit": 5,
  "memory_limit": 128,
  "is_visible": true,
  "created_by": "lecturer_username"
}
```

### Submission (Bài nộp)
```json
{
  "exercise_id": "exercise_id",
  "user_id": "student_username",
  "code": "def main():\n    n = int(input())\n    ...",
  "language": "python",
  "score": 8.5,
  "llm_feedback": "Code có cấu trúc tốt...",
  "test_results": [
    {
      "test_case": 1,
      "input": "5\n3 1 4 1 5",
      "expected": "14",
      "actual": "14",
      "passed": true
    }
  ],
  "execution_time": 0.123,
  "memory_used": 12.5
}
```

## Công nghệ sử dụng

- **Backend**: Flask, MongoDB
- **Frontend**: Bootstrap 5, JavaScript
- **Code Execution**: Subprocess với sandbox
- **AI Analysis**: Mô phỏng AI (có thể tích hợp OpenAI API)
- **Code Highlighting**: Prism.js
- **Charts**: Chart.js

## Bảo mật

- **Sandbox**: Code chạy trong môi trường cách ly
- **Time limits**: Giới hạn thời gian chạy code
- **Memory limits**: Giới hạn bộ nhớ sử dụng
- **Input validation**: Kiểm tra input đầu vào
- **Role-based access**: Phân quyền giảng viên/sinh viên

## Mở rộng

### Tích hợp AI thực tế
```python
# Thay thế hàm _analyze_code_with_ai trong controller
def _analyze_code_with_ai(code, language, exercise):
    # Gọi OpenAI API hoặc LLM khác
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Bạn là giáo viên lập trình..."},
            {"role": "user", "content": f"Phân tích code {language}:\n{code}"}
        ]
    )
    return response.choices[0].message.content
```

### Thêm ngôn ngữ mới
1. Thêm vào choices trong form
2. Cập nhật hàm `_get_file_extension`
3. Thêm logic compile/run trong `_run_code`

### Tính năng nâng cao
- **Plagiarism detection**: Phát hiện đạo code
- **Code review**: Hệ thống review code
- **Collaborative coding**: Lập trình nhóm
- **Real-time feedback**: Phản hồi real-time
- **Gamification**: Hệ thống điểm, badge

## Troubleshooting

### Lỗi thường gặp

1. **Code không chạy được**
   - Kiểm tra cú pháp
   - Đảm bảo đọc input đúng format
   - Test với input mẫu

2. **Timeout error**
   - Tối ưu thuật toán
   - Kiểm tra vòng lặp vô hạn
   - Giảm độ phức tạp

3. **Memory limit exceeded**
   - Tối ưu cấu trúc dữ liệu
   - Giải phóng bộ nhớ không cần thiết
   - Sử dụng generator thay vì list

### Debug

1. **Test code trước khi nộp**
2. **Xem test cases công khai**
3. **Kiểm tra format input/output**
4. **Đọc phản hồi AI**

## Liên hệ

Nếu có vấn đề hoặc góp ý, vui lòng liên hệ:
- Email: support@example.com
- GitHub: https://github.com/your-repo
- Documentation: https://docs.example.com 