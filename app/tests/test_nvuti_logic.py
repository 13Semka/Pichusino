from app.services.nvuti_service import NvutiService


def test_calculate_result_deterministic():
    """
    Тест 16: Результат детерминированный (одинаковые входы = одинаковый выход)
    """
    service = NvutiService(None)
    
    # Одинаковые параметры
    result1 = service.calculate_result("test_server", "test_client", 0)
    result2 = service.calculate_result("test_server", "test_client", 0)
    
    assert result1 == result2


def test_calculate_result_different_nonce():
    """
    Тест 17: Разные nonce дают разные результаты
    """
    service = NvutiService(None)
    
    result1 = service.calculate_result("test_server", "test_client", 0)
    result2 = service.calculate_result("test_server", "test_client", 1)
    
    assert result1 != result2


def test_calculate_result_range():
    """
    Тест 18: Результат в диапазоне 0-99.99
    """
    service = NvutiService(None)
    
    for nonce in range(100):
        result = service.calculate_result("test_server", "test_client", nonce)
        assert 0 <= result <= 99.99


def test_calculate_multiplier():
    """
    Тест 19: Проверка множителя
    """
    service = NvutiService(None)
    
    # 50% шанс → 1.90x
    assert service.calculate_multiplier(50.0) == 1.9
    
    # 10% шанс → 9.50x
    assert service.calculate_multiplier(10.0) == 9.5
    
    # 95% шанс → 1.00x
    assert service.calculate_multiplier(95.0) == 1.0


def test_balance_updates_correctly(auth_client, db):
    """
    Тест 20: Баланс обновляется правильно
    """
    from app.models.user import User
    
    # Получаем начальный баланс
    user = db.query(User).filter(User.username == "testuser").first()
    initial_balance = user.balance
    
    # Делаем ставку
    response = auth_client.post(
        "/api/games/nvuti/bet",
        json={"win_chance": 50.0, "amount": 10.0}
    )
    
    data = response.json()
    profit_loss = data["profit_loss"]
    
    # Проверяем баланс
    db.refresh(user)
    assert user.balance == initial_balance + profit_loss
    assert user.balance == data["new_balance"]