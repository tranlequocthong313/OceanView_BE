# OceanView - Backend (Django)

**OceanView_BE** là phần backend của ứng dụng quản lý chung cư **OceanView**, được phát triển bằng Django. Phần backend này cung cấp các API cần thiết để hỗ trợ các tính năng của ứng dụng di động, bao gồm quản lý người dùng, dịch vụ, hóa đơn, yêu cầu hỗ trợ, và thông báo.

## Tính năng chính

- **Quản lý người dùng**: Đăng ký, đăng nhập, và quản lý thông tin người dùng (cư dân và ban quản lý).
- **Quản lý dịch vụ**: Thêm, cập nhật, xóa, và quản lý các dịch vụ chung cư.
- **Quản lý hóa đơn**: Tạo, cập nhật, và quản lý hóa đơn dịch vụ (điện, nước, dịch vụ chung cư).
- **Yêu cầu hỗ trợ**: Cư dân có thể gửi yêu cầu hỗ trợ hoặc báo cáo sự cố, và ban quản lý có thể phản hồi.
- **Thông báo**: Gửi thông báo đến cư dân về các sự kiện, thông báo chung, hoặc phản hồi yêu cầu.
- **API RESTful**: Cung cấp các API để tích hợp với ứng dụng di động.

## Công nghệ sử dụng

- **Backend**: Django, Django REST Framework (DRF)
- **Database**: PostgreSQL (hoặc MySQL/SQLite tùy cấu hình)
- **Authentication**: JWT (JSON Web Token)
- **API Documentation**: Swagger/OpenAPI (sử dụng DRF Spectacular hoặc drf-yasg)
- **Deployment**: Docker, Nginx, Gunicorn (tùy chọn)

## Cài đặt và chạy dự án

### Yêu cầu hệ thống

- Python 3.8 trở lên
- PostgreSQL (hoặc MySQL/SQLite)
- pip (Python package manager)

### Các bước cài đặt

1. **Clone dự án**:
   ```bash
   git clone https://github.com/tranlequocthong313/OceanView_BE.git
   cd OceanView_BE
   ```

2. **Tạo và kích hoạt môi trường ảo (virtual environment)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Trên Windows: venv\Scripts\activate
   ```

3. **Cài đặt các dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Cấu hình cơ sở dữ liệu**:
   - Tạo một cơ sở dữ liệu PostgreSQL (hoặc sử dụng SQLite cho môi trường phát triển).
   - Cập nhật file `settings.py` với thông tin kết nối cơ sở dữ liệu:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql',
             'NAME': 'your_db_name',
             'USER': 'your_db_user',
             'PASSWORD': 'your_db_password',
             'HOST': 'localhost',
             'PORT': '5432',
         }
     }
     ```

5. **Chạy migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Tạo superuser (quản trị viên)**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Chạy server**:
   ```bash
   python manage.py runserver
   ```

8. **Truy cập API**:
   - Mở trình duyệt và truy cập vào địa chỉ: `http://localhost:8000/api/`
   - Để xem tài liệu API (nếu có), truy cập: `http://localhost:8000/swagger/` hoặc `http://localhost:8000/redoc/`

### Cấu hình môi trường

Tạo file `.env` trong thư mục gốc của dự án và thêm các biến môi trường cần thiết:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

## Cấu trúc thư mục

```
OceanView_BE/
├── oceanview/               # Thư mục chính của project Django
│   ├── settings/            # Cấu hình settings (base.py, dev.py, prod.py)
│   ├── urls.py              # Cấu hình URLs chính
│   ├── wsgi.py              # WSGI config
│   └── asgi.py              # ASGI config
├── apps/                    # Các ứng dụng Django
│   ├── users/               # Quản lý người dùng
│   ├── services/            # Quản lý dịch vụ
│   ├── billing/             # Quản lý hóa đơn
│   ├── support/             # Quản lý yêu cầu hỗ trợ
│   └── notifications/       # Quản lý thông báo
├── manage.py                # Script quản lý Django
├── requirements.txt         # Danh sách các dependencies
├── .env                     # File cấu hình môi trường
└── README.md                # Tài liệu hướng dẫn
```

## API Endpoints

Dưới đây là một số API endpoints chính:

- **Authentication**:
  - `POST /api/auth/register/` - Đăng ký người dùng mới.
  - `POST /api/auth/login/` - Đăng nhập và nhận JWT token.
  - `POST /api/auth/logout/` - Đăng xuất.

- **Users**:
  - `GET /api/users/` - Lấy danh sách người dùng.
  - `GET /api/users/{id}/` - Lấy thông tin chi tiết của một người dùng.
  - `PUT /api/users/{id}/` - Cập nhật thông tin người dùng.

- **Services**:
  - `GET /api/services/` - Lấy danh sách dịch vụ.
  - `POST /api/services/` - Tạo dịch vụ mới.
  - `PUT /api/services/{id}/` - Cập nhật dịch vụ.

- **Billing**:
  - `GET /api/billing/` - Lấy danh sách hóa đơn.
  - `POST /api/billing/` - Tạo hóa đơn mới.
  - `PUT /api/billing/{id}/` - Cập nhật hóa đơn.

- **Support**:
  - `GET /api/support/` - Lấy danh sách yêu cầu hỗ trợ.
  - `POST /api/support/` - Tạo yêu cầu hỗ trợ mới.
  - `PUT /api/support/{id}/` - Cập nhật yêu cầu hỗ trợ.

- **Notifications**:
  - `GET /api/notifications/` - Lấy danh sách thông báo.
  - `POST /api/notifications/` - Gửi thông báo mới.

## Đóng góp

Nếu bạn muốn đóng góp vào dự án, vui lòng làm theo các bước sau:

1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/YourFeatureName`)
3. Commit các thay đổi (`git commit -m 'Add some feature'`)
4. Push lên branch (`git push origin feature/YourFeatureName`)
5. Mở một Pull Request

## Liên hệ

Nếu bạn có bất kỳ câu hỏi hoặc góp ý nào, vui lòng liên hệ:

- **Tên**: Trần Lê Quốc Thông
- **Email**: tranlequocthong313@gmail.com
- **GitHub**: [tranlequocthong313](https://github.com/tranlequocthong313)
