import os
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

load_dotenv()

DB_PATH = Path(os.getenv("DB_NAME", "tasks.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DB_NAME = str(DB_PATH)

_async_engine: AsyncEngine | None = None
_last_database_url: str | None = None


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    db_path = Path(os.getenv("DB_NAME", DB_NAME))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite+aiosqlite:///{db_path}"


def get_engine() -> AsyncEngine:
    global _async_engine, _last_database_url
    database_url = get_database_url()
    if _async_engine is None or database_url != _last_database_url:
        _async_engine = create_async_engine(
            database_url,
            future=True,
            echo=False,
            pool_pre_ping=True,
        )
        _last_database_url = database_url
    return _async_engine


@asynccontextmanager
async def get_db():
    engine = get_engine()
    async with engine.connect() as conn:
        yield conn
