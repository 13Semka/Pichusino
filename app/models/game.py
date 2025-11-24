from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Game(Base):
    """
    MODEL: Игра (Nvuti, Slot и т.д.)
    """
    __tablename__ = "games"  # ✅ Таблица во множественном
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Название и тип
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    
    # Настройки игры
    house_edge = Column(Float, nullable=False)
    min_bet = Column(Float, default=1.0)
    max_bet = Column(Float, default=1000.0)
    
    # Описание правил
    rules = Column(Text, nullable=True)
    
    # Связи
    bets = relationship("Bet", back_populates="game")