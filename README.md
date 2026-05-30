# 🔐 Hệ Thống Quản Lý và Cấp Phát Chứng Nhận X.509

Hệ thống cho phép **Quản trị viên (Admin)** tạo Root CA và cấp phát chứng nhận số X.509 cho **Khách hàng (Customer)**, hỗ trợ toàn bộ vòng đời của chứng nhận: từ yêu cầu → phê duyệt → thu hồi → cập nhật CRL.

---

## 📦 Tổng Quan Hệ Thống

Hệ thống gồm 2 thành phần chính:

| Thành phần       | Công nghệ                 | Mô tả                                                                           |
| ------------------ | --------------------------- | --------------------------------------------------------------------------------- |
| **Backend**  | Python · FastAPI · SQLite | Cung cấp toàn bộ API xử lý logic PKI, xác thực JWT, quản lý chứng nhận |
| **Frontend** | Python · Streamlit         | Giao diện web người dùng kết nối tới Backend qua REST API                  |

---

## ✨ Chức Năng Chính

**Dành cho Admin:**

- Tạo cặp khóa và chứng nhận gốc (Root CA)
- Thiết lập thông số mã hóa (độ dài khóa, thuật toán hash, thời hạn hiệu lực)
- Phê duyệt hoặc từ chối yêu cầu cấp chứng nhận (CSR)
- Thu hồi chứng nhận và cập nhật danh sách CRL
- Theo dõi nhật ký hoạt động toàn hệ thống

**Dành cho Khách hàng:**

- Đăng ký / đăng nhập tài khoản
- Yêu cầu hệ thống sinh cặp khóa RSA và tải về
- Gửi CSR để xin cấp chứng nhận X.509
- Xem trạng thái yêu cầu và tải về chứng nhận đã được cấp
- Yêu cầu thu hồi chứng nhận
- Upload file chứng nhận bất kỳ để xem thông tin chi tiết
- Tra cứu danh sách thu hồi (CRL) toàn hệ thống

---

## 🚀 Hướng Dẫn Cài Đặt và Chạy

> **Yêu cầu:** Python 3.10 trở lên, `pip` đã được cài đặt.

### Bước 1 — Tạo và kích hoạt môi trường ảo

Chạy lệnh này tại **thư mục gốc** của dự án (nơi chứa file `README.md` này):

```bash
python -m venv venv
```

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

---

### Bước 2 — Cài đặt thư viện cho Backend

```bash
cd backend
pip install -r requirements.txt
```

---

### Bước 3 — Khởi tạo cơ sở dữ liệu

Script dưới đây sẽ tạo file database SQLite và tạo sẵn tài khoản Admin mặc định:

```bash
# (đang ở trong thư mục backend/)
python create_initial_data.py
```

> **Tài khoản Admin mặc định:**
>
> - Username: `admin`
> - Password: `admin123`

---

### Bước 4 — Khởi chạy Backend

```bash
# (đang ở trong thư mục backend/)
uvicorn main:app --reload --port 8000
```

Backend sẽ chạy tại: **http://127.0.0.1:8000**

Tài liệu API (Swagger UI) có thể xem tại: **http://127.0.0.1:8000/docs**

---

### Bước 5 — Cài đặt thư viện cho Frontend

Mở **terminal mới** (vẫn giữ Backend đang chạy), kích hoạt lại venv rồi chạy:

```bash
cd frontend
pip install -r requirements.txt
```

---

### Bước 6 — Cấu hình và khởi chạy Frontend

Tạo file `.env` trong thư mục `frontend/` với nội dung:

```env
API_URL=http://localhost:8000/api
```

Sau đó khởi chạy:

```bash
# (đang ở trong thư mục frontend/)
streamlit run app.py
```

Giao diện web sẽ tự động mở tại: **http://localhost:8501**

---

## 🗂️ Cấu Trúc Thư Mục

```
x509-certification-system/
├── backend/
│   ├── main.py                  # Entry point khởi chạy server
│   ├── create_initial_data.py   # Khởi tạo database và tài khoản Admin
│   ├── requirements.txt
│   └── app/                     # Logic API, mã hóa, database models
│
├── frontend/
│   ├── app.py                   # Entry point giao diện Streamlit
│   ├── requirements.txt
│   └── views/                   # Các trang giao diện (auth, admin, user)
│
└── venv/                        # Môi trường ảo Python (không commit)
```

---

## 📝 Lưu Ý

- Đảm bảo `API_URL` trong file `.env` của Frontend trỏ đúng đến địa chỉ Backend.
- File `sql_app.db` được tự động tạo trong thư mục `backend/` sau khi chạy `create_initial_data.py`.
