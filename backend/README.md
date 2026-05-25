# Hệ Thống Quản Lý Và Cấp Phát Chứng Nhận X.509 (Backend)

Hệ thống cung cấp giải pháp Quản lý và Cấp phát các giấy chứng nhận số theo tiêu chuẩn X.509 cho các dịch vụ Website nhằm thiết lập kênh truyền an toàn SSL.

Dự án được xây dựng với kiến trúc chuẩn, bảo mật, và đáp ứng đầy đủ các yêu cầu chuyên môn của đồ án Quản trị An toàn thông tin.

## 🚀 Công Nghệ Sử Dụng

- **Ngôn ngữ**: Python 3
- **Framework**: FastAPI (High-performance, dễ dàng scale, tích hợp sẵn Swagger UI)
- **Cơ sở dữ liệu**: SQLite (qua SQLAlchemy ORM - có thể dễ dàng chuyển sang PostgreSQL/MySQL)
- **Mã hóa và PKI**: `cryptography` (Thư viện chuẩn mực xử lý X.509, RSA, CSR, CRL)
- **Bảo mật**: JWT (JSON Web Tokens), `passlib` (Bcrypt hash passwords)

## 📁 Cấu Trúc Dự Án

```text
x509-certification-system/
├── main.py                     # File entry point chạy toàn bộ server API
├── create_initial_data.py      # Script khởi tạo Database và tài khoản Admin mặc định
├── requirements.txt            # Danh sách các thư viện Python cần thiết
└── app/
    ├── api/                    # Chứa tất cả các Endpoints API và logic Routing
    │   ├── api.py              # File Router chính tập hợp mọi Router con
    │   ├── deps.py             # Middleware / Dependencies (Xác thực JWT, lấy User hiện tại...)
    │   └── endpoints/
    │       ├── admin.py        # Logic API của Quản trị viên (Cấp chứng chỉ, Root CA, Config)
    │       ├── auth.py         # Logic API Đăng nhập, Đăng ký, Đổi mật khẩu
    │       └── customer.py     # Logic API Khách hàng (Tạo CSR, xin cấp phép, yêu cầu Revoke)
    ├── core/                   # Cấu hình và chức năng cốt lõi (Core)
    │   ├── config.py           # Thiết lập các biến hệ thống, đường dẫn Database, JWT configs
    │   ├── crypto_utils.py     # Thư viện tùy chỉnh xử lý toàn bộ logic RSA, CSR, X.509, CRL
    │   └── security.py         # Hàm mã hóa Hash Password và giải mã JWT
    ├── db/                     # Tương tác Database (SQLAlchemy)
    │   ├── database.py         # Khởi tạo kết nối SQLite/PostgreSQL
    │   └── models.py           # Các Table Database (User, Certificate, Request, Config...)
    └── schemas/                # Các mô hình dữ liệu (Pydantic Models) để validate input/output
        ├── certificate.py      # Định dạng dữ liệu cho API liên quan đến Chứng chỉ X.509
        └── user.py             # Định dạng dữ liệu cho API liên quan đến User
```

## 🎯 Chức Năng Chính

### 1. Nhóm Quản Trị (Admin)
- Đăng nhập / Đổi mật khẩu.
- Thiết lập thông số kỹ thuật mã hóa mặc định (Độ dài khóa, Thuật toán hash, thời hạn hiệu lực).
- Phát sinh cặp khóa Public / Private cho Root CA.
- Tạo chứng nhận gốc (Root Certificate).
- Quản lý các yêu cầu cấp phát chứng nhận: Phê duyệt (Ký bằng Root CA sinh ra X.509) hoặc Từ chối yêu cầu.
- Quản lý các chứng nhận đã cấp phát: Yêu cầu thu hồi (Revoke).
- Quản lý danh sách chứng nhận bị thu hồi (CRL) và cập nhật hệ thống.
- Theo dõi nhật ký hoạt động (Activity Logs).

### 2. Nhóm Khách Hàng (Customer)
- Đăng ký tài khoản, Đăng nhập và Đổi mật khẩu hệ thống.
- Yêu cầu hệ thống tự động phát sinh cặp khóa bảo mật cá nhân (RSA Public/Private keys) để tải về.
- Gửi yêu cầu cấp phát chứng nhận thông qua chuỗi CSR (Certificate Signing Request).
- Xem danh sách và trạng thái các yêu cầu (Pending, Approved, Rejected).
- Quản lý, xem thông tin và tải về các Chứng nhận X.509 sau khi được duyệt.
- Gửi yêu cầu thu hồi chứng nhận cho Admin.
- Tra cứu danh sách thu hồi CRL toàn hệ thống.
- Upload một file chứng nhận X.509 bất kỳ để trích xuất và xem các thông tin chi tiết.

## ⚙️ Hướng Dẫn Cài Đặt Và Chạy Dịch Vụ

### 1. Yêu cầu hệ thống
- Python 3.10 trở lên.
- Đã cài đặt `pip` và `venv`.

### 2. Cài đặt thư viện
Từ thư mục gốc của dự án, mở terminal và thiết lập môi trường ảo:

```bash
# Tạo môi trường ảo
python3 -m venv venv

# Kích hoạt môi trường (trên Linux/macOS)
source venv/bin/activate
# Trên Windows sử dụng: venv\Scripts\activate

# Cài đặt các gói phụ thuộc
pip install -r requirements.txt
```

### 3. Khởi tạo Cơ Sở Dữ Liệu
Script này sẽ tạo cấu trúc bảng cho SQLite và đồng thời sinh ra tài khoản Admin mặc định:
- **Tài khoản mặc định:** `admin`
- **Mật khẩu:** `admin123`

```bash
python create_initial_data.py
```

### 4. Khởi chạy Server
Dùng Uvicorn để chạy server FastAPI:

```bash
uvicorn main:app --reload --port 8000
```
Server sẽ chạy mặc định tại: `http://127.0.0.1:8000`

## 📖 Tài Liệu API (Swagger UI)

FastAPI hỗ trợ tài liệu tự động, rất tiện lợi để test API ngay trên trình duyệt mà không cần cài Postman.

- Truy cập **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Truy cập **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Tại Swagger UI, bạn có thể thực hiện đăng nhập bằng tài khoản `admin` để lấy `access_token` và thao tác các tác vụ liên quan đến quản trị như tạo Root CA, duyệt CSR, cập nhật CRL.
