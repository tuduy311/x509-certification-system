"""
frontend/crypto/key_utils.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Client-side RSA/ECC key-pair generation.

The private key is generated and kept in the frontend process.
Only the **public key** is ever sent to the backend for storage.
"""

from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


def generate_key_pair(algorithm: str = "RSA", key_size: int = 2048):
    """
    Generate an RSA or ECC private key object locally.

    Parameters
    ----------
    algorithm : str
        "RSA" or "ECC".
    key_size : int
        For RSA: 2048 | 3072 | 4096.
        For ECC: 256 | 384 | 521 (maps to NIST P-curves).

    Returns
    -------
    cryptography private-key object (RSAPrivateKey or EllipticCurvePrivateKey)
    """
    algo = algorithm.upper()
    if algo == "ECC":
        curve_map = {
            256: ec.SECP256R1(),
            384: ec.SECP384R1(),
            521: ec.SECP521R1(),
        }
        curve = curve_map.get(key_size, ec.SECP256R1())
        return ec.generate_private_key(curve, backend=default_backend())

    # Default → RSA
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend(),
    )


def serialize_keys(private_key) -> tuple[str, str]:
    """
    Serialize a private-key object to PEM strings.

    Returns
    -------
    (private_key_pem, public_key_pem) : tuple[str, str]
        Both values are UTF-8 PEM strings.
    """
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    return private_pem, public_pem
