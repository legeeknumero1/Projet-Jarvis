"""Quick check that Ollama endpoint and client wiring are up."""
import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.config.config import Config
from backend.services.llm import LLMService


async def main() -> None:
    config = Config()
    service = LLMService(config)

    await service.initialize()
    available = service.is_available()
    healthy = await service.ping()

    print(f"ollama_available={available}")
    print(f"ollama_ping={healthy}")

    await service.close()


if __name__ == "__main__":
    asyncio.run(main())
