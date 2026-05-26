import requests
from .helpers import _get, _post, _put, BASE_URL



def login(username: str, password: str) -> dict:
    """
    POST /api/auth/login
    Body: {"username": ..., "password": ...}
    Returns: {"access_token": str, "token_type": "bearer"}
    """
    resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": password},
        timeout=10
    )
    resp.raise_for_status()
    return resp.json()


def register(username: str, password: str) -> dict:
    """
    POST /api/auth/register
    Body: {"username": ..., "password": ...}
    Returns: UserOut dict
    """
    resp = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"username": username, "password": password},
        timeout=10
    )
    resp.raise_for_status()
    return resp.json()


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