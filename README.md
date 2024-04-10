# OceanView - Dự án Quản lý chung cư

Dự án Quản lý Chung cư OceanView là một hệ thống tổ chức và quản lý chung cư, cung cấp một loạt các tính năng hữu ích cho cả quản trị viên và cư dân. Dưới đây là một số tính năng chính của dự án:

- Quản trị viên có thể cấp phát tài khoản cho cư dân.
- Cư dân có thể đăng nhập vào hệ thống với vai trò quản trị viên hoặc cư dân.
- Cư dân có thể thanh toán các loại phí như phí quản lý, phí gửi xe và các phí dịch vụ khác hàng tháng thông qua các phương tiện như chuyển khoản, thanh toán trực tuyến trên hệ thống.
- Cư dân có thể tra cứu hoá đơn đã thanh toán và quản lý các loại hoá đơn trên hệ thống.
- Cư dân có thể đăng ký cho người thân để nhận thẻ giữ xe và ra vào cổng.
- Quản trị viên có thể khoá tài khoản cư dân.
- Mỗi cư dân sẽ có một tủ đồ điện tử trên hệ thống, giúp quản lý đơn hàng và nhận thông báo khi có hàng mới được nhận.
- Cư dân có thể gửi phản ánh về các hoạt động không phù hợp tại chung cư để ban quản trị xử lý.
- Ban quản trị có thể tạo phiếu khảo sát và thống kê kết quả khảo sát từ cư dân về tình hình vệ sinh, cơ sở vật chất và các dịch vụ khác.

Và còn nhiều tính năng khác.

## Hướng dẫn cài đặt và chạy dự án

### 1. Yêu cầu hệ thống

- Python (phiên bản 3.x)
- MySQL
- pip (để quản lý môi trường ảo Python)

### 2. Cài đặt dự án

1. Clone dự án từ repository:

   ```
   git clone https://github.com/tranlequocthong313/OceanView_BE.git
   ```

2. Di chuyển vào thư mục dự án:

   ```
   cd OceanView_BE
   ```

3. Tạo và kích hoạt môi trường ảo:

   ```
   python -m venv venv
   source venv/Scripts/activate
   ```

4. Cài đặt các dependencies:

   ```
   pip install -r requirements.txt
   ```

### 3. Cấu hình biến môi trường

Tạo một tệp `.env` trong thư mục gốc của dự án và cấu hình các biến môi trường cần thiết, bao gồm cả cấu hình cơ sở dữ liệu MySQL:

```
# OceanView environment variables
SECRET_KEY=<seceret_key>
ENVIRONMENT=<environment>
CLOUDINARY_NAME=<your_cloudinary_name>
CLOUDINARY_API_KEY=<your_cloudinary_api_key>
CLOUDINARY_API_SECRET=<your_cloudinary_api_secret>
MYSQL_DATABASE=<your_database_name>
MYSQL_USER=<your_database_user>
MYSQL_PASSWORD=<your_database_password>
MYSQL_HOST=<your_database_host>
MYSQL_PORT=<your_database_port>
```

### 4. Khởi tạo cơ sở dữ liệu

1. Tạo cơ sở dữ liệu MySQL với thông tin đã cấu hình trong `.env`.

2. Chạy các lệnh migrate để tạo bảng và cập nhật cơ sở dữ liệu:

   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

### 5. Chạy dự án

Sau khi hoàn thành các bước trên, bạn có thể khởi động máy chủ phát triển bằng lệnh:

```
python manage.py runserver
```

Mở trình duyệt và truy cập vào `http://127.0.0.1:8000/` để xem dự án OceanView.

---
