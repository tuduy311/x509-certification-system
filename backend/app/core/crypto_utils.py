import os
import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from app.core.config import settings

_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_DIR = os.path.dirname(_CORE_DIR)
_BASE_DIR = os.path.dirname(_APP_DIR)

MANAGEMENT_DIR = os.path.join(_BASE_DIR, "Management")

os.makedirs(MANAGEMENT_DIR,  exist_ok=True)

KEY_CA_DIR  = os.path.join(MANAGEMENT_DIR, "key_CA")
CERT_CA_DIR = os.path.join(MANAGEMENT_DIR, "cert_CA")
CRL_DIR     = os.path.join(MANAGEMENT_DIR, "crl")

os.makedirs(KEY_CA_DIR,  exist_ok=True)
os.makedirs(CERT_CA_DIR, exist_ok=True)
os.makedirs(CRL_DIR,     exist_ok=True)

ROOT_KEY_PATH  = os.path.join(KEY_CA_DIR,  "root_ca.key")
ROOT_CERT_PATH = os.path.join(CERT_CA_DIR, "root_ca.crt")
CRL_FILE_PATH  = os.path.join(CRL_DIR, "crl.pem")

def generate_key_pair(algorithm: str | int = "RSA", key_size: int = 2048):
    algo = algorithm.upper()
    if algo == "ECC":
        if key_size == 256:
            curve = ec.SECP256R1()
        elif key_size == 384:
            curve = ec.SECP384R1()
        elif key_size == 521:
            curve = ec.SECP521R1()
        else:
            curve = ec.SECP256R1()
        return ec.generate_private_key(
            curve,
            backend=default_backend()
        )
    # Default is RSA
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )

def get_hash_algorithm(name: str):
    name = name.upper()
    if name == "SHA256":
        return hashes.SHA256()
    elif name == "SHA384":
        return hashes.SHA384()
    elif name == "SHA512":
        return hashes.SHA512()
    else:
        return hashes.SHA256()

def generate_root_ca_key(algo: str = "RSA", key_size: int = 2048) -> dict:
    """
    Generate a Root CA private key and save it to key_CA/root_ca.key.
    Returns a dict with status and file path info.
    """
    private_key = generate_key_pair(algo, key_size)

    with open(ROOT_KEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    return {
        "algorithm": algo.upper(),
        "key_size": key_size,
        "key_path": ROOT_KEY_PATH,
    }


def generate_root_ca_cert(validity_days: int = 3650, hash_alg: str = "SHA256") -> dict:
    """
    Read the existing Root CA private key from key_CA/root_ca.key,
    build a self-signed certificate, and save it to cert_CA/root_ca.crt.
    Raises FileNotFoundError if the key has not been generated yet.
    """
    if not os.path.exists(ROOT_KEY_PATH):
        raise FileNotFoundError(
            "Root CA private key not found. "
            "Please generate the key pair first via 'Generate Root Key Pair'."
        )

    with open(ROOT_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )

    public_key = private_key.public_key()

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, settings.COUNTRY_NAME),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, settings.STATE_OR_PROVINCE_NAME),
        x509.NameAttribute(NameOID.LOCALITY_NAME, settings.LOCALITY_NAME),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, settings.ORGANIZATION_NAME),
        x509.NameAttribute(NameOID.COMMON_NAME, u"Root CA"),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=validity_days))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(private_key, get_hash_algorithm(hash_alg), default_backend())
    )

    with open(ROOT_CERT_PATH, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    return {
        "cert_path": ROOT_CERT_PATH,
        "valid_days": validity_days,
        "hash_alg": hash_alg,
    }


def root_ca_key_exists() -> bool:
    """Check whether a root CA private key exists in key_CA/."""
    return os.path.exists(ROOT_KEY_PATH)

def root_ca_cert_exists() -> bool:
    """Check whether a root CA certificate exists in cert_CA/."""
    return os.path.exists(ROOT_CERT_PATH)

def get_root_ca():
    if not os.path.exists(ROOT_KEY_PATH) or not os.path.exists(ROOT_CERT_PATH):
        return None, None
    with open(ROOT_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
    with open(ROOT_CERT_PATH, "rb") as f:
        cert = x509.load_pem_x509_certificate(f.read(), default_backend())
        
    return private_key, cert

def generate_csr(private_key, subject_dict: dict, hash_alg: str = "SHA256"):
    subject_attributes = [
        x509.NameAttribute(NameOID.COUNTRY_NAME, subject_dict.get("country", settings.COUNTRY_NAME)),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, subject_dict.get("state", settings.STATE_OR_PROVINCE_NAME)),
        x509.NameAttribute(NameOID.LOCALITY_NAME, subject_dict.get("locality", settings.LOCALITY_NAME)),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, subject_dict.get("organization", settings.ORGANIZATION_NAME)),
        x509.NameAttribute(NameOID.COMMON_NAME, subject_dict.get("common_name")),
    ]
    if subject_dict.get("organizational_unit"):
        subject_attributes.append(
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, subject_dict.get("organizational_unit"))
        )
    
    csr = x509.CertificateSigningRequestBuilder().subject_name(
        x509.Name(subject_attributes)
    ).sign(private_key, get_hash_algorithm(hash_alg), default_backend())
    
    return csr.public_bytes(serialization.Encoding.PEM).decode("utf-8")

