from fastapi import APIRouter, Depends

from app.api.deps import get_knowledge_service
from app.models.schemas import KnowledgeCreate, KnowledgeSaveResult, SearchResponse
from app.services.knowledge_service import KnowledgeService


router = APIRouter()


@router.post("", response_model=KnowledgeSaveResult)
async def save_knowledge(
    knowledge: KnowledgeCreate,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> KnowledgeSaveResult:
    return await service.save(knowledge)


@router.get("/search", response_model=SearchResponse)
async def search_knowledge(
    q: str,
    user_id: str,
    limit: int = 10,
) -> SearchResponse:
    _ = (q, user_id, limit)
    return SearchResponse(
        items=[],
        message="Search is reserved for Phase 5 RAG. MVP only saves knowledge cards.",
    )
