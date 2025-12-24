import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
import books, reviews
from dotenv import load_dotenv

load_dotenv()

# Создаем таблицы в БД при запуске
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Reviews Platform API",
    description="API для платформы отзывов о книгах",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Настройка CORS (разрешаем все для разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(books.router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1")

# Главная страница
@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в Book Reviews Platform API",
        "docs": "/docs",
        "endpoints": {
            "books": "/api/v1/books",
            "reviews": "/api/v1/reviews"
        }
    }

# Проверка здоровья
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "book-reviews-api"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost",port=8000)