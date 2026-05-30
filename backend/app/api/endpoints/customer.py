from typing import Any, List
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend
import datetime
import os
from cryptography import x509 as _x509
from cryptography.hazmat.backends import default_backend as _backend

from app.api import deps
from app.db import models
from app.schemas import certificate as schemas
from app.schemas import standards as standards_schemas
from app.core import crypto_utils

router = APIRouter()

@router.post("/save-public-key", response_model=standards_schemas.KeyManagementOut)
def save_public_key(
    req: standards_schemas.SavePublicKeyRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Store a public key that was generated client-side.

    The private key is kept exclusively on the client and is never sent here.
    This endpoint:
      1. Validates the PEM-encoded public key.
      2. Computes a SHA-256 fingerprint of the DER-encoded key.
      3. Saves a KeyManagement record (public key only) and returns it.
    """
    # ── Validate & parse the PEM public key ──────────────────────────────────
    try:
        public_key = load_pem_public_key(req.pubkey_pem.encode(), backend=default_backend())
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid public key PEM: {exc}"
        )

    # ── Fingerprint ──────────────────────────────────────────────────────────
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    pub_der = public_key.public_bytes(
        encoding=Encoding.DER,
        format=PublicFormat.SubjectPublicKeyInfo
    )
    fingerprint = hashlib.sha256(pub_der).hexdigest()

    # ── Persist ──────────────────────────────────────────────────────────────
    key_record = models.KeyManagement(
        user_id=current_user.id,
        algorithm=req.algorithm.upper(),
        key_size=req.key_size,
        pubkey_pem=req.pubkey_pem,
        fingerprint=fingerprint,
        description=req.description,
        status="active",
    )
    db.add(key_record)
    db.commit()
    db.refresh(key_record)

    deps.log_activity(
        db,
        action="PUBLIC_KEY_SAVED",
        details=(
            f"User {current_user.username} saved a {req.algorithm.upper()}-{req.key_size} "
            f"public key (fingerprint: {fingerprint[:16]}...)"
        ),
        user_id=current_user.id,
    )

    return key_record


@router.get("/my-keys", response_model=List[standards_schemas.KeyManagementOut])
def list_my_keys(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    List all generated key pairs for the current user.
    """
    return db.query(models.KeyManagement).filter(models.KeyManagement.user_id == current_user.id).all()


@router.post("/request-certificate", response_model=schemas.CertificateRequestOut, status_code=201)
def request_certificate(
    csr_data: schemas.CSRUpload,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Submit a CSR to request an X.509 certificate.

    Backend validation steps:
    1. Parse the PEM-encoded CSR.
    2. Verify the CSR self-signature (hash_A == hash_B):
       hash_A = digest of the TBSCertificationRequest body.
       hash_B = decrypted signature using the public key embedded in the CSR.
       This confirms the submitter owns the private key and the data was not tampered.
    3. If invalid → 400 (not saved to DB).
    4. If valid   → save as PENDING and return 201.
    """
    from cryptography import x509 as _x509
    from cryptography.hazmat.backends import default_backend as _backend
    from cryptography.exceptions import InvalidSignature

    # ── 1. Parse CSR ──────────────────────────────────────────────────────────
    try:
        csr = _x509.load_pem_x509_csr(csr_data.csr_pem.encode("utf-8"), _backend())
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid CSR format: cannot parse PEM data. ({e})"
        )

    # ── 2. Verify self-signature (hash_A == hash_B) ───────────────────────────
    if not csr.is_signature_valid:
        raise HTTPException(
            status_code=400,
            detail=(
                "CSR signature verification failed: the signature does not match the "
                "public key embedded in the CSR. "
                "Please ensure the CSR was signed with the correct private key."
            )
        )

    # ── 3. Save as PENDING ────────────────────────────────────────────────────
    cert_req = models.CertificateRequest(
        user_id=current_user.id,
        csr_pem=csr_data.csr_pem,
        status=models.CertStatus.PENDING
    )
    db.add(cert_req)
    db.commit()
    db.refresh(cert_req)

    deps.log_activity(
        db,
        action="CERTIFICATE_REQUESTED",
        details=f"CSR submitted by user {current_user.username}, RequestID: {cert_req.id}",
        user_id=current_user.id
    )

    return cert_req


@router.get("/my-requests", response_model=List[schemas.CertificateRequestOut])
def list_my_requests(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    List all certificate requests for the current user.
    """
    return db.query(models.CertificateRequest).filter(models.CertificateRequest.user_id == current_user.id).all()


@router.get("/my-certificates", response_model=List[schemas.CertificateOut])
def list_my_certificates(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    List all issued certificates for the current user.
    """
    return db.query(models.Certificate).filter(models.Certificate.user_id == current_user.id).all()


@router.get("/revoked-certificates", response_model=List[schemas.CertificateOut])
def list_revoked_certificates(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Return all REVOKED certificates in the system.
    This is public information equivalent to a CRL — any authenticated user
    may see which certificates have been revoked, for CRL inspection purposes.
    The cert_pem field is included so the client can ask the backend to parse it.
    """
    return (
        db.query(models.Certificate)
        .filter(models.Certificate.status == models.CertStatus.REVOKED)
        .all()
    )


@router.get("/certificates/{cert_id}/download")
def download_certificate(
    cert_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Download the certificate as a .crt file.
    """
    cert = db.query(models.Certificate).filter(
        models.Certificate.id == cert_id,
        models.Certificate.user_id == current_user.id
    ).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found or not owned by user")
    
    return Response(
        content=cert.cert_pem,
        media_type="application/x-pem-file",
        headers={"Content-Disposition": f"attachment; filename=certificate_{cert.serial_number}.crt"}
    )


@router.post("/certificates/{cert_id}/request-revoke", response_model=schemas.RevocationRequestOut)
def request_revoke_certificate(
    cert_id: int,
    req_data: schemas.RevocationRequestCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Request revocation of a certificate. Creates a request for admin to approve.
    """
    cert = db.query(models.Certificate).filter(models.Certificate.id == cert_id, models.Certificate.user_id == current_user.id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found or not owned by user")
    
    if cert.status != models.CertStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Certificate is not active")
        
    req = models.RevocationRequest(
        certificate_id=cert.id,
        user_id=current_user.id,
        reason=req_data.reason,
        status=models.CertStatus.PENDING
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.post("/parse-certificate")
def parse_uploaded_certificate(
    cert_data: schemas.CertificateUpload,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Upload and view information of any X.509 certificate.
    Returns browser-style structured info.
    """
    try:
        return crypto_utils.parse_certificate(cert_data.cert_pem)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid certificate format: {str(e)}")


@router.get("/certificates/{cert_id}/info")
def get_certificate_info(
    cert_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Parse a certificate and return browser-style structured info.
    The PEM is fetched on the backend — the client receives only the parsed fields.

    Own certificates: always accessible.
    Other users' certificates: accessible only if REVOKED (public CRL info).
    """
    cert = db.query(models.Certificate).filter(
        models.Certificate.id == cert_id,
    ).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    # Allow access to own certs OR any revoked cert (public CRL info)
    if cert.user_id != current_user.id and cert.status != models.CertStatus.REVOKED:
        raise HTTPException(status_code=403, detail="Access denied")
    try:
        return crypto_utils.parse_certificate(cert.cert_pem)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse certificate: {str(e)}")


@router.get("/crl")
def get_crl(db: Session = Depends(deps.get_db)) -> Any:
    """
    Get the current Certificate Revocation List (CRL) for the system.

    1. If the CRL file does not exist → 404.
    2. If the CRL file exists but has expired (next_update <= now) → regenerate it
       using the current revoked certificates list, then return the new CRL.
    3. If the CRL is still valid → return it directly from file.

    CRL lifetime is controlled by 'crl_lifetime_days' in system_config.
    Periodic regeneration is handled by the backend scheduler; this only acts
    as a safety net so clients never receive an already-expired CRL.
    """

    crl_path = crypto_utils.CRL_FILE_PATH

    if not os.path.exists(crl_path):
        raise HTTPException(
            status_code=404,
            detail=(
                "CRL file not found. The CA may not have been initialized yet. "
                "Please contact the administrator."
            )
        )

    try:
        with open(crl_path, "r", encoding="utf-8") as f:
            crl_pem = f.read()

        crl_obj = _x509.load_pem_x509_crl(crl_pem.encode("utf-8"), _backend())
        try:
            next_update = crl_obj.next_update_utc.replace(tzinfo=None)
        except AttributeError:
            next_update = crl_obj.next_update

        now = datetime.datetime.utcnow()

        if next_update <= now:
            crl_pem = crypto_utils.update_crl_cache(db)

        return {"crl_pem": crl_pem}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not retrieve CRL: " + str(e))


def parse_monitored_certificate(cert_pem: str) -> dict:
    """
    Parse a PEM certificate using the existing crypto_utils.parse_certificate function,
    suitable for UI display in Monitored Certificates.
    """

    try:
        # Leverage the existing parse_certificate function!
        parsed = crypto_utils.parse_certificate(cert_pem)
    except Exception as e:
        raise ValueError(f"Invalid certificate PEM format: {e}")

    # Map Issued To structured attributes to subject string
    to_attrs = parsed.get("Issued To", {})
    subject_parts = []
    if to_attrs.get("Common Name (CN)") != "<Not Part Of Certificate>":
        subject_parts.append(f"CN={to_attrs['Common Name (CN)']}")
    if to_attrs.get("Organization (O)") != "<Not Part Of Certificate>":
        subject_parts.append(f"O={to_attrs['Organization (O)']}")
    if to_attrs.get("Organizational Unit (OU)") != "<Not Part Of Certificate>":
        subject_parts.append(f"OU={to_attrs['Organizational Unit (OU)']}")
    subject_str = ",".join(subject_parts) if subject_parts else "CN=Unknown"

    # Map Issued By structured attributes to issuer string
    by_attrs = parsed.get("Issued By", {})
    issuer_parts = []
    if by_attrs.get("Common Name (CN)") != "<Not Part Of Certificate>":
        issuer_parts.append(f"CN={by_attrs['Common Name (CN)']}")
    if by_attrs.get("Organization (O)") != "<Not Part Of Certificate>":
        issuer_parts.append(f"O={by_attrs['Organization (O)']}")
    if by_attrs.get("Organizational Unit (OU)") != "<Not Part Of Certificate>":
        issuer_parts.append(f"OU={by_attrs['Organizational Unit (OU)']}")
    issuer_str = ",".join(issuer_parts) if issuer_parts else "CN=Unknown"

    serial_hex = parsed.get("Basic Details", {}).get("Serial Number", "Unknown")

    # Re-parse formatted dates using the exact matching format from parse_certificate
    date_fmt = "%A, %B %d, %Y at %I:%M:%S %p"
    try:
        issued_on_str = parsed.get("Validity Period", {}).get("Issued On", "")
        expires_on_str = parsed.get("Validity Period", {}).get("Expires On", "")
        not_before = datetime.datetime.strptime(issued_on_str, date_fmt)
        not_after = datetime.datetime.strptime(expires_on_str, date_fmt)
    except Exception as exc:
        raise ValueError(f"Failed to parse certificate dates: {exc}")

    status = "VALID" if not_after > datetime.datetime.utcnow() else "EXPIRED"

    return {
        "subject": subject_str,
        "issuer": issuer_str,
        "serial_number": serial_hex,
        "valid_from": not_before,
        "valid_to": not_after,
        "status": status
    }


@router.post("/monitored-certificates", response_model=schemas.MonitoredCertificateOut)
def upload_monitored_certificate(
    req: schemas.MonitoredCertificateCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Upload a certificate to monitor its validity.
    Validates PEM format, parses it on backend, and stores it in database.
    """
    try:
        parsed_fields = parse_monitored_certificate(req.cert_pem)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    monitored_cert = models.MonitoredCertificate(
        user_id=current_user.id,
        filename=req.filename,
        cert_pem=req.cert_pem
    )
    db.add(monitored_cert)
    db.commit()
    db.refresh(monitored_cert)

    deps.log_activity(
        db,
        action="MONITORED_CERTIFICATE_UPLOADED",
        details=f"Uploaded monitored certificate '{monitored_cert.filename}' (ID: {monitored_cert.id})",
        user_id=current_user.id
    )

    # Return output by combining database record fields and dynamically parsed fields
    return schemas.MonitoredCertificateOut(
        id=monitored_cert.id,
        user_id=monitored_cert.user_id,
        filename=monitored_cert.filename,
        cert_pem=monitored_cert.cert_pem,
        created_at=monitored_cert.created_at,
        **parsed_fields
    )


@router.get("/monitored-certificates", response_model=List[schemas.MonitoredCertificateOut])
def list_monitored_certificates(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    List all uploaded monitored certificates for the current user.
    Dynamic properties (subject, validity, status) are parsed live on demand.
    """
    certs = db.query(models.MonitoredCertificate).filter(
        models.MonitoredCertificate.user_id == current_user.id
    ).all()

    result = []
    for cert in certs:
        try:
            parsed_fields = parse_monitored_certificate(cert.cert_pem)
        except Exception:
            # Fallback values if certificate became unparseable
            from datetime import datetime
            parsed_fields = {
                "subject": "Unknown (Invalid Certificate)",
                "issuer": "Unknown (Invalid Certificate)",
                "serial_number": "Unknown",
                "valid_from": cert.created_at,
                "valid_to": cert.created_at,
                "status": "EXPIRED"
            }
        
        result.append(
            schemas.MonitoredCertificateOut(
                id=cert.id,
                user_id=cert.user_id,
                filename=cert.filename,
                cert_pem=cert.cert_pem,
                created_at=cert.created_at,
                **parsed_fields
            )
        )
    return result
