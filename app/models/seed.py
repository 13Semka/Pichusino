from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Seed(Base):
    """
    MODEL: Seed pair для Provably Fair системы
    """
    __tablename__ = "seeds"  # ✅ Таблица во множественном
    
    id = Column(Integer, primary_key=True, index=True)
    
    # К какому пользователю относится
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Server seed (секретный)
    server_seed = Column(String(128), nullable=False)
    
    # Хеш server seed (публичный)
    server_seed_hash = Column(String(64), nullable=False, index=True)
    
    # Client seed
    client_seed = Column(String(64), nullable=False)
    
    # Счётчик игр
    nonce = Column(Integer, default=0, nullable=False)
    
    # Активен ли
    active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Связи (единственное - ссылка на одного пользователя)
    user = relationship("User", back_populates="seeds")