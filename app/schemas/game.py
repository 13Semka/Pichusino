from pydantic import BaseModel, Field


class NvutiBetRequest(BaseModel):
    """
    Схема для создания ставки в Nvuti
    """
    win_chance: float = Field(
        ge=1.0,
        le=95.0,
        description="Win chance percentage (1-95%)"
    )
    amount: float = Field(
        gt=0,
        description="Bet amount (must be positive)"
    )


class NvutiBetResponse(BaseModel):
    """
    Схема ответа после ставки
    """
    bet_id: int
    result_number: float
    win_chance: float
    multiplier: float
    is_win: bool
    payout: float
    profit_loss: float
    new_balance: float
    # Provably Fair данные
    server_seed_hash: str
    client_seed: str
    nonce: int


class SeedInfo(BaseModel):
    """
    Информация о текущем seed
    """
    server_seed_hash: str
    client_seed: str
    nonce: int


class SeedRotateRequest(BaseModel):
    """
    Запрос на смену seed
    """
    new_client_seed: str | None = None


class SeedRotateResponse(BaseModel):
    """
    Ответ после смены seed
    """
    previous_server_seed: str | None
    previous_server_seed_hash: str | None
    new_server_seed_hash: str
    new_client_seed: str
    message: str