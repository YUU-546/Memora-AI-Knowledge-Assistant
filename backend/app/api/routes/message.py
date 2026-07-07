from fastapi import APIRouter, Depends

from app.api.deps import get_knowledge_service
from app.models.schemas import MessageIn, MessageProcessResult
from app.services.knowledge_service import KnowledgeService


router = APIRouter()


@router.post("/message", response_model=MessageProcessResult)
async def process_message(
    message: MessageIn,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> MessageProcessResult:
    return await service.process_message(message)
