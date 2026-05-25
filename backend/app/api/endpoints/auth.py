import re
from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from jose import jwt

from app.core import security
from app.core.config import settings
from app.db import models
from app.api import deps
from app.schemas import user as schemas

router = APIRouter()

def validate_password_strength(password: str) -> None:
    """Validate that password meets strength requirements."""
    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long."
        )
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter."
        )
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one lowercase letter."
        )
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one digit."
        )
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one special character."
        )

async def get_login_data(request: Request) -> schemas.LoginRequest:
    """Helper dependency to parse login credentials from either JSON or Form data."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            return schemas.LoginRequest(**body)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")
    else:
        try:
            form = await request.form()
            username = form.get("username")
            password = form.get("password")
            if not username or not password:
                raise Exception()
            return schemas.LoginRequest(username=str(username), password=str(password))
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid form data. Please provide username and password."
            )

@router.post("/login", response_model=schemas.Token)
def login_access_token(
    form_data: schemas.LoginRequest = Depends(get_login_data),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Supports both JSON and Form data.
    """
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        user.username, expires_delta=access_token_expires
    )
    
    deps.log_activity(db, action="USER_LOGIN", details=f"Username: {user.username}", user_id=user.id)
    
    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.post("/register", response_model=schemas.UserOut)
def register_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Register a new customer.
    """
    
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    validate_password_strength(user_in.password)
    
    hashed_password = security.get_password_hash(user_in.password)
    user = models.User(
        username=user_in.username,
        hashed_password=hashed_password,
        role=models.Role.CUSTOMER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    deps.log_activity(db, action="USER_REGISTERED", details=f"Username: {user.username}", user_id=user.id)
    return user

@router.put("/change-password", response_model=schemas.UserOut)
def change_password(
    pwd_in: schemas.PasswordChange,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Change user password securely.
    """
    print(pwd_in.old_password, current_user.hashed_password)
    if not security.verify_password(pwd_in.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")


    if pwd_in.new_password == pwd_in.old_password:
        raise HTTPException(
            status_code=400,
            detail="New password must be different from old password"
        )
        
    if pwd_in.new_password != pwd_in.confirm_new_password:
        raise HTTPException(
            status_code=400,
            detail="New password and confirmation password do not match"
        )
        
    validate_password_strength(pwd_in.new_password)
    
    hashed_password = security.get_password_hash(pwd_in.new_password)
    current_user.hashed_password = hashed_password
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    deps.log_activity(
        db,
        action="PASSWORD_CHANGED",
        details=f"Username: {current_user.username}",
        user_id=current_user.id
    )
    return current_user

@router.post("/logout")
def logout(
    token: str = Depends(deps.oauth2_scheme),
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Invalidate the current JWT token by adding it to the blacklist.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        exp = payload.get("exp")
        expires_at = datetime.utcfromtimestamp(exp)
    except Exception:
        expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    blacklist_entry = models.TokenBlacklist(
        token=token,
        user_id=current_user.id,
        expires_at=expires_at
    )
    db.add(blacklist_entry)
    db.commit()
    
    deps.log_activity(db, action="USER_LOGOUT", details=f"Username: {current_user.username}", user_id=current_user.id)
    return {"msg": "Successfully logged out"}

@router.get("/me", response_model=schemas.UserOut)
def get_current_user(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user profile.
    """
    return current_user
