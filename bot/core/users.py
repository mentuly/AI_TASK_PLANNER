import aiosqlite
from .db import DB_NAME


async def register_user(telegram_id: int, username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (telegram_id, username)
            VALUES (?, ?)
        """, (telegram_id, username))
        await db.commit()


async def get_user_by_username(username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id, telegram_id FROM users WHERE username=?",
            (username,)
        )
        return await cursor.fetchone()