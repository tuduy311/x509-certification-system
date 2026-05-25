from typing import Any, List
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives import serialization

from app.api import deps
from app.db import models
from app.schemas import certificate as schemas
from app.schemas import standards as standards_schemas
from app.core import crypto_utils

router = APIRouter()

@router.post("/generate-keys")
def generate_personal_keys(
    req: standards_schemas.KeyCreateRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Generate, save to DB, and return a new RSA/ECC public/private key pair.
    """
    try:
        private_key = crypto_utils.generate_key_pair(req.algorithm, req.key_size)
        
        # Serialize Private Key to PEM
        # TraditionalOpenSSL or PKCS8 depending on algorithm
        # For EC, PKCS8 is cleaner, but let's just use PKCS8 or TraditionalOpenSSL
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize Public Key to PEM
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Calculate public key fingerprint (SHA256 of DER)
        pub_der = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        fingerprint = hashlib.sha256(pub_der).hexdigest()
        
        # Save key record to DB
        key_record = models.KeyManagement(
            user_id=current_user.id,
            algorithm=req.algorithm.upper(),
            key_size=req.key_size,
            pubkey_pem=public_pem.decode('utf-8'),
            fingerprint=fingerprint,
            description=req.description,
            status="active"
        )
        db.add(key_record)
        db.commit()
        db.refresh(key_record)
        
        return {
            "private_key": private_pem.decode('utf-8'),
            "public_key": public_pem.decode('utf-8'),
            "key_record": standards_schemas.KeyManagementOut.from_orm(key_record)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate key pair: {str(e)}")

@router.get("/my-keys", response_model=List[standards_schemas.KeyManagementOut])
def list_my_keys(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    List all generated key pairs for the current user.
    """
    return db.query(models.KeyManagement).filter(models.KeyManagement.user_id == current_user.id).all()


@router.post("/request-certificate", response_model=schemas.CertificateRequestOut)
def request_certificate(
    csr_data: schemas.CSRUpload,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Submit a CSR to request an X.509 certificate.
    """
    # Simple validation if CSR is valid format could be added here
    cert_req = models.CertificateRequest(
        user_id=current_user.id,
        csr_pem=csr_data.csr_pem,
        status=models.CertStatus.PENDING
    )
    db.add(cert_req)
    db.commit()
    db.refresh(cert_req)
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
    """
    try:
        return crypto_utils.parse_certificate(cert_data.cert_pem)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid certificate format: {str(e)}")

@router.get("/crl")
def get_crl(db: Session = Depends(deps.get_db)) -> Any:
    """
    Get the latest Certificate Revocation List (CRL) for the system.
    """
    # This could be pre-generated by admin and stored, but for simplicity we generate on the fly or fetch the latest generated file.
    # To meet requirements, admin updates CRL (endpoint created), so let's just generate it on the fly here or say we read it.
    revoked_certs = db.query(models.Certificate).filter(models.Certificate.status == models.CertStatus.REVOKED).all()
    serials = [c.serial_number for c in revoked_certs]
    try:
        crl_pem = crypto_utils.generate_crl(serials)
        return {"crl_pem": crl_pem}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not generate CRL: " + str(e))
