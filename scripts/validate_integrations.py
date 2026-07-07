import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.core.config import get_settings  # noqa: E402
from app.integrations.deepseek import DeepSeekClient  # noqa: E402
from app.integrations.feishu import FeishuClient  # noqa: E402
from app.models.schemas import MessageIn  # noqa: E402


async def validate_deepseek() -> None:
    result = await DeepSeekClient(get_settings()).analyze_knowledge(
        MessageIn(
            user_id="integration_check",
            content_type="text",
            content="Memora 是一个基于微信入口的 AI 个人知识助手，用 DeepSeek 低成本完成知识摘要、分类和标签生成。",
        )
    )
    print("DeepSeek: ok")
    print(f"- model: {result.model}")
    print(f"- title: {result.title}")
    print(f"- category: {result.category}")
    print(f"- tags_count: {len(result.tags)}")
    if result.token_usage:
        print(f"- total_tokens: {result.token_usage.total_tokens}")


async def validate_feishu() -> None:
    result = await FeishuClient(get_settings()).validate_access()
    print(f"Feishu: {result['status']}")
    print(f"- {result['message']}")


async def main() -> None:
    await validate_deepseek()
    await validate_feishu()


if __name__ == "__main__":
    asyncio.run(main())
