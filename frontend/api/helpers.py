import os
import requests
import streamlit as st

BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

def _auth_headers() -> dict:
    """Return Authorization header dict using the token stored in session_state."""
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}

def _handle_http_error(e: requests.exceptions.HTTPError):
    if e.response is not None and e.response.status_code == 401:
        st.error(
            "🔒 Session expired or invalid token! Please log in again."
        )

        if "access_token" in st.session_state:
            del st.session_state["access_token"]

        st.rerun()

    raise e


def _get(path: str, params: dict | None = None) -> dict | list:
    try:
        resp = requests.get(
            f"{BASE_URL}{path}",
            headers=_auth_headers(),
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        _handle_http_error(e)
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend server.")
        raise


def _post(
    path: str, json: dict | None = None, params: dict | None = None
) -> dict | list:
    try:
        resp = requests.post(
            f"{BASE_URL}{path}",
            headers=_auth_headers(),
            json=json,
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        _handle_http_error(e)
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend server.")
        raise


def _put(
    path: str, json: dict | None = None, params: dict | None = None
) -> dict | list:
    try:
        resp = requests.put(
            f"{BASE_URL}{path}",
            headers=_auth_headers(),
            json=json,
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        _handle_http_error(e)
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend server.")
        raise
