import httpx

from app.core.config import Settings
from app.models.schemas import FeishuFieldSpec, KnowledgeCreate, KnowledgeSaveResult


MVP_KNOWLEDGE_FIELDS = [
    FeishuFieldSpec(field_name="user_id"),
    FeishuFieldSpec(field_name="title"),
    FeishuFieldSpec(field_name="source"),
    FeishuFieldSpec(field_name="original_url", type=15),
    FeishuFieldSpec(field_name="raw_content"),
    FeishuFieldSpec(field_name="summary"),
    FeishuFieldSpec(field_name="category"),
    FeishuFieldSpec(field_name="tags"),
    FeishuFieldSpec(field_name="keywords"),
    FeishuFieldSpec(field_name="user_note"),
    FeishuFieldSpec(field_name="model"),
    FeishuFieldSpec(field_name="prompt_tokens", type=2),
    FeishuFieldSpec(field_name="completion_tokens", type=2),
    FeishuFieldSpec(field_name="total_tokens", type=2),
]


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

    async def ensure_knowledge_fields(self) -> list[str]:
        if not self.settings.feishu_enabled:
            raise RuntimeError("Feishu is not configured.")

        token = await self._tenant_access_token()
        existing = await self._list_field_names(token)
        created: list[str] = []

        for field in MVP_KNOWLEDGE_FIELDS:
            if field.field_name in existing:
                continue
            await self._create_field(token, field)
            created.append(field.field_name)

        return created

    async def _list_field_names(self, token: str) -> set[str]:
        url = (
            "https://open.feishu.cn/open-apis/bitable/v1/apps/"
            f"{self.settings.feishu_bitable_app_token}/tables/"
            f"{self.settings.feishu_bitable_table_id}/fields"
        )
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            data = response.json()

        fields = data.get("data", {}).get("items", [])
        return {field.get("field_name", "") for field in fields if field.get("field_name")}

    async def _create_field(self, token: str, field: FeishuFieldSpec) -> None:
        url = (
            "https://open.feishu.cn/open-apis/bitable/v1/apps/"
            f"{self.settings.feishu_bitable_app_token}/tables/"
            f"{self.settings.feishu_bitable_table_id}/fields"
        )
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={"field_name": field.field_name, "type": field.type},
            )
            response.raise_for_status()

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

    async def validate_access(self) -> dict[str, str]:
        if not self.settings.feishu_enabled:
            return {"status": "missing_config", "message": "Feishu config is incomplete."}

        token = await self._tenant_access_token()
        try:
            await self._list_field_names(token)
        except httpx.HTTPStatusError as exc:
            return {
                "status": "failed",
                "message": self._summarize_error(exc),
            }

        return {"status": "ok", "message": "Feishu Bitable access is available."}

    def _summarize_error(self, exc: httpx.HTTPStatusError) -> str:
        try:
            data = exc.response.json()
        except ValueError:
            return exc.response.text[:500]

        code = data.get("code")
        msg = data.get("msg", "")
        violations = data.get("error", {}).get("permission_violations", [])
        scopes = [
            item.get("subject")
            for item in violations
            if item.get("type") == "action_scope_required" and item.get("subject")
        ]
        if scopes:
            return f"Feishu error {code}: missing scopes: {', '.join(scopes)}. {msg}"
        return f"Feishu error {code}: {msg}"

    def _to_feishu_fields(self, knowledge: KnowledgeCreate) -> dict[str, object]:
        analysis = knowledge.analysis
        usage = analysis.token_usage
        fields = {
            "user_id": knowledge.user_id,
            "title": analysis.title,
            "source": analysis.source,
            "original_url": {
                "text": analysis.original_url,
                "link": analysis.original_url,
            }
            if analysis.original_url
            else None,
            "raw_content": knowledge.raw_content,
            "summary": analysis.summary,
            "category": analysis.category,
            "tags": ", ".join(analysis.tags),
            "keywords": ", ".join(analysis.keywords),
            "user_note": analysis.user_note or "",
            "model": analysis.model or "",
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
        }
        return {key: value for key, value in fields.items() if value is not None}
