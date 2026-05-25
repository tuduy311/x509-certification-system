from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api import deps
from app.db import models
from app.schemas import certificate as schemas
from app.schemas import standards as standards_schemas
from app.core import crypto_utils

router = APIRouter()

@router.post("/setup-root-ca", response_model=dict)
def setup_root_ca(
    key_size: int = 2048,
    validity_days: int = 3650,
    hash_alg: str = "SHA256",
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Generate Root Certificate and Keys.
    """
    try:
        crypto_utils.generate_root_ca(key_size, validity_days, hash_alg)
        return {"msg": "Root CA generated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/requests", response_model=List[schemas.CertificateRequestOut])
def list_requests(
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    List all certificate requests.
    """
    requests = db.query(models.CertificateRequest).offset(skip).limit(limit).all()
    return requests

@router.post("/requests/{request_id}/approve", response_model=schemas.CertificateOut)
def approve_request(
    request_id: int,
    validity_days: int = 365,
    hash_alg: str = "SHA256",
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Approve a CSR and issue an X.509 certificate.
    """
    cert_req = db.query(models.CertificateRequest).filter(models.CertificateRequest.id == request_id).first()
    if not cert_req:
        raise HTTPException(status_code=404, detail="Request not found")
    if cert_req.status != models.CertStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already processed")

    try:
        cert_pem, serial_num = crypto_utils.sign_csr(cert_req.csr_pem, validity_days, hash_alg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    cert_req.status = models.CertStatus.APPROVED
    
    cert = models.Certificate(
        request_id=cert_req.id,
        user_id=cert_req.user_id,
        serial_number=serial_num,
        cert_pem=cert_pem,
        status=models.CertStatus.APPROVED,
        valid_from=datetime.utcnow(),
        valid_to=datetime.utcnow() + timedelta(days=validity_days)
    )
    db.add(cert)
    db.add(cert_req)
    db.commit()
    db.refresh(cert)
    return cert

@router.post("/requests/{request_id}/reject", response_model=schemas.CertificateRequestOut)
def reject_request(
    request_id: int,
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Reject a certificate request.
    """
    cert_req = db.query(models.CertificateRequest).filter(models.CertificateRequest.id == request_id).first()
    if not cert_req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    cert_req.status = models.CertStatus.REJECTED
    db.add(cert_req)
    db.commit()
    db.refresh(cert_req)
    return cert_req

@router.post("/certificates/{cert_id}/revoke", response_model=schemas.CertificateOut)
def revoke_certificate(
    cert_id: int,
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Revoke an active certificate.
    """
    cert = db.query(models.Certificate).filter(models.Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    cert.status = models.CertStatus.REVOKED
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert

# =========================================================================
@router.get("/certificates", response_model=List[schemas.CertificateOut])
def list_all_certificates(
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 200
) -> Any:
    """
    List all issued X.509 certificates in the system (admin only).
    """
    return db.query(models.Certificate).offset(skip).limit(limit).all()
# =========================================================================

@router.get("/config")
def get_config(
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """Get system configurations."""
    configs = db.query(models.SystemConfig).all()
    return {c.key: c.value for c in configs}

@router.put("/config")
def update_config(
    key: str,
    value: str,
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """Update a technical parameter."""
    config = db.query(models.SystemConfig).filter(models.SystemConfig.key == key).first()
    if config:
        config.value = value
    else:
        config = models.SystemConfig(key=key, value=value)
    db.add(config)
    db.commit()
    return {"msg": "Configuration updated successfully"}

@router.post("/config/reset")
def reset_config_to_defaults(
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """Reset all system configurations to their default values in database."""
    configs = db.query(models.SystemConfig).all()
    for c in configs:
        if c.default_value is not None:
            c.value = c.default_value
    db.commit()
    return {"msg": "Configuration reset to defaults successfully"}

@router.get("/options/asymmetric-algorithms", response_model=List[standards_schemas.AsymmetricAlgorithmOut])
def list_asymmetric_algorithms(
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """List asymmetric algorithms available."""
    return db.query(models.AsymmetricAlgorithm).filter(models.AsymmetricAlgorithm.is_active == True).all()

@router.get("/options/hash-algorithms", response_model=List[standards_schemas.HashAlgorithmOut])
def list_hash_algorithms(
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """List hash algorithms available."""
    return db.query(models.HashAlgorithm).filter(models.HashAlgorithm.is_active == True).all()

@router.get("/options/key-lengths", response_model=List[standards_schemas.KeyLengthOut])
def list_key_lengths(
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """List key lengths available."""
    return db.query(models.KeyLength).filter(models.KeyLength.is_active == True).all()

@router.get("/options/validity-options", response_model=List[standards_schemas.ValidityOptionOut])
def list_validity_options(
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """List validity period options available."""
    return db.query(models.ValidityOption).filter(models.ValidityOption.is_active == True).all()


@router.get("/revocation-requests", response_model=List[schemas.RevocationRequestOut])
def list_revocation_requests(
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """List certificate revocation requests."""
    return db.query(models.RevocationRequest).all()

@router.post("/revocation-requests/{req_id}/approve", response_model=schemas.CertificateOut)
def approve_revocation_request(
    req_id: int,
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """Approve revocation request."""
    req = db.query(models.RevocationRequest).filter(models.RevocationRequest.id == req_id).first()
    if not req or req.status != models.CertStatus.PENDING:
        raise HTTPException(status_code=400, detail="Invalid request")
    
    cert = db.query(models.Certificate).filter(models.Certificate.id == req.certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
        
    req.status = models.CertStatus.APPROVED
    cert.status = models.CertStatus.REVOKED
    db.add(req)
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert

# =========================================================================
@router.post("/revocation-requests/{req_id}/reject", response_model=schemas.RevocationRequestOut)
def reject_revocation_request(
    req_id: int,
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """Reject a revocation request (keep certificate active)."""
    req = db.query(models.RevocationRequest).filter(models.RevocationRequest.id == req_id).first()
    if not req or req.status != models.CertStatus.PENDING:
        raise HTTPException(status_code=400, detail="Invalid or already-processed request")
    req.status = models.CertStatus.REJECTED
    db.add(req)
    db.commit()
    db.refresh(req)
    return req

@router.post("/certificates/{cert_id}/renew", response_model=schemas.CertificateOut)
def renew_certificate(
    cert_id: int,
    validity_days: int = 365,
    hash_alg: str = "SHA256",
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Renew a certificate by re-signing its original CSR with a new validity period.
    Creates a new Certificate record; the old certificate stays as-is.
    """
    cert = db.query(models.Certificate).filter(models.Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    # Re-use the original CSR from the linked request if available
    if not cert.request_id:
        raise HTTPException(status_code=400, detail="No original CSR found for this certificate")
    cert_req = db.query(models.CertificateRequest).filter(
        models.CertificateRequest.id == cert.request_id
    ).first()
    if not cert_req:
        raise HTTPException(status_code=404, detail="Original CSR request not found")

    try:
        cert_pem, serial_num = crypto_utils.sign_csr(cert_req.csr_pem, validity_days, hash_alg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    new_cert = models.Certificate(
        request_id=cert_req.id,
        user_id=cert.user_id,
        serial_number=serial_num,
        cert_pem=cert_pem,
        status=models.CertStatus.APPROVED,
        valid_from=datetime.utcnow(),
        valid_to=datetime.utcnow() + timedelta(days=validity_days)
    )
    db.add(new_cert)
    db.commit()
    db.refresh(new_cert)
    return new_cert
# =========================================================================

@router.post("/generate-crl")
def generate_crl_endpoint(
    validity_days: int = 30,
    hash_alg: str = "SHA256",
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """Generate CRL from revoked certificates."""
    revoked_certs = db.query(models.Certificate).filter(models.Certificate.status == models.CertStatus.REVOKED).all()
    serials = [c.serial_number for c in revoked_certs]
    try:
        crl_pem = crypto_utils.generate_crl(serials, validity_days, hash_alg)
        return {"crl_pem": crl_pem}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs", response_model=List[schemas.ActivityLogOut])
def view_logs(
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """View system activity logs."""
    return db.query(models.ActivityLog).order_by(models.ActivityLog.created_at.desc()).limit(100).all()
