from typing import Any, List
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend

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
    Get the latest Certificate Revocation List (CRL) for the system.
    Returns CRL PEM content directly from the file.
    Updates the file cache dynamically if expired (configured in system DB) or missing.
    """
    import os
    import time

    # 1. Fetch crl_update_days from DB
    cfg = db.query(models.SystemConfig).filter(models.SystemConfig.key == "crl_update_days").first()
    crl_update_days = int(cfg.value) if cfg else 30

    crl_path = crypto_utils.CRL_FILE_PATH
    need_regenerate = False

    # 2. Check if file exists and mtime check
    if not os.path.exists(crl_path):
        need_regenerate = True
    else:
        # Check mtime
        mtime = os.path.getmtime(crl_path)
        age_seconds = time.time() - mtime
        age_days = age_seconds / 86400.0
        if age_days >= crl_update_days:
            need_regenerate = True

    try:
        if need_regenerate:
            crl_pem = crypto_utils.update_crl_cache(db, validity_days=crl_update_days)
        else:
            with open(crl_path, "r", encoding="utf-8") as f:
                crl_pem = f.read()
        return {"crl_pem": crl_pem}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not retrieve CRL: " + str(e))



