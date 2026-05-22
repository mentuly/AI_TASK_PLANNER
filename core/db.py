import os
from pathlib import Path
import aiosqlite

DB_PATH = Path(os.getenv("DB_NAME", "tasks.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DB_NAME = str(DB_PATH)

async def get_db():
    return await aiosqlite.connect(DB_NAME)