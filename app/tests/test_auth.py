def test_register_success(client):
    """
    Тест 1: Успешная регистрация
    """
    response = client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "new@test.com",
            "password": "pass123456"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@test.com"
    assert data["balance"] == 1000.0
    assert "id" in data
    assert "created_at" in data


def test_register_duplicate_username(client):
    """
    Тест 2: Регистрация с существующим username
    """
    # Первая регистрация
    client.post(
        "/api/auth/register",
        json={
            "username": "user1",
            "email": "user1@test.com",
            "password": "pass123"
        }
    )
    
    # Попытка зарегистрировать того же username
    response = client.post(
        "/api/auth/register",
        json={
            "username": "user1",
            "email": "user2@test.com",
            "password": "pass123"
        }
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_register_duplicate_email(client):
    """
    Тест 3: Регистрация с существующим email
    """
    # Первая регистрация
    client.post(
        "/api/auth/register",
        json={
            "username": "user1",
            "email": "same@test.com",
            "password": "pass123"
        }
    )
    
    # Попытка с тем же email
    response = client.post(
        "/api/auth/register",
        json={
            "username": "user2",
            "email": "same@test.com",
            "password": "pass123"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client):
    """
    Тест 4: Успешный логин
    """
    # Регистрация
    client.post(
        "/api/auth/register",
        json={
            "username": "loginuser",
            "email": "login@test.com",
            "password": "pass123"
        }
    )
    
    # Логин
    response = client.post(
        "/api/auth/login",
        data={
            "username": "loginuser",
            "password": "pass123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """
    Тест 5: Логин с неверным паролем
    """
    # Регистрация
    client.post(
        "/api/auth/register",
        json={
            "username": "user",
            "email": "user@test.com",
            "password": "correct"
        }
    )
    
    # Логин с неверным паролем
    response = client.post(
        "/api/auth/login",
        data={
            "username": "user",
            "password": "wrong"
        }
    )
    
    assert response.status_code == 401


def test_get_me_authorized(auth_client):
    """
    Тест 6: Получение данных пользователя (авторизован)
    """
    response = auth_client.get("/api/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@test.com"


def test_get_me_unauthorized(client):
    """
    Тест 7: Получение данных без авторизации
    """
    response = client.get("/api/auth/me")
    
    assert response.status_code == 401