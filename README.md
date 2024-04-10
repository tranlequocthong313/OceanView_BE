# OceanView - Dự án Quản lý chung cư

Dự án Quản lý Chung cư OceanView là một hệ thống quản lý dành cho các tòa nhà chung cư, cung cấp một loạt các tính năng quản lý và tiện ích cho cả quản trị viên và cư dân. Dưới đây là một số tính năng chính của dự án:

- **Quản lý Tài khoản:** Quản trị viên có thể tạo và quản lý tài khoản cho cư dân.
- **Thanh Toán Phí:** Cư dân có thể thanh toán các loại phí như phí quản lý, phí gửi xe và các dịch vụ khác thông qua các phương tiện thanh toán trực tuyến.
- **Quản lý Hoá đơn:** Cư dân có thể tra cứu và quản lý các hoá đơn đã thanh toán trên hệ thống.
- **Quản lý Thẻ Giữ Xe:** Cư dân có thể đăng ký cho người thân để nhận thẻ giữ xe và ra vào cổng.
- **Gửi Phản ánh:** Cư dân có thể gửi phản ánh về các vấn đề không phù hợp để ban quản trị xử lý.
- **Khảo sát và Thống kê:** Ban quản trị có thể tạo và thống kê kết quả khảo sát từ cư dân về các hoạt động và dịch vụ tại chung cư.

Và còn nhiều tính năng khác.

## Hướng dẫn Cài đặt và Chạy dự án

### 1. Yêu cầu hệ thống

- Python (phiên bản 3.x)
- MySQL
- pip (để quản lý môi trường ảo Python)

### 2. Cài đặt dự án

1. **Clone dự án từ repository:**

   ```
   git clone https://github.com/tranlequocthong313/OceanView_BE.git
   ```

2. **Di chuyển vào thư mục dự án:**

   ```
   cd OceanView_BE
   ```

3. **Tạo và kích hoạt môi trường ảo:**

   ```
   python -m venv venv
   source venv/Scripts/activate
   ```

4. **Cài đặt dependencies:**

   ```
   pip install -r requirements.txt
   ```

### 3. Cấu hình biến môi trường

Tạo một tệp `.env` trong thư mục gốc của dự án và cấu hình các biến môi trường cần thiết, bao gồm cả cấu hình cơ sở dữ liệu MySQL.

### 4. Khởi tạo cơ sở dữ liệu

1. **Tạo cơ sở dữ liệu MySQL** với thông tin đã cấu hình trong `.env`.

2. **Chạy migrations để tạo bảng và cập nhật cơ sở dữ liệu:**

   ```
   python manage.py migrate
   ```

### 5. Chạy dự án

Sau khi hoàn thành các bước trên, bạn có thể khởi động máy chủ phát triển bằng lệnh:

```
python manage.py runserver
```

Mở trình duyệt và truy cập vào `http://127.0.0.1:8000/` để xem dự án OceanView.

---
