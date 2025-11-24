import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.game import Game

# Тестовая БД в памяти (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """
    Fixture для тестовой БД
    Создаёт все таблицы, даёт сессию, потом удаляет всё
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Добавляем тестовую игру Nvuti
    game = Game(
        name="Nvuti",
        type="dice",
        house_edge=5.0,
        min_bet=1.0,
        max_bet=1000.0,
        rules="Test game"
    )
    db.add(game)
    db.commit()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """
    Fixture для HTTP клиента
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client, db):
    """
    Fixture для авторизованного клиента
    Создаёт пользователя и возвращает клиент с токеном
    """
    # Регистрация
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@test.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 201
    
    # Логин
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Устанавливаем токен в заголовки
    client.headers = {"Authorization": f"Bearer {token}"}
    
    return client