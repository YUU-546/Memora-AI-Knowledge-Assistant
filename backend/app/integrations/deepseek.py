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
        )

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
