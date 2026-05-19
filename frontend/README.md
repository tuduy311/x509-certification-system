# X509 Certificate System Frontend (Streamlit)

Ứng dụng quản lí chứng chỉ số X.509 được xây dựng với **Streamlit** và phthon

## Tính năng

- **Xác thực**: Login/Register với validation
- **User Dashboard**: Trang quản lý cho người dùng
- **Admin Dashboard**: Trang quản lý cho quản trị viên

# Yêu cầu 
- python
- pip

## Cài đặt

### 1. Create virtual environment
```bash
python -m venv venv
```

### 2. Activate virtual environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Copy `.env.example` to `.env` and set values:
```bash
API_URL=http://localhost:8000/api
```

### 5. Run Streamlit app
```bash
streamlit run app.py
```
App will open at `http://localhost:8501`

## Cấu trúc dự án

```
frontend/
|__ app.py
|__ requirements.txt
|__ views/
|    |__ auth.py
|    |__ admin_dashborad
|    |__ user_dashboard
|
|__ README.md

```
