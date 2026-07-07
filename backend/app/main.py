from fastapi import FastAPI

from app.api.routes import ai, health, knowledge, message, wechat
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Memora AI personal knowledge assistant backend",
)

app.include_router(health.router)
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(message.router, prefix="/api", tags=["message"])
app.include_router(wechat.router, prefix="/api/wechat", tags=["wechat"])
