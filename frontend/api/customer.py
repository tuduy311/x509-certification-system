from .helpers import _get, _post, _put, BASE_URL



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

