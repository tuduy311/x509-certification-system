import os
import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from app.core.config import settings

ROOT_KEY_PATH = f"{settings.ROOT_CA_PATH}.key"
ROOT_CERT_PATH = f"{settings.ROOT_CA_PATH}.crt"

def generate_key_pair(key_size: int = 2048):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    return private_key

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

def generate_root_ca(key_size: int = 2048, validity_days: int = 3650, hash_alg: str = "SHA256"):
    private_key = generate_key_pair(key_size)
    public_key = private_key.public_key()
    
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, settings.COUNTRY_NAME),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, settings.STATE_OR_PROVINCE_NAME),
        x509.NameAttribute(NameOID.LOCALITY_NAME, settings.LOCALITY_NAME),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, settings.ORGANIZATION_NAME),
        x509.NameAttribute(NameOID.COMMON_NAME, u"Root CA"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        public_key
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=validity_days)
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True,
    ).sign(private_key, get_hash_algorithm(hash_alg), default_backend())
    
    # Save to files
    with open(ROOT_KEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
        
    with open(ROOT_CERT_PATH, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

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

def parse_certificate(cert_pem: str):
    cert = x509.load_pem_x509_certificate(cert_pem.encode("utf-8"), default_backend())
    subject = {attr.oid._name: attr.value for attr in cert.subject}
    issuer = {attr.oid._name: attr.value for attr in cert.issuer}

    # Dùng not_valid_before_utc / not_valid_after_utc (UTC-aware) thay vì
    # not_valid_before / not_valid_after (naive datetime - deprecated)
    try:
        not_before = cert.not_valid_before_utc
        not_after = cert.not_valid_after_utc
    except AttributeError:  # fallback cho cryptography phiên bản cũ
        not_before = cert.not_valid_before
        not_after = cert.not_valid_after

    return {
        "serial_number": str(cert.serial_number),
        "subject": subject,
        "issuer": issuer,
        "not_valid_before": not_before.isoformat(),
        "not_valid_after": not_after.isoformat()
    }

