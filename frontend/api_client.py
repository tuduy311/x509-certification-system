import os
import requests
import streamlit as st

BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _auth_headers() -> dict:
    """Return Authorization header dict using the token stored in session_state."""
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _get(path: str, params: dict | None = None) -> dict | list:
    resp = requests.get(f"{BASE_URL}{path}", headers=_auth_headers(), params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _post(path: str, json: dict | None = None, params: dict | None = None) -> dict | list:
    resp = requests.post(
        f"{BASE_URL}{path}", headers=_auth_headers(),
        json=json, params=params, timeout=15
    )
    resp.raise_for_status()
    return resp.json()


def _put(path: str, json: dict | None = None, params: dict | None = None) -> dict | list:
    resp = requests.put(
        f"{BASE_URL}{path}", headers=_auth_headers(),
        json=json, params=params, timeout=15
    )
    resp.raise_for_status()
    return resp.json()


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# Customer endpoints
# ─────────────────────────────────────────────────────────────────────────────

def generate_keys(algorithm: str = "RSA", key_size: int = 2048, description: str | None = None) -> dict:
    """
    POST /api/customer/generate-keys
    Body: {"algorithm": str, "key_size": int, "description": str}
    Returns: {"private_key": str, "public_key": str, "key_record": dict}
    """
    return _post("/api/customer/generate-keys", json={
        "algorithm": algorithm,
        "key_size": key_size,
        "description": description
    })


def get_my_keys() -> list:
    """
    GET /api/customer/my-keys
    Returns: List[KeyManagementOut]
    """
    return _get("/api/customer/my-keys")


def request_certificate(csr_pem: str) -> dict:
    """
    POST /api/customer/request-certificate
    Body: {"csr_pem": str}
    Returns: CertificateRequestOut dict
    """
    return _post("/api/customer/request-certificate", json={"csr_pem": csr_pem})


def get_my_requests() -> list:
    """
    GET /api/customer/my-requests
    Returns: List[CertificateRequestOut]
    """
    return _get("/api/customer/my-requests")


def get_my_certificates() -> list:
    """
    GET /api/customer/my-certificates
    Returns: List[CertificateOut]
    """
    return _get("/api/customer/my-certificates")


def request_revoke_certificate(cert_id: int, reason: str) -> dict:
    """
    POST /api/customer/certificates/{cert_id}/request-revoke
    Body: {"reason": str}
    Returns: RevocationRequestOut dict
    """
    return _post(
        f"/api/customer/certificates/{cert_id}/request-revoke",
        json={"reason": reason}
    )


def parse_certificate(cert_pem: str) -> dict:
    """
    POST /api/customer/parse-certificate
    Body: {"cert_pem": str}
    Returns: parsed certificate info dict
    """
    return _post("/api/customer/parse-certificate", json={"cert_pem": cert_pem})


def get_crl() -> dict:
    """
    GET /api/customer/crl  (public – no auth needed, but sends if available)
    Returns: {"crl_pem": str}
    """
    return _get("/api/customer/crl")


# ─────────────────────────────────────────────────────────────────────────────
# Admin endpoints
# ─────────────────────────────────────────────────────────────────────────────

def setup_root_ca(algo: str = "RSA", key_size: int = 2048, validity_days: int = 3650, hash_alg: str = "SHA256") -> dict:
    """
    POST /api/admin/setup-root-ca?algo=...&key_size=...&validity_days=...&hash_alg=...
    Returns: {"msg": "Root CA generated successfully"}
    """
    return _post("/api/admin/setup-root-ca", params={
        "algo": algo,
        "key_size": key_size,
        "validity_days": validity_days,
        "hash_alg": hash_alg
    })


def get_all_requests() -> list:
    """
    GET /api/admin/requests
    Returns: List[CertificateRequestOut]
    """
    return _get("/api/admin/requests")


def approve_request(request_id: int, validity_days: int = 365, hash_alg: str = "SHA256") -> dict:
    """
    POST /api/admin/requests/{request_id}/approve?validity_days=...&hash_alg=...
    Returns: CertificateOut dict
    """
    return _post(f"/api/admin/requests/{request_id}/approve", params={
        "validity_days": validity_days,
        "hash_alg": hash_alg
    })


def reject_request(request_id: int) -> dict:
    """
    POST /api/admin/requests/{request_id}/reject
    Returns: CertificateRequestOut dict
    """
    return _post(f"/api/admin/requests/{request_id}/reject")


def admin_revoke_certificate(cert_id: int) -> dict:
    """
    POST /api/admin/certificates/{cert_id}/revoke
    Returns: CertificateOut dict
    """
    return _post(f"/api/admin/certificates/{cert_id}/revoke")


def get_all_certificates() -> list:
    """
    GET /api/admin/certificates
    Returns: List[CertificateOut] – all issued certificates in the system.
    """
    return _get("/api/admin/certificates")


def get_config() -> dict:
    """
    GET /api/admin/config
    Returns: dict of key→value configuration pairs
    """
    return _get("/api/admin/config")


def update_config(settings_dict: dict) -> dict:
    """
    PUT /api/admin/config
    Body: {"key1": "value1", "key2": "value2"}
    Returns: {"msg": "Configurations updated successfully"}
    """
    return _put("/api/admin/config", json=settings_dict)


def reset_config_to_defaults() -> dict:
    """
    POST /api/admin/config/reset
    Returns: {"msg": "Configuration reset to defaults successfully"}
    """
    return _post("/api/admin/config/reset")


def get_all_options() -> dict:
    """
    GET /api/admin/options/all
    Returns: {"asymmetric_algorithms": [...], "hash_algorithms": [...], "key_lengths": [...], "validity_options": [...]}
    """
    return _get("/api/admin/options/all")


def get_asymmetric_algorithms() -> list:
    """
    GET /api/admin/options/asymmetric-algorithms
    Returns: List[AsymmetricAlgorithmOut]
    """
    return _get("/api/admin/options/asymmetric-algorithms")


def get_hash_algorithms() -> list:
    """
    GET /api/admin/options/hash-algorithms
    Returns: List[HashAlgorithmOut]
    """
    return _get("/api/admin/options/hash-algorithms")


def get_key_lengths() -> list:
    """
    GET /api/admin/options/key-lengths
    Returns: List[KeyLengthOut]
    """
    return _get("/api/admin/options/key-lengths")


def get_validity_options() -> list:
    """
    GET /api/admin/options/validity-options
    Returns: List[ValidityOptionOut]
    """
    return _get("/api/admin/options/validity-options")


def get_revocation_requests() -> list:
    """
    GET /api/admin/revocation-requests
    Returns: List[RevocationRequestOut]
    """
    return _get("/api/admin/revocation-requests")


def approve_revocation_request(req_id: int) -> dict:
    """
    POST /api/admin/revocation-requests/{req_id}/approve
    Returns: CertificateOut dict
    """
    return _post(f"/api/admin/revocation-requests/{req_id}/approve")


def reject_revocation_request(req_id: int) -> dict:
    """
    POST /api/admin/revocation-requests/{req_id}/reject
    Returns: RevocationRequestOut dict (status set to REJECTED)
    """
    return _post(f"/api/admin/revocation-requests/{req_id}/reject")


def admin_renew_certificate(cert_id: int, validity_days: int = 365, hash_alg: str = "SHA256") -> dict:
    """
    POST /api/admin/certificates/{cert_id}/renew?validity_days=...&hash_alg=...
    Re-signs the original CSR and creates a new certificate record.
    Returns: CertificateOut dict
    """
    return _post(f"/api/admin/certificates/{cert_id}/renew", params={
        "validity_days": validity_days,
        "hash_alg": hash_alg
    })


def generate_crl(validity_days: int = 30, hash_alg: str = "SHA256") -> dict:
    """
    POST /api/admin/generate-crl?validity_days=...&hash_alg=...
    Returns: {"crl_pem": str}
    """
    return _post("/api/admin/generate-crl", params={
        "validity_days": validity_days,
        "hash_alg": hash_alg
    })


def get_activity_logs() -> list:
    """
    GET /api/admin/logs
    Returns: List[ActivityLogOut]
    """
    return _get("/api/admin/logs")
