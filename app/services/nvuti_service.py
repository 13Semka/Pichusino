import secrets
import hashlib
import hmac
import json
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.seed import Seed
from app.models.user import User
from app.models.bet import Bet
from app.models.game import Game


class NvutiService:
    """
    CONTROLLER: Логика игры Nvuti с Provably Fair
    
    Nvuti - игра где игрок выбирает шанс выигрыша (1-95%)
    Результат генерируется криптографически (Provably Fair)
    """
    
    # Константы игры
    HOUSE_EDGE = 5.0  # Преимущество казино 5%
    MIN_WIN_CHANCE = 1.0
    MAX_WIN_CHANCE = 95.0
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================
    # PROVABLY FAIR ФУНКЦИИ
    # =========================
    
    def get_or_create_active_seed(self, user_id: int) -> Seed:
        """
        Получить активный seed pair или создать новый
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Активный Seed объект
        """
        # Ищем активный seed
        seed = self.db.query(Seed).filter(
            Seed.user_id == user_id,
            Seed.active == True
        ).first()
        
        if seed:
            return seed
        
        # Создаём новый seed pair
        server_seed = secrets.token_hex(32)  # 64 символа
        server_seed_hash = hashlib.sha256(server_seed.encode()).hexdigest()
        client_seed = secrets.token_hex(16)  # 32 символа
        
        new_seed = Seed(
            user_id=user_id,
            server_seed=server_seed,
            server_seed_hash=server_seed_hash,
            client_seed=client_seed,
            nonce=0,
            active=True
        )
        
        self.db.add(new_seed)
        self.db.commit()
        self.db.refresh(new_seed)
        
        return new_seed
    
    def calculate_result(self, server_seed: str, client_seed: str, nonce: int) -> float:
        """
        Вычислить результат игры (Provably Fair алгоритм)
        
        Алгоритм:
        1. Создаём HMAC-SHA256 из server_seed, client_seed, nonce
        2. Берём первые 8 hex символов
        3. Конвертируем в число 0-9999
        4. Делим на 100 → получаем 0.00 - 99.99
        
        Args:
            server_seed: Серверный seed
            client_seed: Клиентский seed
            nonce: Номер игры
        
        Returns:
            Число от 0.00 до 99.99
        """
        # Создаём HMAC
        hmac_result = hmac.new(
            key=server_seed.encode('utf-8'),
            msg=f"{client_seed}:{nonce}".encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Берём первые 8 символов
        hex_part = hmac_result[:8]
        
        # Конвертируем в число
        decimal = int(hex_part, 16)
        
        # Результат 0.00 - 99.99
        result = (decimal % 10000) / 100.0
        
        return round(result, 2)
    
    def calculate_multiplier(self, win_chance: float) -> float:
        """
        Рассчитать множитель выплаты
        
        Формула: (100 - house_edge) / win_chance
        
        Примеры:
        - 50% шанс → (100 - 5) / 50 = 1.90x
        - 10% шанс → 95 / 10 = 9.50x
        - 90% шанс → 95 / 90 = 1.06x
        
        Args:
            win_chance: Шанс выигрыша (1-95%)
        
        Returns:
            Множитель выплаты
        """
        return round((100 - self.HOUSE_EDGE) / win_chance, 2)
    
    # =========================
    # ИГРОВАЯ ЛОГИКА
    # =========================
    
    def play(self, user_id: int, game_id: int, bet_amount: float, win_chance: float) -> dict:
        """
        Сыграть раунд Nvuti
        
        Args:
            user_id: ID пользователя
            game_id: ID игры (из таблицы games)
            bet_amount: Размер ставки
            win_chance: Шанс выигрыша (1-95%)
        
        Returns:
            Результат игры со всеми данными
        
        Raises:
            ValueError: Если валидация не прошла
        """
        # Валидация шанса выигрыша
        if not (self.MIN_WIN_CHANCE <= win_chance <= self.MAX_WIN_CHANCE):
            raise ValueError(
                f"Win chance must be between {self.MIN_WIN_CHANCE} and {self.MAX_WIN_CHANCE}"
            )
        
        # Получаем пользователя
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Проверка баланса
        if user.balance < bet_amount:
            raise ValueError("Insufficient balance")
        
        # Получаем игру
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise ValueError("Game not found")
        
        # Проверка лимитов ставки
        if bet_amount < game.min_bet or bet_amount > game.max_bet:
            raise ValueError(
                f"Bet must be between {game.min_bet} and {game.max_bet}"
            )
        
        # Получить активный seed
        seed = self.get_or_create_active_seed(user_id)
        
        # Текущий nonce (ДО увеличения)
        current_nonce = seed.nonce
        
        # Увеличиваем nonce для следующей игры
        seed.nonce += 1
        
        # Вычисляем результат (Provably Fair)
        result_number = self.calculate_result(
            seed.server_seed,
            seed.client_seed,
            current_nonce
        )
        
        # Определяем выигрыш
        is_win = result_number < win_chance
        
        # Рассчитываем множитель и выплату
        multiplier = self.calculate_multiplier(win_chance)
        
        if is_win:
            payout = bet_amount * multiplier
            profit_loss = payout - bet_amount
        else:
            payout = 0
            profit_loss = -bet_amount
        
        # Обновляем баланс пользователя
        user.balance += profit_loss
        
        # Сохраняем ставку в БД
        bet = Bet(
            user_id=user_id,
            game_id=game_id,
            amount=bet_amount,
            result="win" if is_win else "loss",
            profit_loss=profit_loss,
            game_data=json.dumps({
                "win_chance": win_chance,
                "multiplier": multiplier,
                "result_number": result_number,
                "server_seed_hash": seed.server_seed_hash,
                "client_seed": seed.client_seed,
                "nonce": current_nonce,
                "is_win": is_win,
                "payout": payout
            })
        )
        
        self.db.add(bet)
        self.db.commit()
        self.db.refresh(bet)
        
        # Возвращаем результат
        return {
            "bet_id": bet.id,
            "result_number": result_number,
            "win_chance": win_chance,
            "multiplier": multiplier,
            "is_win": is_win,
            "payout": payout,
            "profit_loss": profit_loss,
            "new_balance": user.balance,
            # Данные для Provably Fair верификации
            "server_seed_hash": seed.server_seed_hash,
            "client_seed": seed.client_seed,
            "nonce": current_nonce
        }
    
    def rotate_seed(self, user_id: int, new_client_seed: str = None) -> dict:
        """
        Сменить seed pair (раскрыть старый server_seed)
        
        Это позволяет игроку верифицировать все прошлые игры
        
        Args:
            user_id: ID пользователя
            new_client_seed: Новый client seed (опционально)
        
        Returns:
            Данные о старом и новом seed
        """
        # Деактивируем старый seed
        old_seed = self.db.query(Seed).filter(
            Seed.user_id == user_id,
            Seed.active == True
        ).first()
        
        if old_seed:
            old_seed.active = False
            old_server_seed = old_seed.server_seed
            old_server_seed_hash = old_seed.server_seed_hash
        else:
            old_server_seed = None
            old_server_seed_hash = None
        
        # Создаём новый seed pair
        server_seed = secrets.token_hex(32)
        server_seed_hash = hashlib.sha256(server_seed.encode()).hexdigest()
        client_seed = new_client_seed or secrets.token_hex(16)
        
        new_seed = Seed(
            user_id=user_id,
            server_seed=server_seed,
            server_seed_hash=server_seed_hash,
            client_seed=client_seed,
            nonce=0,
            active=True
        )
        
        self.db.add(new_seed)
        self.db.commit()
        
        return {
            "previous_server_seed": old_server_seed,  # РАСКРЫЛИ
            "previous_server_seed_hash": old_server_seed_hash,
            "new_server_seed_hash": server_seed_hash,
            "new_client_seed": client_seed,
            "message": "Seed rotated successfully. Use previous_server_seed to verify past games."
        }
    
    def get_current_seed_info(self, user_id: int) -> dict:
        """
        Получить информацию о текущем seed (для отображения игроку)
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Публичная информация о seed
        """
        seed = self.get_or_create_active_seed(user_id)
        
        return {
            "server_seed_hash": seed.server_seed_hash,  # Хеш (публичный)
            "client_seed": seed.client_seed,
            "nonce": seed.nonce
        }