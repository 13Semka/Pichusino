from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth import (
    get_password_hash,
    create_access_token,
    authenticate_user,
    get_current_user
)

# Настройка логирования
logger = logging.getLogger(__name__)

# Создание роутера
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

# =========================
# ENDPOINTS
# =========================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя
    
    - Проверяет уникальность username и email
    - Хеширует пароль
    - Создаёт пользователя с начальным балансом 1000
    """
    # Проверка существования username
    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Проверка существования email
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Создание пользователя
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        balance=1000.0  # Начальный баланс
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"New user registered: {user.username}")
    
    return user

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Логин (получение JWT токена)
    
    - Проверяет username и пароль
    - Возвращает JWT токен для использования в защищённых endpoints
    
    Используй токен так:
    Authorization: Bearer <token>
    """
    # Аутентификация
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создание токена
    access_token = create_access_token(data={"sub": user.username})
    
    logger.info(f"User logged in: {user.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о текущем пользователе
    
    Требует авторизации (JWT токен)
    """
    return current_user

@router.get("/test-protected")
def test_protected(
    current_user: User = Depends(get_current_user)
):
    """
    Тестовый защищённый endpoint
    
    Требует авторизации
    """
    return {
        "message": f"Hello, {current_user.username}!",
        "balance": current_user.balance
    }