from fastapi import APIRouter, Depends

from app.api.deps import get_knowledge_service
from app.models.schemas import KnowledgeAnalysis, MessageIn
from app.services.knowledge_service import KnowledgeService


router = APIRouter()


@router.post("/analyze", response_model=KnowledgeAnalysis)
async def analyze_message(
    message: MessageIn,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> KnowledgeAnalysis:
    return await service.analyze(message)
