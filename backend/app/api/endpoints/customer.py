from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives import serialization

from backend.app.api import deps
from backend.app.db import models
from backend.app.schemas import certificate as schemas
from backend.app.core import crypto_utils

router = APIRouter()

# ─────────────────────────────────────────────
# B.4 — Phát sinh cặp khoá Public/Private cá nhân
# ─────────────────────────────────────────────
@router.get("/generate-keys")
def generate_personal_keys(
    key_size: int = 2048,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Generate and return a new RSA public/private key pair.
    """
    private_key = crypto_utils.generate_key_pair(key_size)

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return {
        "private_key": private_pem.decode('utf-8'),
        "public_key": public_pem.decode('utf-8')
    }

# ─────────────────────────────────────────────
# [THÊM MỚI] B.5 — Tự động sinh CSR từ thông tin form (common_name, org, country…)
# Trước đây customer phải tự tạo CSR bên ngoài, nay hệ thống hỗ trợ sinh CSR từ form
# Endpoint trả về: private_key (PEM) + csr_pem để customer submit tiếp
# ─────────────────────────────────────────────
@router.post("/generate-csr", response_model=schemas.CSRGenerateResponse)
def generate_csr_from_form(
    csr_data: schemas.CSRCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Tự động sinh cặp khoá RSA và CSR từ thông tin đăng ký (tên miền, tổ chức...).
    Trả về private_key và csr_pem để customer lưu private key và nộp csr_pem.
    
    Body:
    - common_name: Tên miền website (VD: example.com)
    - country: Quốc gia (VD: VN)
    - state: Tỉnh/thành phố
    - locality: Quận/huyện
    - organization: Tên tổ chức / cá nhân
    - organizational_unit: Phòng ban (không bắt buộc)
    """
    # Sinh cặp khoá RSA mới
    private_key = crypto_utils.generate_key_pair(key_size=2048)

    # Sinh CSR từ thông tin form
    subject_dict = {
        "common_name": csr_data.common_name,
        "country": csr_data.country,
        "state": csr_data.state,
        "locality": csr_data.locality,
        "organization": csr_data.organization,
    }
    csr_pem = crypto_utils.generate_csr(private_key, subject_dict)

    # Lấy private key dạng PEM để trả về cho customer lưu
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")

    # Log hoạt động
    deps.log_activity(
        db=db,
        action="CSR_GENERATED",
        details=f"User '{current_user.username}' generated CSR for domain '{csr_data.common_name}'",
        user_id=current_user.id
    )

    return {"private_key": private_pem, "csr_pem": csr_pem}


# ─────────────────────────────────────────────
# B.5 — Nộp CSR để xin cấp phát chứng nhận X.509
# ─────────────────────────────────────────────
@router.post("/request-certificate", response_model=schemas.CertificateRequestOut)
def request_certificate(
    csr_data: schemas.CSRUpload,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Submit a CSR PEM string to request an X.509 certificate.
    """
    cert_req = models.CertificateRequest(
        user_id=current_user.id,
        csr_pem=csr_data.csr_pem,
        status=models.CertStatus.PENDING
    )
    db.add(cert_req)
    db.commit()
    db.refresh(cert_req)

    # [THÊM] Log hoạt động nộp CSR
    deps.log_activity(
        db=db,
        action="CERTIFICATE_REQUESTED",
        details=f"User '{current_user.username}' submitted a CSR (request_id={cert_req.id})",
        user_id=current_user.id
    )

    return cert_req

# ─────────────────────────────────────────────
# B.6 — Xem danh sách yêu cầu cấp phát chứng nhận
# ─────────────────────────────────────────────
@router.get("/my-requests", response_model=List[schemas.CertificateRequestOut])
def list_my_requests(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    List all certificate requests for the current user.
    """
    return db.query(models.CertificateRequest).filter(models.CertificateRequest.user_id == current_user.id).all()

# ─────────────────────────────────────────────
# B.6 — Xem danh sách chứng nhận đã được cấp
# ─────────────────────────────────────────────
@router.get("/my-certificates", response_model=List[schemas.CertificateOut])
def list_my_certificates(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    List all issued certificates for the current user.
    """
    return db.query(models.Certificate).filter(models.Certificate.user_id == current_user.id).all()

# ─────────────────────────────────────────────
# [THÊM MỚI] B.6 — Tải về file chứng nhận .crt
# Trước đây chỉ trả JSON, nay có thể tải về file .crt thực sự
# ─────────────────────────────────────────────
@router.get("/certificates/{cert_id}/download")
def download_certificate(
    cert_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Tải về file chứng nhận X.509 dạng .crt (PEM format).
    Chỉ owner của chứng nhận mới có quyền tải.
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
        headers={
            "Content-Disposition": f"attachment; filename=certificate_{cert_id}.crt"
        }
    )

# ─────────────────────────────────────────────
# B.7 — Yêu cầu thu hồi chứng nhận
# ─────────────────────────────────────────────
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
    cert = db.query(models.Certificate).filter(
        models.Certificate.id == cert_id,
        models.Certificate.user_id == current_user.id
    ).first()
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

    # [THÊM] Log hoạt động yêu cầu thu hồi
    deps.log_activity(
        db=db,
        action="REVOCATION_REQUESTED",
        details=f"User '{current_user.username}' requested revocation of certificate_id={cert_id}, reason: {req_data.reason}",
        user_id=current_user.id
    )

    return req


# ─────────────────────────────────────────────
# Renew chứng nhận
# ─────────────────────────────────────────────
@router.post("/certificates/{cert_id}/renew", response_model=schemas.CertificateRequestOut)
def request_certificate_renewal(
    cert_id: int,
    renewal_data: schemas.CSRUpload = None,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Request renewal of an existing certificate.
    - If CSR is provided in body, use it for renewal
    - Otherwise, reuse the original CSR from the certificate request
    - Creates a new CertificateRequest for Admin to approve
    - Only works for APPROVED certificates (not revoked)
    """
    # 1. Kiểm tra chứng nhận tồn tại và quyền sở hữu
    cert = db.query(models.Certificate).filter(
        models.Certificate.id == cert_id,
        models.Certificate.user_id == current_user.id
    ).first()

    if not cert:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found or not owned by user"
        )

    # 2. Kiểm tra trạng thái (không cho phép renew nếu bị thu hồi)
    if cert.status == models.CertStatus.REVOKED:
        raise HTTPException(
            status_code=400,
            detail="Cannot renew a revoked certificate"
        )

    # 3. Xác định CSR sẽ dùng cho renewal
    if renewal_data and renewal_data.csr_pem:
        # Sử dụng CSR mới từ request body
        csr_to_use = renewal_data.csr_pem
    else:
        # Sử dụng CSR gốc từ original certificate request
        original_request = db.query(models.CertificateRequest).filter(
            models.CertificateRequest.id == cert.request_id
        ).first()

        if not original_request:
            raise HTTPException(
                status_code=400,
                detail="Original CSR not found for renewal"
            )
        csr_to_use = original_request.csr_pem

    # 4. Tạo renewal request mới
    renewal_request = models.CertificateRequest(
        user_id=current_user.id,
        csr_pem=csr_to_use,
        status=models.CertStatus.PENDING
    )
    db.add(renewal_request)
    db.commit()
    db.refresh(renewal_request)

    # Log the activity
    deps.log_activity(
        db=db,
        action="CERTIFICATE_RENEWAL_REQUESTED",
        details=f"User requested renewal for certificate ID {cert_id}",
        user_id=current_user.id
    )

    return renewal_request


# ─────────────────────────────────────────────
# B.9 — Upload chứng nhận bất kỳ để xem thông tin
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# B.8 — Tra cứu CRL toàn hệ thống (không cần auth — đúng chuẩn PKI public)
# ─────────────────────────────────────────────
@router.get("/crl")
def get_crl(db: Session = Depends(deps.get_db)) -> Any:
    """
    Get the latest Certificate Revocation List (CRL) for the system.
    This endpoint is public (no auth required) as per PKI standards.
    """
    revoked_certs = db.query(models.Certificate).filter(
        models.Certificate.status == models.CertStatus.REVOKED
    ).all()
    serials = [c.serial_number for c in revoked_certs]
    try:
        crl_pem = crypto_utils.generate_crl(serials)
        return {"crl_pem": crl_pem}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not generate CRL: " + str(e))
