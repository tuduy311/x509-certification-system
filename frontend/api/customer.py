from .helpers import _get, _post, _put, BASE_URL



def save_public_key(
    algorithm: str,
    key_size: int,
    pubkey_pem: str,
    description: str | None = None,
) -> dict:
    """
    POST /api/customer/save-public-key
    Body: {"algorithm": str, "key_size": int, "pubkey_pem": str, "description": str|None}
    Returns: KeyManagementOut dict (public key record – no private key).

    The key pair must be generated on the client first (see frontend/crypto/key_utils.py).
    Only the public key is sent to the backend.
    """
    return _post("/api/customer/save-public-key", json={
        "algorithm": algorithm,
        "key_size": key_size,
        "pubkey_pem": pubkey_pem,
        "description": description,
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


def get_revoked_certificates() -> list:
    """
    GET /api/customer/revoked-certificates
    Returns: List[CertificateOut] — all REVOKED certs in the system (public CRL info).
    """
    return _get("/api/customer/revoked-certificates")


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


def get_certificate_info(cert_id: int) -> dict:
    """
    GET /api/customer/certificates/{cert_id}/info
    Returns: browser-style parsed certificate info (no PEM sent to client)
    """
    return _get(f"/api/customer/certificates/{cert_id}/info")


def get_crl() -> dict:
    """
    GET /api/customer/crl  (public – no auth needed, but sends if available)
    Returns: {"crl_pem": str}
    """
    return _get("/api/customer/crl")


def get_monitored_certificates() -> list:
    """
    GET /api/customer/monitored-certificates
    Returns: List[MonitoredCertificateOut]
    """
    return _get("/api/customer/monitored-certificates")


def upload_monitored_certificate(filename: str, cert_pem: str) -> dict:
    """
    POST /api/customer/monitored-certificates
    Body: {"filename": str, "cert_pem": str}
    Returns: MonitoredCertificateOut dict
    """
    return _post("/api/customer/monitored-certificates", json={
        "filename": filename,
        "cert_pem": cert_pem
    })

