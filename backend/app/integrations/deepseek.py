import json
from typing import Any

import httpx

from app.agents.prompts import KNOWLEDGE_ANALYZER_SYSTEM_PROMPT
from app.core.config import Settings
from app.models.schemas import KnowledgeAnalysis, MessageIn, TokenUsage


class DeepSeekClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def analyze_knowledge(self, message: MessageIn) -> KnowledgeAnalysis:
        if not self.settings.deepseek_api_key:
            return self._fallback_analysis(message)

        payload = {
            "model": self.settings.deepseek_model,
            "messages": [
                {"role": "system", "content": KNOWLEDGE_ANALYZER_SYSTEM_PROMPT},
                {"role": "user", "content": self._build_user_prompt(message)},
            ],
            "temperature": self.settings.deepseek_temperature,
            "max_tokens": self.settings.deepseek_max_tokens,
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"{self.settings.deepseek_base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        usage = self._parse_usage(data.get("usage", {}))

        return KnowledgeAnalysis(
            **parsed,
            model=self.settings.deepseek_model,
            token_usage=usage,
        ).model_copy(update=self._fallback_missing_fields(parsed, message))

    def _build_user_prompt(self, message: MessageIn) -> str:
        return "\n".join(
            [
                f"user_id: {message.user_id}",
                f"content_type: {message.content_type}",
                f"source_url: {message.source_url or ''}",
                f"user_note: {message.user_note or ''}",
                "content:",
                message.content,
            ]
        )

    def _parse_usage(self, usage: dict[str, Any]) -> TokenUsage:
        return TokenUsage(
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
        )

    def _fallback_missing_fields(self, parsed: dict[str, Any], message: MessageIn) -> dict[str, Any]:
        updates: dict[str, Any] = {}
        content = message.content.strip()
        bad_titles = {"", "无法识别的内容", "未命名知识", "无标题"}
        if str(parsed.get("title", "")).strip() in bad_titles:
            updates["title"] = self._derive_title(content)
        if not parsed.get("summary"):
            updates["summary"] = content[:160] or "用户保存的待整理内容。"
        if not parsed.get("category"):
            updates["category"] = "待整理"
        if not parsed.get("tags"):
            updates["tags"] = self._derive_tags(content)
        if not parsed.get("keywords"):
            updates["keywords"] = self._derive_tags(content)
        if message.source_url and not parsed.get("original_url"):
            updates["original_url"] = message.source_url
        if message.user_note and not parsed.get("user_note"):
            updates["user_note"] = message.user_note
        return updates

    def _derive_title(self, content: str) -> str:
        first_line = content.splitlines()[0].strip() if content else ""
        return first_line[:40] or "待整理知识"

    def _derive_tags(self, content: str) -> list[str]:
        tags = []
        keyword_map = {
            "AI": "AI",
            "知识": "知识管理",
            "微信": "微信入口",
            "飞书": "飞书",
            "产品": "产品设计",
            "架构": "技术架构",
        }
        for needle, tag in keyword_map.items():
            if needle in content and tag not in tags:
                tags.append(tag)
        return tags or ["待整理"]

    def _fallback_analysis(self, message: MessageIn) -> KnowledgeAnalysis:
        content = message.content.strip()
        title = content.splitlines()[0][:40] if content else "未命名知识"
        summary = content[:140] if len(content) > 140 else content

        return KnowledgeAnalysis(
            title=title or "未命名知识",
            source="local_fallback",
            original_url=message.source_url,
            summary=summary or "本地开发模式下生成的占位摘要。",
            category="待整理",
            tags=["待整理"],
            keywords=[],
            user_note=message.user_note,
            model="local-fallback",
            token_usage=TokenUsage(),
        )
