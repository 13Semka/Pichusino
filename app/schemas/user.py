from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    """
    Схема для регистрации нового пользователя
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    """
    Схема для логина (на самом деле используется OAuth2PasswordRequestForm)
    """
    username: str
    password: str

class UserResponse(BaseModel):
    """
    Схема для ответа (НЕ включает пароль!)
    """
    id: int
    username: str
    email: str
    balance: float
    created_at: datetime
    
    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy

class Token(BaseModel):
    """
    Схема для JWT токена
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Данные внутри JWT токена
    """
    username: str | None = None