from .helpers import _get, _post, _put, BASE_URL



# ─────────────────────────────────────────────────────────────────────────────
# Admin endpoints
# ─────────────────────────────────────────────────────────────────────────────

def generate_root_key(algo: str = "RSA", key_size: int = 2048) -> dict:
    """
    POST /api/admin/generate-root-key?algo=...&key_size=...
    Generates a Root CA private key and saves it to key_CA/ on the server.
    Returns: {"msg": str, "algorithm": str, "key_size": int}
    """
    return _post("/api/admin/generate-root-key", params={"algo": algo, "key_size": key_size})


def generate_root_cert(validity_days: int = 3650, hash_alg: str = "SHA256") -> dict:
    """
    POST /api/admin/generate-root-cert?validity_days=...&hash_alg=...
    Reads the existing key from key_CA/, generates a self-signed cert, saves to cert_CA/.
    Returns: {"msg": str, "validity_days": int, "hash_alg": str}
    """
    return _post("/api/admin/generate-root-cert", params={"validity_days": validity_days, "hash_alg": hash_alg})


def get_ca_status() -> dict:
    """
    GET /api/admin/ca-status
    Returns: {"key_exists": bool, "cert_exists": bool}
    """
    return _get("/api/admin/ca-status")


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


def reject_request(request_id: int, rejection_reason: str, rejection_details: str) -> dict:
    """
    POST /api/admin/requests/{request_id}/reject
    Returns: CertificateRequestOut dict
    """
    return _post(f"/api/admin/requests/{request_id}/reject", json={
        "rejection_reason": rejection_reason,
        "rejection_details": rejection_details
    })


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


def get_certificate_info(cert_id: int) -> dict:
    """
    GET /api/admin/certificates/{cert_id}/info
    Returns: browser-style parsed certificate info (no PEM sent to client).
    """
    return _get(f"/api/admin/certificates/{cert_id}/info")


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


def generate_crl(validity_days: int = 365, hash_alg: str = "SHA256") -> dict:
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
