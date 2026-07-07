import asyncio

from app.core.config import Settings
from app.integrations.deepseek import DeepSeekClient
from app.models.schemas import MessageIn


def test_fallback_analyzer_without_api_key() -> None:
    settings = Settings(deepseek_api_key="")
    client = DeepSeekClient(settings)

    result = asyncio.run(
        client.analyze_knowledge(
            MessageIn(
                user_id="u_001",
                content="DeepSeek 成本较低，适合 MVP 阶段做知识摘要和分类。",
            )
        )
    )

    assert result.title
    assert result.category == "待整理"
    assert result.model == "local-fallback"
