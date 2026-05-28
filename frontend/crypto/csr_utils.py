"""
frontend/crypto/csr_utils.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Build a PKCS#10 Certificate Signing Request (CSR) entirely on the client.

The private key is supplied by the caller and NEVER leaves the frontend
process — it is not transmitted to the backend.
"""

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


def build_csr(subject_dict: dict, private_key_pem: str, hash_alg: str = "SHA256") -> str:
    """
    Build and sign a CSR locally using the provided private key.

    Parameters
    ----------
    subject_dict : dict
        Keys accepted: common_name (required), country, state, locality,
        organization, organizational_unit.
    private_key_pem : str
        PEM-encoded private key (RSA or ECC). Must match the public key
        that will be uploaded separately.
    hash_alg : str
        Digest algorithm for the CSR signature: SHA256 | SHA384 | SHA512.

    Returns
    -------
    str
        PEM-encoded CSR (-----BEGIN CERTIFICATE REQUEST-----...).

    Raises
    ------
    ValueError
        With a human-readable message on any failure so the UI can show it.
    """
    # ── Load private key ──────────────────────────────────────────────────────
    try:
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(), password=None, backend=default_backend()
        )
    except Exception as exc:
        raise ValueError(f"Invalid private key: {exc}") from exc

    # ── Hash algorithm ────────────────────────────────────────────────────────
    _hash_map = {
        "SHA256": hashes.SHA256(),
        "SHA384": hashes.SHA384(),
        "SHA512": hashes.SHA512(),
    }
    digest = _hash_map.get(hash_alg.upper(), hashes.SHA256())

    # ── Subject name ──────────────────────────────────────────────────────────
    name_attrs = []
    if subject_dict.get("country"):
        name_attrs.append(
            x509.NameAttribute(NameOID.COUNTRY_NAME, subject_dict["country"][:2].upper())
        )
    if subject_dict.get("state"):
        name_attrs.append(
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, subject_dict["state"])
        )
    if subject_dict.get("locality"):
        name_attrs.append(
            x509.NameAttribute(NameOID.LOCALITY_NAME, subject_dict["locality"])
        )
    if subject_dict.get("organization"):
        name_attrs.append(
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, subject_dict["organization"])
        )
    if subject_dict.get("organizational_unit"):
        name_attrs.append(
            x509.NameAttribute(
                NameOID.ORGANIZATIONAL_UNIT_NAME, subject_dict["organizational_unit"]
            )
        )
    if not subject_dict.get("common_name"):
        raise ValueError("Common Name (CN) is required.")
    name_attrs.append(
        x509.NameAttribute(NameOID.COMMON_NAME, subject_dict["common_name"])
    )

    # ── Build & sign ──────────────────────────────────────────────────────────
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(x509.Name(name_attrs))
        .sign(private_key, digest, default_backend())
    )

    return csr.public_bytes(serialization.Encoding.PEM).decode("utf-8")
