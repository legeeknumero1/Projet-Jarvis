"""Quick CLI test to validate basic DB read/write."""
import os
import sys
from pathlib import Path
from datetime import datetime
from types import SimpleNamespace

import asyncio
from pydantic import ValidationError
from sqlalchemy import select

try:
    import asyncpg  # noqa: F401
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from backend.config.config import Config  # noqa: E402
from backend.db.database import Database, User, Memory  # noqa: E402


async def main() -> None:
    try:
        config = Config()
    except ValidationError as exc:
        print(f"[db-cli-test] Config validation failed ({exc.__class__.__name__}); using minimal fallback config")
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://jarvis:jarvis@localhost:5432/jarvis_db",
        )
        config = SimpleNamespace(database_url=database_url, debug=False)

    # Fallback to psycopg async driver if asyncpg isn't available (e.g., Python 3.13)
    if (
        not HAS_ASYNCPG
        and config.database_url.startswith("postgresql+asyncpg://")
    ):
        config.database_url = config.database_url.replace(
            "postgresql+asyncpg://", "postgresql+psycopg://", 1
        )
        print("[db-cli-test] Switched DSN to use psycopg async driver")
    database = Database(config)
    user_id = "cli_test_user"

    try:
        await database.connect()
        print("[db-cli-test] Connected to database")

        async with database.get_session() as session:
            user = await session.get(User, user_id)
            if not user:
                user = User(id=user_id, name="CLI Test User")
                session.add(user)
                await session.commit()
                print(f"[db-cli-test] Inserted user '{user_id}'")

            memory = Memory(user_id=user_id, category="debug")
            memory.decrypted_content = f"Test memory written at {datetime.utcnow().isoformat()}"
            session.add(memory)
            await session.commit()
            await session.refresh(memory)
            print(f"[db-cli-test] Inserted memory id={memory.id}")

            result = await session.execute(select(Memory).where(Memory.user_id == user_id))
            memories = result.scalars().all()
            print(f"[db-cli-test] Retrieved {len(memories)} memories for user '{user_id}'")

            await session.delete(memory)
            await session.commit()
            print(f"[db-cli-test] Deleted memory id={memory.id}")

    except Exception as exc:
        print(f"[db-cli-test] ERROR: {exc}")
    finally:
        await database.disconnect()
        print("[db-cli-test] Disconnected from database")


if __name__ == "__main__":
    asyncio.run(main())
