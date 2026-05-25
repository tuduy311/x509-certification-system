from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api import deps
from app.db import models
from app.schemas import certificate as schemas
from app.core import crypto_utils

router = APIRouter()

# ─────────────────────────────────────────────
# Helper: đọc giá trị cấu hình từ DB, fallback về default nếu chưa thiết lập
# ─────────────────────────────────────────────
def _get_config_value(db: Session, key: str, default):
    """
    Đọc giá trị cấu hình hệ thống từ bảng system_config.
    Nếu chưa có thì dùng giá trị mặc định (default).
    """
    config = db.query(models.SystemConfig).filter(models.SystemConfig.key == key).first()
    if config and config.value:
        try:
            return type(default)(config.value)
        except (ValueError, TypeError):
            return default
    return default


# ─────────────────────────────────────────────
# A.4 + A.5 — Phát sinh cặp khoá Root CA + Root Certificate
# ─────────────────────────────────────────────
@router.post("/setup-root-ca", response_model=dict)
def setup_root_ca(
    key_size: int = 2048,
    validity_days: int = 3650,
    hash_alg: str = "SHA256",
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    [A.4] Phát sinh cặp khoá Public/Private cho Root CA.
    [A.5] Phát sinh Root Certificate cho toàn hệ thống.
    Hai bước được thực hiện cùng nhau trong một lệnh PKI chuẩn.
    """
    try:
        crypto_utils.generate_root_ca(key_size, validity_days, hash_alg)

        # [THÊM] Log hoạt động tạo Root CA
        deps.log_activity(
            db=db,
            action="ROOT_CA_GENERATED",
            details=f"Admin generated Root CA: key_size={key_size}, validity={validity_days} days, hash={hash_alg}",
            user_id=current_user.id
        )

        return {"msg": "Root CA generated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────
# Xem danh sách tất cả yêu cầu cấp chứng nhận
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# A.7 — Phê duyệt và phát sinh chứng nhận X.509
# [SỬA] Dùng config DB nếu không truyền tham số; thêm logging
# ─────────────────────────────────────────────
@router.post("/requests/{request_id}/approve", response_model=schemas.CertificateOut)
def approve_request(
    request_id: int,
    validity_days: Optional[int] = None,   # None → đọc từ config DB
    hash_alg: Optional[str] = None,         # None → đọc từ config DB
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    [A.7] Approve a CSR and issue an X.509 certificate.
    Nếu không truyền validity_days / hash_alg, hệ thống dùng giá trị
    đã thiết lập trong Admin Config (A.3). Fallback: 365 ngày / SHA256.
    """
    cert_req = db.query(models.CertificateRequest).filter(
        models.CertificateRequest.id == request_id
    ).first()
    if not cert_req:
        raise HTTPException(status_code=404, detail="Request not found")
    if cert_req.status != models.CertStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already processed")

    # [SỬA] Áp dụng config hệ thống nếu tham số không được cung cấp
    if validity_days is None:
        validity_days = _get_config_value(db, "default_validity_days", 365)
    if hash_alg is None:
        hash_alg = _get_config_value(db, "hash_algorithm", "SHA256")

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

    # [THÊM] Log hoạt động duyệt chứng nhận
    deps.log_activity(
        db=db,
        action="CERTIFICATE_APPROVED",
        details=f"Admin approved request #{request_id}, issued certificate serial={serial_num}, valid={validity_days} days",
        user_id=current_user.id
    )

    return cert

# ─────────────────────────────────────────────
# A.6 — Từ chối yêu cầu cấp chứng nhận
# [SỬA] Thêm logging
# ─────────────────────────────────────────────
@router.post("/requests/{request_id}/reject", response_model=schemas.CertificateRequestOut)
def reject_request(
    request_id: int,
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    [A.6] Reject a certificate request.
    """
    cert_req = db.query(models.CertificateRequest).filter(
        models.CertificateRequest.id == request_id
    ).first()
    if not cert_req:
        raise HTTPException(status_code=404, detail="Request not found")

    cert_req.status = models.CertStatus.REJECTED
    db.add(cert_req)
    db.commit()
    db.refresh(cert_req)

    # [THÊM] Log hoạt động từ chối
    deps.log_activity(
        db=db,
        action="CERTIFICATE_REJECTED",
        details=f"Admin rejected certificate request #{request_id}",
        user_id=current_user.id
    )

    return cert_req

# ─────────────────────────────────────────────
# A.8 — Revoke chứng nhận trực tiếp (không cần customer yêu cầu)
# [SỬA] Thêm logging
# ─────────────────────────────────────────────
@router.post("/certificates/{cert_id}/revoke", response_model=schemas.CertificateOut)
def revoke_certificate(
    cert_id: int,
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    [A.8] Revoke an active certificate directly (admin action, no customer request needed).
    """
    cert = db.query(models.Certificate).filter(models.Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if cert.status == models.CertStatus.REVOKED:
        raise HTTPException(status_code=400, detail="Certificate is already revoked")

    cert.status = models.CertStatus.REVOKED
    db.add(cert)
    db.commit()
    db.refresh(cert)

    # [THÊM] Log hoạt động thu hồi
    deps.log_activity(
        db=db,
        action="CERTIFICATE_REVOKED",
        details=f"Admin directly revoked certificate_id={cert_id}, serial={cert.serial_number}",
        user_id=current_user.id
    )

    return cert

# ─────────────────────────────────────────────
# A.3 — Xem cấu hình hệ thống
# ─────────────────────────────────────────────
@router.get("/config")
def get_config(
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    [A.3] Get system configurations (key_size, validity_days, hash_algorithm, ...).
    """
    configs = db.query(models.SystemConfig).all()
    return {c.key: c.value for c in configs}

# ─────────────────────────────────────────────
# A.3 — Thiết lập thông số kỹ thuật chuẩn
# [SỬA] Thêm logging
# ─────────────────────────────────────────────
@router.put("/config")
def update_config(
    key: str,
    value: str,
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    [A.3] Update a technical parameter.
    Supported keys: default_key_size, default_validity_days, hash_algorithm
    """
    config = db.query(models.SystemConfig).filter(models.SystemConfig.key == key).first()
    if config:
        config.value = value
    else:
        config = models.SystemConfig(key=key, value=value)
    db.add(config)
    db.commit()

    # [THÊM] Log hoạt động cập nhật cấu hình
    deps.log_activity(
        db=db,
        action="CONFIG_UPDATED",
        details=f"Admin updated system config: {key} = {value}",
        user_id=current_user.id
    )

    return {"msg": f"Configuration '{key}' updated to '{value}' successfully"}

# ─────────────────────────────────────────────
# A.9 — Xem danh sách yêu cầu thu hồi chứng nhận
# ─────────────────────────────────────────────
@router.get("/revocation-requests", response_model=List[schemas.RevocationRequestOut])
def list_revocation_requests(
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """[A.9] List all certificate revocation requests from customers."""
    return db.query(models.RevocationRequest).all()

# ─────────────────────────────────────────────
# A.9 — Phê duyệt yêu cầu thu hồi chứng nhận
# [SỬA] Thêm logging
# ─────────────────────────────────────────────
@router.post("/revocation-requests/{req_id}/approve", response_model=schemas.CertificateOut)
def approve_revocation_request(
    req_id: int,
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """[A.9] Approve revocation request — marks certificate as REVOKED."""
    req = db.query(models.RevocationRequest).filter(
        models.RevocationRequest.id == req_id
    ).first()
    if not req or req.status != models.CertStatus.PENDING:
        raise HTTPException(status_code=400, detail="Invalid or already processed request")

    cert = db.query(models.Certificate).filter(
        models.Certificate.id == req.certificate_id
    ).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    req.status = models.CertStatus.APPROVED
    cert.status = models.CertStatus.REVOKED
    db.add(req)
    db.add(cert)
    db.commit()
    db.refresh(cert)

    # [THÊM] Log hoạt động phê duyệt thu hồi
    deps.log_activity(
        db=db,
        action="REVOCATION_APPROVED",
        details=f"Admin approved revocation request #{req_id}, certificate_id={cert.id} is now REVOKED",
        user_id=current_user.id
    )

    return cert

# ─────────────────────────────────────────────
# [THÊM MỚI] A.9 — Từ chối yêu cầu thu hồi chứng nhận
# Trước đây chỉ có approve, thiếu reject
# ─────────────────────────────────────────────
@router.post("/revocation-requests/{req_id}/reject", response_model=schemas.RevocationRequestOut)
def reject_revocation_request(
    req_id: int,
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    [A.9] Reject a certificate revocation request.
    Certificate remains APPROVED/active. The revocation request is marked REJECTED.
    """
    req = db.query(models.RevocationRequest).filter(
        models.RevocationRequest.id == req_id
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Revocation request not found")
    if req.status != models.CertStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already processed")

    req.status = models.CertStatus.REJECTED
    db.add(req)
    db.commit()
    db.refresh(req)

    # Log hoạt động
    deps.log_activity(
        db=db,
        action="REVOCATION_REJECTED",
        details=f"Admin rejected revocation request #{req_id} for certificate_id={req.certificate_id}",
        user_id=current_user.id
    )

    return req

# ─────────────────────────────────────────────
# A.10 — Cập nhật danh sách thu hồi CRL
# [SỬA] Thêm logging
# ─────────────────────────────────────────────
@router.post("/generate-crl")
def generate_crl_endpoint(
    validity_days: int = 30,
    hash_alg: str = "SHA256",
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """[A.10] Generate CRL from all revoked certificates."""
    revoked_certs = db.query(models.Certificate).filter(
        models.Certificate.status == models.CertStatus.REVOKED
    ).all()
    serials = [c.serial_number for c in revoked_certs]
    try:
        crl_pem = crypto_utils.generate_crl(serials, validity_days, hash_alg)

        # [THÊM] Log hoạt động tạo CRL
        deps.log_activity(
            db=db,
            action="CRL_GENERATED",
            details=f"Admin generated CRL with {len(serials)} revoked certificates",
            user_id=current_user.id
        )

        return {"crl_pem": crl_pem}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────
# A.11 — Theo dõi nhật ký hoạt động hệ thống
# ─────────────────────────────────────────────
@router.get("/logs", response_model=List[schemas.ActivityLogOut])
def view_logs(
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db),
    limit: int = 100
) -> Any:
    """[A.11] View system activity logs, ordered by most recent."""
    return db.query(models.ActivityLog).order_by(
        models.ActivityLog.created_at.desc()
    ).limit(limit).all()

# ─────────────────────────────────────────────
# A.8 — Phê duyệt yêu cầu gia hạn (renew) chứng nhận
# [SỬA] Áp dụng config DB + logging
# ─────────────────────────────────────────────
@router.post("/requests/{request_id}/approve-renewal", response_model=schemas.CertificateOut)
def approve_renewal_request(
    request_id: int,
    validity_days: Optional[int] = None,   # None → đọc từ config DB
    hash_alg: Optional[str] = None,         # None → đọc từ config DB
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    [A.8] Approve a certificate renewal request and issue the renewed certificate.
    Nếu không truyền tham số, hệ thống tự động dùng config đã thiết lập ở A.3.
    """
    cert_req = db.query(models.CertificateRequest).filter(
        models.CertificateRequest.id == request_id
    ).first()
    if not cert_req:
        raise HTTPException(status_code=404, detail="Request not found")
    if cert_req.status != models.CertStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already processed")

    # [SỬA] Áp dụng config hệ thống nếu không truyền tham số
    if validity_days is None:
        validity_days = _get_config_value(db, "default_validity_days", 365)
    if hash_alg is None:
        hash_alg = _get_config_value(db, "hash_algorithm", "SHA256")

    try:
        cert_pem, serial_num = crypto_utils.sign_csr(cert_req.csr_pem, validity_days, hash_alg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    cert_req.status = models.CertStatus.APPROVED

    renewed_cert = models.Certificate(
        request_id=cert_req.id,
        user_id=cert_req.user_id,
        serial_number=serial_num,
        cert_pem=cert_pem,
        status=models.CertStatus.APPROVED,
        valid_from=datetime.utcnow(),
        valid_to=datetime.utcnow() + timedelta(days=validity_days)
    )
    db.add(renewed_cert)
    db.add(cert_req)
    db.commit()
    db.refresh(renewed_cert)

    # Log the activity
    deps.log_activity(
        db=db,
        action="CERTIFICATE_RENEWAL_APPROVED",
        details=f"Admin approved renewal request #{request_id}, issued new certificate serial={serial_num}",
        user_id=current_user.id
    )

    return renewed_cert

# ─────────────────────────────────────────────
# A.8 — Từ chối yêu cầu gia hạn chứng nhận
# ─────────────────────────────────────────────
@router.post("/requests/{request_id}/reject-renewal", response_model=schemas.CertificateRequestOut)
def reject_renewal_request(
    request_id: int,
    current_user: models.User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    [A.8] Reject a certificate renewal request.
    """
    cert_req = db.query(models.CertificateRequest).filter(
        models.CertificateRequest.id == request_id
    ).first()
    if not cert_req:
        raise HTTPException(status_code=404, detail="Request not found")

    cert_req.status = models.CertStatus.REJECTED
    db.add(cert_req)
    db.commit()
    db.refresh(cert_req)

    # Log the activity
    deps.log_activity(
        db=db,
        action="CERTIFICATE_RENEWAL_REJECTED",
        details=f"Admin rejected renewal request #{request_id}",
        user_id=current_user.id
    )

    return cert_req
