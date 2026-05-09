# X509 Certificate System Frontend (Streamlit)


## Setup

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
