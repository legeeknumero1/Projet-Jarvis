"""Vérifie rapidement la persistance mémoire via MemoryService."""
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
from backend.db.database import Database
from backend.services.memory import MemoryService


async def main() -> None:
    config = Config()
    database = Database(config)
    memory_service = MemoryService(config)

    await memory_service.initialize(database)

    message = "Note que j aime le cafe."
    response = "Très bien, je retiens cette information."
    saved = await memory_service.store_interaction("cli_test_user", message, response)
    print(f"store_interaction={saved}")

    memories = await memory_service.get_contextual_memories(
        "cli_test_user", "Que sais-tu sur moi?", limit=3
    )
    print(f"memories_count={len(memories)}")
    for idx, memory in enumerate(memories, 1):
        excerpt = memory.get("content", "")[:60]
        print(f"[{idx}] {excerpt!r}")


if __name__ == "__main__":
    asyncio.run(main())
