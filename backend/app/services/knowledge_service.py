from app.core.config import Settings
from app.integrations.deepseek import DeepSeekClient
from app.integrations.feishu import FeishuClient
from app.models.schemas import (
    KnowledgeAnalysis,
    KnowledgeCreate,
    KnowledgeSaveResult,
    MessageIn,
    MessageProcessResult,
)


class KnowledgeService:
    def __init__(self, settings: Settings) -> None:
        self.deepseek = DeepSeekClient(settings)
        self.feishu = FeishuClient(settings)

    async def analyze(self, message: MessageIn) -> KnowledgeAnalysis:
        return await self.deepseek.analyze_knowledge(message)

    async def save(self, knowledge: KnowledgeCreate) -> KnowledgeSaveResult:
        return await self.feishu.create_knowledge_record(knowledge)

    async def process_message(self, message: MessageIn) -> MessageProcessResult:
        analysis = await self.analyze(message)
        save_result = await self.save(
            KnowledgeCreate(
                user_id=message.user_id,
                raw_content=message.content,
                analysis=analysis,
            )
        )
        return MessageProcessResult(
            saved=save_result.saved,
            knowledge_id=save_result.knowledge_id,
            storage=save_result.storage,
            analysis=analysis,
        )
