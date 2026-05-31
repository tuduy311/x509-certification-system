import requests
import streamlit as st
from .helpers import _get, _post, _put, BASE_URL, _handle_http_error, BackendError



def login(username: str, password: str) -> dict:
    """
    POST /api/auth/login
    Body: {"username": ..., "password": ...}
    Returns: {"access_token": str, "token_type": "bearer"}
    Raises BackendError (with st.error already shown) on HTTP errors,
    or re-raises requests.HTTPError for 400 so the caller can show a
    custom "wrong credentials" message.
    """
    try:
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 400:
            raise
        
        _handle_http_error(e)
    except requests.exceptions.ConnectionError:
        st.error("❌ Không thể kết nối đến backend. Hãy đảm bảo server đang chạy tại http://localhost:8000")
        raise


def register(username: str, password: str) -> dict:
    """
    POST /api/auth/register
    Body: {"username": ..., "password": ...}
    Returns: UserOut dict
    Raises BackendError (with st.error already shown) on HTTP errors,
    or re-raises requests.HTTPError for 400 so the caller can show a
    custom validation message.
    """
    try:
        resp = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"username": username, "password": password},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 400:
            raise

        _handle_http_error(e)
    except requests.exceptions.ConnectionError:
        st.error("❌ Không thể kết nối đến backend. Hãy đảm bảo server đang chạy.")
        raise


def change_password(old_password: str, new_password: str, confirm_new_password: str) -> dict:
    """
    PUT /api/auth/change-password
    
    Request Body (JSON):
    {
        "old_password": "...",
        "new_password": "...",
        "confirm_new_password": "..."
    }
    
    Returns:
        UserOut dict chứa thông tin user sau khi cập nhật thành công.
    """
    
    return _put("/api/auth/change-password", json={
        "old_password": old_password,
        "new_password": new_password,
        "confirm_new_password": confirm_new_password
    })


def get_me() -> dict:
    """
    GET /api/auth/me
    Returns: UserOut dict
    """
    return _get("/api/auth/me")


def logout() -> dict:
    """
    POST /api/auth/logout
    Invalidate the current JWT token by adding it to the blacklist.
    Returns: {"msg": "Successfully logged out"}
    """
    return _post("/api/auth/logout")
