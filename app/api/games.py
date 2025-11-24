from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models.user import User
from app.models.game import Game
from app.schemas.game import (
    NvutiBetRequest,
    NvutiBetResponse,
    SeedInfo,
    SeedRotateRequest,
    SeedRotateResponse
)
from app.services.auth import get_current_user
from app.services.nvuti_service import NvutiService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/games",
    tags=["Games"]
)


# =========================
# NVUTI ENDPOINTS
# =========================

@router.post("/nvuti/bet", response_model=NvutiBetResponse)
def play_nvuti(
    bet_data: NvutiBetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Сыграть в Nvuti (Provably Fair Dice Game)
    
    Игрок выбирает:
    - **win_chance**: Шанс выигрыша (1-95%)
    - **amount**: Размер ставки
    
    Система генерирует случайное число 0.00 - 99.99
    
    **Если число < win_chance → выигрыш**
    
    Множитель выплаты: (100 - 5) / win_chance
    
    Примеры:
    - 50% шанс → 1.90x множитель
    - 10% шанс → 9.50x множитель
    - 90% шанс → 1.06x множитель
    
    **Provably Fair:** Результат можно проверить криптографически
    """
    # Получаем игру Nvuti из БД
    game = db.query(Game).filter(Game.type == "dice").first()
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nvuti game not found in database. Run init_db.py first."
        )
    
    # Создаём сервис и играем
    service = NvutiService(db)
    
    try:
        result = service.play(
            user_id=current_user.id,
            game_id=game.id,
            bet_amount=bet_data.amount,
            win_chance=bet_data.win_chance
        )
        
        logger.info(
            f"User {current_user.username} played Nvuti: "
            f"bet={bet_data.amount}, win_chance={bet_data.win_chance}, "
            f"result={result['is_win']}, profit_loss={result['profit_loss']}"
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/nvuti/seed", response_model=SeedInfo)
def get_current_seed(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить текущий seed pair
    
    Показывает:
    - **server_seed_hash**: Хеш серверного seed (публичный)
    - **client_seed**: Клиентский seed
    - **nonce**: Количество игр с этим seed pair
    
    Этот endpoint НЕ раскрывает server_seed до смены seed.
    """
    service = NvutiService(db)
    return service.get_current_seed_info(current_user.id)


@router.post("/nvuti/seed/rotate", response_model=SeedRotateResponse)
def rotate_seed(
    request: SeedRotateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Сменить seed pair
    
    При смене:
    - **Раскрывается** старый server_seed (для верификации прошлых игр)
    - Создаётся новый seed pair
    - Можно задать свой client_seed
    
    После смены ты можешь верифицировать все игры со старым seed.
    """
    service = NvutiService(db)
    
    result = service.rotate_seed(
        user_id=current_user.id,
        new_client_seed=request.new_client_seed
    )
    
    logger.info(f"User {current_user.username} rotated seed")
    
    return result


@router.get("/")
def list_games(db: Session = Depends(get_db)):
    """
    Список всех доступных игр
    """
    games = db.query(Game).all()
    return games