def test_play_nvuti_success(auth_client):
    """
    Тест 8: Успешная игра в Nvuti
    """
    response = auth_client.post(
        "/api/games/nvuti/bet",
        json={
            "win_chance": 50.0,
            "amount": 10.0
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Проверка структуры ответа
    assert "bet_id" in data
    assert "result_number" in data
    assert "is_win" in data
    assert "multiplier" in data
    assert "new_balance" in data
    
    # Проверка значений
    assert data["win_chance"] == 50.0
    assert data["multiplier"] == 1.9
    assert 0 <= data["result_number"] <= 99.99
    
    # Проверка Provably Fair данных
    assert "server_seed_hash" in data
    assert "client_seed" in data
    assert "nonce" in data


def test_play_nvuti_insufficient_balance(auth_client):
    """
    Тест 9: Ставка больше баланса
    """
    response = auth_client.post(
        "/api/games/nvuti/bet",
        json={
            "win_chance": 50.0,
            "amount": 10000.0  # Больше начального баланса 1000
        }
    )
    
    assert response.status_code == 400
    assert "insufficient" in response.json()["detail"].lower()


def test_play_nvuti_invalid_win_chance_too_low(auth_client):
    """
    Тест 10: Шанс выигрыша слишком низкий
    """
    response = auth_client.post(
        "/api/games/nvuti/bet",
        json={
            "win_chance": 0.5,  # Меньше 1
            "amount": 10.0
        }
    )
    
    assert response.status_code == 422  # Pydantic validation error


def test_play_nvuti_invalid_win_chance_too_high(auth_client):
    """
    Тест 11: Шанс выигрыша слишком высокий
    """
    response = auth_client.post(
        "/api/games/nvuti/bet",
        json={
            "win_chance": 96.0,  # Больше 95
            "amount": 10.0
        }
    )
    
    assert response.status_code == 422


def test_play_nvuti_negative_amount(auth_client):
    """
    Тест 12: Отрицательная ставка
    """
    response = auth_client.post(
        "/api/games/nvuti/bet",
        json={
            "win_chance": 50.0,
            "amount": -10.0
        }
    )
    
    assert response.status_code == 422


def test_get_seed_info(auth_client):
    """
    Тест 13: Получение информации о seed
    """
    response = auth_client.get("/api/games/nvuti/seed")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "server_seed_hash" in data
    assert "client_seed" in data
    assert "nonce" in data
    assert data["nonce"] == 0  # Первый seed


def test_rotate_seed(auth_client):
    """
    Тест 14: Смена seed
    """
    # Сначала сыграем
    auth_client.post(
        "/api/games/nvuti/bet",
        json={"win_chance": 50.0, "amount": 10.0}
    )
    
    # Смена seed
    response = auth_client.post("/api/games/nvuti/seed/rotate", json={})
    
    assert response.status_code == 200
    data = response.json()
    
    # Проверка что старый seed раскрыт
    assert "previous_server_seed" in data
    assert data["previous_server_seed"] is not None
    
    # Проверка нового seed
    assert "new_server_seed_hash" in data
    assert "new_client_seed" in data


def test_list_games(auth_client):
    """
    Тест 15: Список игр
    """
    response = auth_client.get("/api/games/")
    
    assert response.status_code == 200
    games = response.json()
    
    assert len(games) > 0
    assert games[0]["name"] == "Nvuti"
    assert games[0]["type"] == "dice"