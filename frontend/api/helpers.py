import os
import requests
import streamlit as st

BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

class BackendError(requests.exceptions.HTTPError):
    """
    Subclass of HTTPError raised after the error message has already been
    displayed via st.error(). Callers that catch this can safely `pass` or
    `return` without printing a second error message.
    """

    pass


def _auth_headers() -> dict:
    """Return Authorization header dict using the token stored in session_state."""

    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}

def _handle_http_error(e: requests.exceptions.HTTPError):
    """Parse the backend error detail and show a user-friendly st.error message."""
    
    if e.response is not None:
        status_code = e.response.status_code

        if status_code == 401:
            st.error("🔒 Session expired or invalid token! Please log in again.")
            if "access_token" in st.session_state:
                del st.session_state["access_token"]
            st.rerun()

        try:
            detail = e.response.json().get("detail", None)
        except Exception:
            detail = None

        if detail:
            label = {
                400: "❌ Bad request",
                403: "⛔ Access denied",
                404: "🔍 Not found",
                409: "⚠️ Conflict",
                422: "❌ Validation error",
                500: "🔥 Server error",
            }.get(status_code, f"❌ Error {status_code}")
            st.error(f"{label}: {detail}")
        else:
            st.error(f"❌ Error {status_code}: {e.response.text or 'Unknown error'}")
    else:
        st.error(f"❌ Request failed: {e}")

    raise BackendError(str(e), response=e.response)


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
