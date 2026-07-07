import httpx

from app.core.config import Settings
from app.models.schemas import KnowledgeCreate, KnowledgeSaveResult


class FeishuClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def create_knowledge_record(self, knowledge: KnowledgeCreate) -> KnowledgeSaveResult:
        if not self.settings.feishu_enabled:
            return KnowledgeSaveResult(
                saved=True,
                knowledge_id=None,
                storage="dry_run",
                message="Feishu is not configured. Saved as dry-run result.",
            )

        token = await self._tenant_access_token()
        url = (
            "https://open.feishu.cn/open-apis/bitable/v1/apps/"
            f"{self.settings.feishu_bitable_app_token}/tables/"
            f"{self.settings.feishu_bitable_table_id}/records"
        )
        payload = {"fields": self._to_feishu_fields(knowledge)}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        record_id = data.get("data", {}).get("record", {}).get("record_id")
        return KnowledgeSaveResult(
            saved=True,
            knowledge_id=record_id,
            storage="feishu",
            message="Knowledge saved to Feishu.",
        )

    async def _tenant_access_token(self) -> str:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                json={
                    "app_id": self.settings.feishu_app_id,
                    "app_secret": self.settings.feishu_app_secret,
                },
            )
            response.raise_for_status()
            data = response.json()

        token = data.get("tenant_access_token")
        if not token:
            raise RuntimeError(f"Failed to get Feishu tenant_access_token: {data}")
        return token

    def _to_feishu_fields(self, knowledge: KnowledgeCreate) -> dict[str, object]:
        analysis = knowledge.analysis
        return {
            "user_id": knowledge.user_id,
            "title": analysis.title,
            "source": analysis.source,
            "original_url": analysis.original_url or "",
            "raw_content": knowledge.raw_content,
            "summary": analysis.summary,
            "category": analysis.category,
            "tags": ", ".join(analysis.tags),
            "keywords": ", ".join(analysis.keywords),
            "user_note": analysis.user_note or "",
            "model": analysis.model or "",
        }
