from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AsymmetricAlgorithmOut(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True

class HashAlgorithmOut(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True

class KeyLengthOut(BaseModel):
    id: int
    value: int
    algo_name: str
    is_active: bool

    class Config:
        from_attributes = True

class ValidityOptionOut(BaseModel):
    id: int
    value: int
    is_active: bool

    class Config:
        from_attributes = True

class KeyManagementOut(BaseModel):
    id: int
    user_id: int
    algorithm: str
    key_size: int
    pubkey_pem: str
    fingerprint: str
    description: Optional[str] = None
    created_at: datetime
    status: str

    class Config:
        from_attributes = True

class KeyCreateRequest(BaseModel):
    algorithm: str
    key_size: int
    description: Optional[str] = None

class SavePublicKeyRequest(BaseModel):
    """Payload for /save-public-key: key pair was generated on the client."""
    algorithm: str
    key_size: int
    pubkey_pem: str
    description: Optional[str] = None

class AllOptionsOut(BaseModel):
    asymmetric_algorithms: list[AsymmetricAlgorithmOut]
    hash_algorithms: list[HashAlgorithmOut]
    key_lengths: list[KeyLengthOut]
    validity_options: list[ValidityOptionOut]

