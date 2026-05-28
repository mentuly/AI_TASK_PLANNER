import secrets
from sqlalchemy import select, insert, delete
from core.db import get_db
from core.db_models.auth_tokens import auth_tokens


async def create_auth_token(user_id: int):
    token = secrets.token_urlsafe(32)

    async with get_db() as conn:
        await conn.execute(
            insert(auth_tokens).values(token=token, user_id=user_id)
        )
        await conn.commit()

    return token


async def get_user_by_token(token: str):
    async with get_db() as conn:
        result = await conn.execute(
            select(auth_tokens.c.user_id).where(auth_tokens.c.token == token)
        )
        row = result.fetchone()
        if row:
            user_id = row[0]
            await conn.execute(delete(auth_tokens).where(auth_tokens.c.token == token))
            await conn.commit()
            return user_id

    return None