from app.core.config import get_settings
from app.services.knowledge_service import KnowledgeService


def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService(get_settings())
