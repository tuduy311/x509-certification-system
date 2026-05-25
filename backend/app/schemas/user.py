from pydantic import BaseModel
from typing import Optional
from backend.app.db.models import Role

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

# [THÊM MỚI] Schema để đổi mật khẩu qua request body (an toàn hơn query param)
class PasswordChange(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str

class UserOut(UserBase):
    id: int
    role: Role
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
