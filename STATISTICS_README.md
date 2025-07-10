# Tính năng Thống kê cho Giảng viên

## Tổng quan

Tính năng thống kê cung cấp cho giảng viên một dashboard toàn diện để theo dõi tiến độ học tập, điểm số, số lượng bài nộp và xuất báo cáo chi tiết.

## Tính năng chính

### 1. Dashboard Tổng quan
- **Thống kê khóa học**: Số lượng khóa học, khóa học đang hoạt động
- **Thống kê sinh viên**: Tổng số sinh viên đăng ký
- **Thống kê bài tập**: Số bài tập đã tạo, bài tập đang hiển thị
- **Thống kê bài nộp**: Tổng số bài nộp, bài nộp trong 7 ngày gần nhất
- **Thống kê Quiz**: Số quiz đã tạo, bài nộp quiz
- **Thống kê tài liệu**: Số tài liệu đã upload, lượt tải xuống
- **Điểm trung bình**: Điểm trung bình của tất cả bài tập

### 2. Biểu đồ hoạt động
- **Biểu đồ 7 ngày**: Hiển thị số bài nộp và điểm trung bình theo ngày
- **Bài nộp gần đây**: Danh sách 5 bài nộp mới nhất
- **Thống kê real-time**: Cập nhật theo thời gian thực

### 3. Thống kê tiến độ khóa học
- **Thống kê bài tập**: Tỷ lệ hoàn thành, điểm trung bình từng bài
- **Thống kê sinh viên**: Tiến độ học tập, điểm số từng sinh viên
- **Phân tích chi tiết**: Progress bars, badges trạng thái

### 4. Xuất báo cáo
- **Excel Report**: Báo cáo chi tiết với nhiều sheet
- **PDF Report**: Báo cáo định dạng PDF (đang phát triển)
- **Tùy chọn xuất**: Chọn định dạng và thời gian

## Cách sử dụng

### Truy cập Dashboard
1. Đăng nhập với tài khoản giảng viên
2. Tự động redirect về dashboard thống kê
3. Hoặc click "Dashboard" trong navigation

### Xem thống kê tiến độ khóa học
1. Từ dashboard, click vào khóa học cụ thể
2. Xem thống kê chi tiết bài tập và sinh viên
3. Phân tích tỷ lệ hoàn thành và điểm số

### Xuất báo cáo
1. Từ dashboard, click "Xuất Excel" hoặc "Xuất PDF"
2. Chọn định dạng mong muốn
3. File sẽ được tải về máy

## Cấu trúc dữ liệu

### Dashboard Stats
```json
{
  "courses": {
    "total": 5,
    "active": 3
  },
  "students": {
    "total": 25
  },
  "exercises": {
    "total": 15,
    "active": 12
  },
  "submissions": {
    "total": 120,
    "recent_7_days": 15
  },
  "quizzes": {
    "total": 8,
    "submissions": 45,
    "recent_7_days": 8
  },
  "documents": {
    "total": 20,
    "downloads": 150
  },
  "performance": {
    "avg_score": 8.2,
    "total_scores": 95
  }
}
```

### Course Progress Stats
```json
{
  "course": {
    "id": "course_id",
    "name": "Python Programming",
    "total_students": 15,
    "total_exercises": 10
  },
  "exercise_stats": [
    {
      "exercise_id": "ex_id",
      "title": "Bài tập 1",
      "total_submissions": 15,
      "completed_submissions": 12,
      "completion_rate": 80.0,
      "avg_score": 8.5
    }
  ],
  "student_stats": [
    {
      "username": "student1",
      "full_name": "Nguyễn Văn A",
      "completed_exercises": 8,
      "total_exercises": 10,
      "progress_rate": 80.0,
      "avg_score": 8.2
    }
  ]
}
```

## API Endpoints

### Dashboard
- `GET /lecture/dashboard` - Dashboard tổng quan
- `GET /lecture/course/<course_id>/progress` - Thống kê tiến độ khóa học
- `GET /lecture/recent-activity` - Hoạt động gần đây

### Export Reports
- `GET /lecture/export-report?format=excel` - Xuất báo cáo Excel
- `GET /lecture/export-report?format=pdf` - Xuất báo cáo PDF

## Cấu hình

### Requirements
```txt
openpyxl>=3.1.2
reportlab>=4.0.0
```

### CSS Files
- `app/static/css/dashboard.css` - Styling cho dashboard

### Templates
- `app/templates/lecture/dashboard.html` - Dashboard chính
- `app/templates/lecture/course_progress.html` - Thống kê khóa học
- `app/templates/lecture/recent_activity.html` - Hoạt động gần đây

## Tính năng nâng cao

### 1. Real-time Updates
- WebSocket để cập nhật thống kê real-time
- Auto-refresh dashboard mỗi 5 phút

### 2. Advanced Analytics
- Phân tích xu hướng học tập
- Dự đoán điểm số
- Phát hiện sinh viên có nguy cơ

### 3. Custom Reports
- Tạo báo cáo tùy chỉnh
- Lọc theo thời gian, khóa học
- Export nhiều định dạng

### 4. Notifications
- Thông báo bài nộp mới
- Alert khi điểm thấp
- Reminder cho deadline

## Troubleshooting

### Lỗi thường gặp

1. **Dashboard không load được**
   - Kiểm tra database connection
   - Kiểm tra quyền người dùng
   - Xem log lỗi trong console

2. **Thống kê không chính xác**
   - Kiểm tra dữ liệu trong database
   - Verify các relationship giữa collections
   - Refresh cache nếu cần

3. **Export báo cáo lỗi**
   - Kiểm tra thư viện openpyxl/reportlab
   - Đảm bảo đủ quyền ghi file
   - Kiểm tra dung lượng ổ đĩa

### Performance Optimization

1. **Database Indexing**
   ```javascript
   // Index cho queries thống kê
   db.submissions.createIndex({"exercise_id": 1, "submitted_at": -1})
   db.submissions.createIndex({"user_id": 1, "exercise_id": 1})
   ```

2. **Caching**
   - Cache thống kê tổng quan
   - Cache biểu đồ 7 ngày
   - Invalidate cache khi có dữ liệu mới

3. **Pagination**
   - Phân trang cho danh sách bài nộp
   - Lazy loading cho bảng lớn
   - Virtual scrolling cho performance

## Mở rộng

### Thêm biểu đồ mới
```javascript
// Thêm biểu đồ phân bố điểm
const scoreDistributionChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['0-5', '5-7', '7-9', '9-10'],
        datasets: [{
            data: [5, 15, 25, 10],
            backgroundColor: ['#e74a3b', '#f6c23e', '#36b9cc', '#1cc88a']
        }]
    }
});
```

### Thêm metrics mới
```python
# Thêm thống kê thời gian hoàn thành
def get_completion_time_stats(exercise_id):
    submissions = Submission.find_by_exercise(exercise_id)
    completion_times = []
    for sub in submissions:
        if sub.get('submitted_at') and sub.get('created_at'):
            time_diff = sub['submitted_at'] - sub['created_at']
            completion_times.append(time_diff.total_seconds() / 3600)  # hours
    
    return {
        'avg_completion_time': sum(completion_times) / len(completion_times),
        'min_completion_time': min(completion_times),
        'max_completion_time': max(completion_times)
    }
```

Tính năng thống kê này cung cấp cho giảng viên một công cụ mạnh mẽ để theo dõi và đánh giá hiệu quả giảng dạy, giúp cải thiện chất lượng học tập của sinh viên. 