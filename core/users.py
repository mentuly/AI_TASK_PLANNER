from sqlalchemy import select, insert
from core.db import get_db
from core.db_models.users import users


async def register_user(telegram_id: int, username: str):
    async with get_db() as conn:
        result = await conn.execute(
            select(users.c.id).where(users.c.telegram_id == telegram_id)
        )
        if result.scalar_one_or_none() is None:
            await conn.execute(
                insert(users).values(telegram_id=telegram_id, username=username)
            )
            await conn.commit()


async def get_user_by_username(username: str):
    async with get_db() as conn:
        result = await conn.execute(
            select(users.c.id, users.c.telegram_id).where(users.c.username == username)
        )
        row = result.fetchone()

    return tuple(row) if row else None
