from datetime import timedelta, datetime
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from backend.app.core import security
from backend.app.core.config import settings
from backend.app.db import models
from backend.app.api import deps
from backend.app.schemas import user as schemas

router = APIRouter()

# ─────────────────────────────────────────────
# Helper: Validate password strength
# ─────────────────────────────────────────────
def validate_password_strength(password: str) -> None:
    """
    Validate password meets minimum security requirements.
    Requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character (!@#$%^&*)
    """
    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long"
        )
    
    if not any(c.isupper() for c in password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 1 uppercase letter"
        )
    
    if not any(c.islower() for c in password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 1 lowercase letter"
        )
    
    if not any(c.isdigit() for c in password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 1 digit (0-9)"
        )
    
    special_chars = "!@#$%^&*()"
    if not any(c in special_chars for c in password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 1 special character (!@#$%^&*)"
        )

# ─────────────────────────────────────────────
# Helper: Support both JSON and Form (for Swagger UI /docs Authorize button)
# ─────────────────────────────────────────────
async def get_login_data(
    request: Request,
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
) -> schemas.LoginRequest:
    """
    Dependency to support login via both application/json (API clients/tests)
    and application/x-www-form-urlencoded (Swagger UI Authorize button).
    """
    if "application/json" in request.headers.get("content-type", "").lower():
        try:
            body = await request.json()
            return schemas.LoginRequest(**body)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
            
    if username is not None and password is not None:
        return schemas.LoginRequest(username=username, password=password)
        
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Login credentials must be provided as JSON or Form data"
    )

@router.post("/login", response_model=schemas.Token)
def login_access_token(
    form_data: schemas.LoginRequest = Depends(get_login_data),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # [THÊM] Log hoạt động đăng nhập
    deps.log_activity(db=db, action="USER_LOGIN", details=f"User '{user.username}' logged in", user_id=user.id)

    return {
        "access_token": security.create_access_token(
            user.username, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=schemas.UserOut)
def register_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Register a new customer.
    Password must meet security requirements (min 8 chars, uppercase, lowercase, digit, special char).
    """
    # Validate password strength
    validate_password_strength(user_in.password)
    
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    hashed_password = security.get_password_hash(user_in.password)
    user = models.User(
        username=user_in.username,
        hashed_password=hashed_password,
        role=models.Role.CUSTOMER
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # [THÊM] Log hoạt động đăng ký
    deps.log_activity(db=db, action="USER_REGISTERED", details=f"New customer '{user.username}' registered", user_id=user.id)

    return user

# [SỬA] Nhận mật khẩu mới qua request body (schemas.PasswordChange) thay vì query param
# Lý do: Query param làm lộ mật khẩu trong URL, server log, và browser history
@router.put("/change-password", response_model=schemas.UserOut)
def change_password(
    pwd_data: schemas.PasswordChange,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Change user password. Password is sent in request body (not query param) for security.
    Body: { "new_password": "..." }
    New password must meet security requirements.
    """
    # 1. XÁC THỰC MẬT KHẨU CŨ
    if not security.verify_password(pwd_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu cũ không chính xác."
        )
    
    # 2. Kiểm tra mật khẩu mới có trùng mật khẩu cũ không (Optional nhưng nên có)
    if pwd_data.old_password == pwd_data.new_password:
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu mới không được trùng với mật khẩu cũ."
        )
    #3. Validate new password
    if pwd_data.new_password != pwd_data.confirm_new_password:
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu mới không khớp với mật khẩu xác nhận."
        )
    # Validate password strength
    validate_password_strength(pwd_data.new_password)
    
    hashed_password = security.get_password_hash(pwd_data.new_password)
    current_user.hashed_password = hashed_password
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    # [THÊM] Log hoạt động đổi mật khẩu
    deps.log_activity(db=db, action="PASSWORD_CHANGED", details=f"User '{current_user.username}' changed password", user_id=current_user.id)

    return current_user

# ─────────────────────────────────────────────
# [THÊM MỚI] Logout endpoint - invalidate token
# ─────────────────────────────────────────────
@router.post("/logout")
def logout(
    current_user: models.User = Depends(deps.get_current_active_user),
    token: str = Depends(deps.oauth2_scheme),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Logout endpoint. Blacklist the current JWT token to prevent reuse.
    This invalidates the token immediately even before natural expiry.
    """
    try:
        # Decode token to get expiry time
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            token_expiry = datetime.utcfromtimestamp(exp_timestamp)
        else:
            # Fallback: use default expiry
            token_expiry = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Add token to blacklist
        blacklist_entry = models.TokenBlacklist(
            token=token,
            user_id=current_user.id,
            expires_at=token_expiry
        )
        db.add(blacklist_entry)
        db.commit()
        
        # Log the logout activity
        deps.log_activity(
            db=db,
            action="USER_LOGOUT",
            details=f"User '{current_user.username}' logged out",
            user_id=current_user.id
        )
        
        return {"msg": "Successfully logged out", "detail": "Token has been blacklisted"}
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
