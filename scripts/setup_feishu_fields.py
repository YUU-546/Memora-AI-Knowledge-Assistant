import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.core.config import get_settings  # noqa: E402
from app.integrations.feishu import FeishuClient  # noqa: E402


async def main() -> None:
    client = FeishuClient(get_settings())
    created = await client.ensure_knowledge_fields()
    if created:
        print("created fields:")
        for field in created:
            print(f"- {field}")
    else:
        print("all required fields already exist")


if __name__ == "__main__":
    asyncio.run(main())
