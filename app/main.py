from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Импорт роутеров
from app.api import auth  # ← ДОБАВЬ ЭТУ СТРОКУ

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создание приложения
app = FastAPI(
    title="Pichisino API",
    description="Educational casino simulation with Provably Fair Nvuti game",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Базовые endpoints
@app.get("/")
def root():
    return {
        "message": "Welcome to Pichisino API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Подключение роутеров
app.include_router(auth.router)  # ← ДОБАВЬ ЭТУ СТРОКУ

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)