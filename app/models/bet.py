from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Bet(Base):
    """
    MODEL: Ставка (история игр)
    """
    __tablename__ = "bets"  # ✅ Таблица во множественном
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Связи
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    
    # Данные ставки
    amount = Column(Float, nullable=False)
    
    # Результат
    result = Column(String(20), nullable=False)  # "win", "loss"
    profit_loss = Column(Float, nullable=False)
    
    # Детали игры (JSON)
    game_data = Column(Text, nullable=True)
    
    # Время
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Связи (единственное - ссылки на один объект)
    user = relationship("User", back_populates="bets")
    game = relationship("Game", back_populates="bets")