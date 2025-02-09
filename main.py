from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.routers import users, subscriptions, payments, messages, article, blog, ai, tinkoff, admin
from src.error.error_handlers import add_error_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.database.models import async_main
    await async_main()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="User Management API",
    description="API для управления пользователями, подписками, платежами и сообщениями",
    version="1.0.0"
)

# Отключаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы с любых доменов
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все HTTP-методы
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.include_router(users.router, prefix="/user", tags=["Users"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])
app.include_router(article.router, prefix="/article", tags=["Article"])
app.include_router(blog.router, prefix="/blog", tags=["Blog"])
app.include_router(ai.router, prefix="/ai", tags=["Ai"])
app.include_router(tinkoff.router, prefix="/tinkoff", tags=["Tinkoff"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

add_error_handlers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
