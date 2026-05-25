from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.core import security
from backend.app.core.config import settings
from backend.app.db.database import SessionLocal
from backend.app.db import models
from backend.app.schemas.user import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def is_token_blacklisted(db: Session, token: str) -> bool:
    """Check if token is in blacklist and hasn't expired naturally."""
    blacklist_entry = db.query(models.TokenBlacklist).filter(
        models.TokenBlacklist.token == token
    ).first()
    if blacklist_entry:
        # Only return True if token is still within its natural expiry time
        # After expiry, it's invalid anyway
        return blacklist_entry.expires_at > datetime.utcnow()
    return False

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Check if token is blacklisted (user logged out)
    if is_token_blacklisted(db, token):
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if current_user.role != models.Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user

def log_activity(db: Session, action: str, details: str = None, user_id: int = None):
    log = models.ActivityLog(user_id=user_id, action=action, details=details)
    db.add(log)
    db.commit()