def sign_csr(csr_pem: str, validity_days: int = 365, hash_alg: str = "SHA256"):
    root_key, root_cert = get_root_ca()
    if not root_key or not root_cert:
        raise Exception("Root CA not found")
        
    csr = x509.load_pem_x509_csr(csr_pem.encode("utf-8"), default_backend())
    if not csr.is_signature_valid:
        raise Exception("CSR signature is invalid")
         
    cert = x509.CertificateBuilder().subject_name(
        csr.subject
    ).issuer_name(
        root_cert.subject
    ).public_key(
        csr.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=validity_days)
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True,
    ).sign(root_key, get_hash_algorithm(hash_alg), default_backend())
    
    return cert.public_bytes(serialization.Encoding.PEM).decode("utf-8"), str(cert.serial_number)

def generate_crl(revoked_certs_serials: list, validity_days: int = 30, hash_alg: str = "SHA256"):
    root_key, root_cert = get_root_ca()
    if not root_key or not root_cert:
        raise Exception("Root CA not found")
        
    builder = x509.CertificateRevocationListBuilder().issuer_name(
        root_cert.subject
    ).last_update(
        datetime.datetime.utcnow()
    ).next_update(
        datetime.datetime.utcnow() + datetime.timedelta(days=validity_days)
    )
    
    for serial in revoked_certs_serials:
        revoked_cert = x509.RevokedCertificateBuilder().serial_number(
            int(serial)
        ).revocation_date(
            datetime.datetime.utcnow()
        ).build()
        builder = builder.add_revoked_certificate(revoked_cert)
        
    crl = builder.sign(
        private_key=root_key, algorithm=get_hash_algorithm(hash_alg),
        backend=default_backend()
    )
    return crl.public_bytes(serialization.Encoding.PEM).decode("utf-8")

def _get_name_attributes(name_obj) -> dict:
    """Extract CN, O, OU from a Name object. Returns '<Not Part Of Certificate>' when missing."""
    from cryptography.x509.oid import NameOID as _NameOID
    def _get(oid):
        attrs = name_obj.get_attributes_for_oid(oid)
        return attrs[0].value if attrs else "<Not Part Of Certificate>"
    return {
        "Common Name (CN)": _get(_NameOID.COMMON_NAME),
        "Organization (O)": _get(_NameOID.ORGANIZATION_NAME),
        "Organizational Unit (OU)": _get(_NameOID.ORGANIZATIONAL_UNIT_NAME),
    }


def parse_certificate(cert_pem: str) -> dict:
    """
    Parse a PEM certificate and return a browser-style structured dict:
      - Basic Details   (Version, Serial Number)
      - Issued To       (CN, O, OU of subject)
      - Issued By       (CN, O, OU of issuer)
      - Validity Period (Issued On, Expires On)
      - SHA-256 Fingerprints (Certificate, Public Key)
    """
    cert = x509.load_pem_x509_certificate(cert_pem.encode("utf-8"), default_backend())

    # Date format: "Saturday, May 09, 2026 at 06:52:00 AM"
    fmt = lambda dt: dt.strftime("%A, %B %d, %Y at %I:%M:%S %p")

    # Certificate fingerprint (SHA-256 of the full DER)
    cert_fp = cert.fingerprint(hashes.SHA256()).hex()

    # Public key fingerprint (SHA-256 of SPKI DER)
    pub_der = cert.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    pubkey_fp = hashes.Hash(hashes.SHA256())
    pubkey_fp.update(pub_der)
    pubkey_fp = pubkey_fp.finalize().hex()

    # Serial number — uppercase hex, no "0x" prefix
    serial_hex = hex(cert.serial_number).upper().replace("0X", "")

    # Try to read validity dates (UTC-aware or naive)
    try:
        not_before = cert.not_valid_before_utc
        not_after  = cert.not_valid_after_utc
    except AttributeError:
        # cryptography < 42 fallback
        not_before = cert.not_valid_before
        not_after  = cert.not_valid_after

    return {
        "Basic Details": {
            "Version": cert.version.name.upper(),
            "Serial Number": serial_hex,
        },
        "Issued To": _get_name_attributes(cert.subject),
        "Issued By": _get_name_attributes(cert.issuer),
        "Validity Period": {
            "Issued On":  fmt(not_before),
            "Expires On": fmt(not_after),
        },
        "SHA-256 Fingerprints": {
            "Certificate": cert_fp,
            "Public Key":  pubkey_fp,
        },
    }


def write_crl_file(crl_pem: str):
    """Write the CRL PEM string to Management/crl/crl.pem file."""
    with open(CRL_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(crl_pem)


def update_crl_cache(db, validity_days: int = None, hash_alg: str = None) -> str:
    """
    Fetch all revoked certificates from the database, generate a new CRL,
    save it to Management/crl/crl.pem and return the PEM string.
    """
    from app.db import models
    
    if validity_days is None:
        cfg = db.query(models.SystemConfig).filter(models.SystemConfig.key == "crl_lifetime_days").first()
        validity_days = int(cfg.value) if cfg else 30
    if hash_alg is None:
        cfg = db.query(models.SystemConfig).filter(models.SystemConfig.key == "hash_algorithm").first()
        hash_alg = cfg.value if cfg else "SHA256"
        
    revoked_certs = db.query(models.Certificate).filter(models.Certificate.status == models.CertStatus.REVOKED).all()
    serials = [c.serial_number for c in revoked_certs]
    
    crl_pem = generate_crl(serials, validity_days, hash_alg)
    write_crl_file(crl_pem)
    return crl_pem


