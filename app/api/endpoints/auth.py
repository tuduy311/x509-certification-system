from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.db import models
from app.api import deps
from app.schemas import user as schemas

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
def login_access_token(
    form_data: schemas.LoginRequest,
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
    """
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
    return user

@router.put("/change-password", response_model=schemas.UserOut)
def change_password(
    new_password: str,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Change user password.
    """
    hashed_password = security.get_password_hash(new_password)
    current_user.hashed_password = hashed_password
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
