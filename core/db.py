import aiosqlite

DB_NAME = "tasks.db"

async def get_db():
    return await aiosqlite.connect(DB_NAME)