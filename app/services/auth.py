from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

# =========================
# НАСТРОЙКИ БЕЗОПАСНОСТИ
# =========================

# Контекст для хеширования паролей (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 схема (говорит FastAPI где брать токен)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# =========================
# ФУНКЦИИ ДЛЯ ПАРОЛЕЙ
# =========================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверить пароль
    
    Args:
        plain_password: Пароль который ввёл пользователь
        hashed_password: Хеш из БД
    
    Returns:
        True если пароль правильный
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Захешировать пароль
    
    Args:
        password: Обычный пароль
    
    Returns:
        Хеш пароля для хранения в БД
    """
    return pwd_context.hash(password)

# =========================
# ФУНКЦИИ ДЛЯ JWT ТОКЕНОВ
# =========================

def create_access_token(data: dict) -> str:
    """
    Создать JWT токен
    
    Args:
        data: Данные для включения в токен (обычно {"sub": username})
    
    Returns:
        JWT токен строка
    """
    to_encode = data.copy()
    
    # Добавляем время истечения
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    
    # Кодируем токен
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Декодировать JWT токен
    
    Args:
        token: JWT токен строка
    
    Returns:
        Данные из токена
    
    Raises:
        JWTError: Если токен невалидный
    """
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    return payload

# =========================
# DEPENDENCY ДЛЯ ПОЛУЧЕНИЯ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ
# =========================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Получить текущего пользователя из JWT токена
    
    Эта функция используется как Dependency в защищённых endpoints:
    
    @app.get("/protected")
    def protected_route(current_user: User = Depends(get_current_user)):
        return {"user": current_user.username}
    
    Args:
        token: JWT токен из заголовка Authorization
        db: Сессия БД
    
    Returns:
        Объект User из БД
    
    Raises:
        HTTPException 401: Если токен невалидный или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Декодируем токен
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
    
    except JWTError:
        raise credentials_exception
    
    # Ищем пользователя в БД
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise credentials_exception
    
    return user

# =========================
# ФУНКЦИЯ ДЛЯ АУТЕНТИФИКАЦИИ
# =========================

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    Проверить username и пароль
    
    Args:
        db: Сессия БД
        username: Имя пользователя
        password: Пароль
    
    Returns:
        User если логин успешен, None если нет
    """
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user