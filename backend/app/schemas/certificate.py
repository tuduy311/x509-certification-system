from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.models import CertStatus

class CSRCreate(BaseModel):
    common_name: str
    country: str = "VN"
    state: str = "Hanoi"
    locality: str = "Hanoi"
    organization: str = "My Organization"
    organizational_unit: str = "IT Department"

class CSRUpload(BaseModel):
    csr_pem: str

class CertificateRequestOut(BaseModel):
    id: int
    user_id: int
    csr_pem: str
    status: CertStatus
    rejection_reason: Optional[str] = None
    rejection_details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CertificateRequestReject(BaseModel):
    rejection_reason: str
    rejection_details: str

class CertificateOut(BaseModel):
    id: int
    request_id: Optional[int]
    user_id: int
    serial_number: str
    cert_pem: str
    status: CertStatus
    valid_from: datetime
    valid_to: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class ConfigUpdate(BaseModel):
    default_key_size: int
    default_validity_days: int
    hash_algorithm: str

class RevocationRequestCreate(BaseModel):
    reason: str

class RevocationRequestOut(BaseModel):
    id: int
    certificate_id: int
    user_id: int
    reason: str
    status: CertStatus
    created_at: datetime

    class Config:
        from_attributes = True

class ActivityLogOut(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    details: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class CertificateUpload(BaseModel):
    cert_pem: str

