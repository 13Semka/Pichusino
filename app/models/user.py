from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    """
    MODEL: Пользователь
    """
    __tablename__ = "users"  # ✅ Таблица во множественном
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Данные для входа
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Игровые данные
    balance = Column(Float, default=1000.0)
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи (множественное число для коллекций)
    bets = relationship("Bet", back_populates="user")
    seeds = relationship("Seed", back_populates="user")