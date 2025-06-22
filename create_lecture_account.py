from app import create_app
from app.models.user_model import User

def create_lecture_account():
    app = create_app()
    with app.app_context():
        # Kiểm tra xem tài khoản lecture đã tồn tại chưa
        existing_lecture = User.find_by_username('lecture')
        if existing_lecture is None:
            # Tạo tài khoản lecture mặc định
            User.create('lecture', 'lecture123', 'lecture')
            print("Đã tạo tài khoản lecture thành công!")
            print("Username: lecture")
            print("Password: lecture123")
            print("Role: lecture")
        else:
            print("Tài khoản lecture đã tồn tại!")

if __name__ == '__main__':
    create_lecture_account() 