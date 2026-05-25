from pathlib import Path
from typing import List, Union
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Project settings loaded from .env file using pydantic_settings"""
    
    model_config = ConfigDict(
        extra="ignore",  # Ignore extra fields from .env
        case_sensitive=True,
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8"
    )
    
    PROJECT_NAME: str = "X509 Certification System"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    CERTIFICATE_VALIDITY_DAYS: int = 365
    ALLOWED_ORIGINS: Union[str, List[str]] = "http://localhost:3000"  # Accept both string and list
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str
    
    ROOT_CA_PATH: str = "./root_ca"
    COUNTRY_NAME: str = "VN"
    STATE_OR_PROVINCE_NAME: str = "Hanoi"
    LOCALITY_NAME: str = "Hanoi"
    ORGANIZATION_NAME: str = "My CA"
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse comma-separated ALLOWED_ORIGINS string into list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

settings = Settings()
