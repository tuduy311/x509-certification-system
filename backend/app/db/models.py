from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base

class Role(str, enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"

class CertStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"
    EXPIRED = "expired"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(Role), default=Role.CUSTOMER)
    is_active = Column(Boolean, default=True)
    
    certificate_requests = relationship("CertificateRequest", back_populates="owner")
    certificates = relationship("Certificate", back_populates="owner")

class CertificateRequest(Base):
    __tablename__ = "certificate_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    csr_pem = Column(Text)
    status = Column(Enum(CertStatus), default=CertStatus.PENDING)
    rejection_reason = Column(String, nullable=True)
    rejection_details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="certificate_requests")
    certificate = relationship("Certificate", back_populates="request", uselist=False)

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("certificate_requests.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    serial_number = Column(String, unique=True, index=True)
    cert_pem = Column(Text)
    status = Column(Enum(CertStatus), default=CertStatus.APPROVED)
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="certificates")
    request = relationship("CertificateRequest", back_populates="certificate")

class SystemConfig(Base):
    __tablename__ = "system_config"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)
    default_value = Column(String, nullable=True)

class AsymmetricAlgorithm(Base):
    __tablename__ = "asymmetric_algorithms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)

class HashAlgorithm(Base):
    __tablename__ = "hash_algorithms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)

class KeyLength(Base):
    __tablename__ = "key_lengths"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, index=True)
    algo_name = Column(String, index=True) # "RSA" or "ECC"
    is_active = Column(Boolean, default=True)

class ValidityOption(Base):
    __tablename__ = "validity_options"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, unique=True, index=True)
    is_active = Column(Boolean, default=True)

class KeyManagement(Base):
    __tablename__ = "key_management"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    algorithm = Column(String)
    key_size = Column(Integer)
    pubkey_pem = Column(Text)
    fingerprint = Column(String, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="active")

    owner = relationship("User")

class RevocationRequest(Base):
    __tablename__ = "revocation_requests"
    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(Integer, ForeignKey("certificates.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    reason = Column(String)
    status = Column(Enum(CertStatus), default=CertStatus.PENDING) # PENDING, APPROVED, REJECTED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    certificate = relationship("Certificate")
    user = relationship("User")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime, nullable=False)


