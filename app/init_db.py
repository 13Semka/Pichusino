from app.database import SessionLocal
from app.models.game import Game


def init_games():
    """
    Инициализация игр в БД
    """
    db = SessionLocal()
    
    try:
        # Проверяем есть ли уже игра Nvuti
        existing_game = db.query(Game).filter(Game.name == "Nvuti").first()
        if existing_game:
            print("✅ Game 'Nvuti' already exists")
            print(f"   ID: {existing_game.id}")
            print(f"   House Edge: {existing_game.house_edge}%")
            return
        
        # Создаём игру Nvuti
        nvuti = Game(
            name="Nvuti",
            type="dice",
            house_edge=5.0,
            min_bet=1.0,
            max_bet=1000.0,
            rules="""
# Nvuti - Provably Fair Dice Game

## Правила:
1. Выбери **шанс выигрыша** (1% - 95%)
2. Выбери **размер ставки** (1₽ - 1000₽)
3. Система генерирует случайное число 0.00 - 99.99
4. **Если число < твоего шанса → ВЫИГРЫШ**

## Множитель выплаты:
```
Множитель = (100 - house_edge) / win_chance
```

### Примеры:
- **50% шанс** → множитель **1.90x** (часто выигрываешь, но мало)
- **10% шанс** → множитель **9.50x** (редко выигрываешь, но много)
- **90% шанс** → множитель **1.06x** (почти всегда выигрываешь, но очень мало)

## Provably Fair:
Каждый результат можно проверить криптографически!

Система использует:
- **Server Seed** (секретный)
- **Client Seed** (твой или автоматический)
- **Nonce** (номер игры)

Перед игрой ты видишь **хеш server seed**.  
После смены seed - раскрывается **сам server seed**.  
Ты можешь пересчитать результаты всех игр и убедиться что казино не жульничало.

## House Edge: 5%
Математическое ожидание: за каждые 100₽ ставок ты проиграешь 5₽ в долгосрочной перспективе.
            """
        )
        
        db.add(nvuti)
        db.commit()
        db.refresh(nvuti)
        
        print("✅ Game 'Nvuti' created successfully!")
        print(f"   ID: {nvuti.id}")
        print(f"   Type: {nvuti.type}")
        print(f"   House Edge: {nvuti.house_edge}%")
        print(f"   Min Bet: {nvuti.min_bet}₽")
        print(f"   Max Bet: {nvuti.max_bet}₽")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing games...")
    init_games()