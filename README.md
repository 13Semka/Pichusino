# Pichisino

Веб-приложение казино с игрой Nvuti и системой Provably Fair для демонстрации математики азартных игр.

## Технологии

- FastAPI
- PostgreSQL 
- SQLAlchemy
- JWT Authentication
- Provably Fair криптография

## Установка
```bash
# Клонирование
git clone <repo-url>
cd pichisino

# Виртуальное окружение
python -m venv .venv
source .venv/bin/activate

# Зависимости
pip install -r requirements.txt

# Переменные окружения
cat > .env << 'EOF'
DATABASE_URL=postgresql://user:password@localhost:5432/pichisino
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# База данных
docker-compose up -d
alembic upgrade head
python -m app.init_db
```

## Запуск
```bash
uvicorn app.main:app --reload
```

Откройте http://localhost:8000/docs для Swagger UI.

## Архитектура

Проект следует MVC паттерну:

- `models/` - SQLAlchemy модели (User, Game, Seed, Bet)
- `services/` - бизнес-логика (NvutiService, auth)
- `api/` - HTTP endpoints (REST API)
- `schemas/` - Pydantic валидация

## API

### Аутентификация

- `POST /api/auth/register` - регистрация
- `POST /api/auth/login` - получение JWT токена
- `GET /api/auth/me` - данные пользователя

### Игра Nvuti

- `POST /api/games/nvuti/bet` - сделать ставку
- `GET /api/games/nvuti/seed` - текущий seed
- `POST /api/games/nvuti/seed/rotate` - сменить seed

## Игра Nvuti

Выбираешь шанс выигрыша (1-95%) и размер ставки. Система генерирует число 0-99.99. Если число меньше твоего шанса - выигрываешь.

Множитель: `(100 - 5) / шанс`

Примеры:
- 50% шанс → 1.90x множитель
- 10% шанс → 9.50x множитель

House edge 5% означает что в долгосрочной перспективе проиграешь 5% от всех ставок.

## Provably Fair

Каждый результат проверяется криптографически через HMAC-SHA256. До игры видишь хеш server_seed, после смены seed получаешь сам server_seed и можешь пересчитать все результаты.

## Тестирование
```bash
# Установка pytest
pip install pytest pytest-asyncio httpx

# Создание pytest.ini
cat > pytest.ini << 'EOF'
[pytest]
pythonpath = .
testpaths = tests
EOF

# Запуск тестов
PYTHONPATH=. pytest -v

# С покрытием
pip install pytest-cov
PYTHONPATH=. pytest --cov=app --cov-report=html
```

## Структура проекта
```
pichisino/
├── app/
│   ├── models/       # БД модели
│   ├── services/     # Логика
│   ├── api/          # Endpoints
│   ├── schemas/      # Валидация
│   └── main.py
├── tests/            # Тесты
├── alembic/          # Миграции
└── docker-compose.yml
```

## Примеры запросов

### Регистрация
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"player1","email":"player@test.com","password":"pass123"}'
```

### Логин
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=player1&password=pass123"
```

### Ставка
```bash
curl -X POST http://localhost:8000/api/games/nvuti/bet \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"win_chance":50,"amount":10}'
```

## База данных
```
users ──┬─→ seeds (provably fair)
        └─→ bets ←── games
```

Foreign Key связи обеспечивают целостность данных.

## Disclaimer

Образовательный проект. Реальное казино требует лицензии, KYC/AML, платёжные процессоры и правовую команду. Не используй для настоящих ставок.