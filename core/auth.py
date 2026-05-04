import secrets
from core.db import get_db


async def create_auth_token(user_id: int):
    token = secrets.token_urlsafe(32)

    db = await get_db()
    await db.execute(
        "INSERT INTO auth_tokens (token, user_id) VALUES (?, ?)",
        (token, user_id)
    )
    await db.commit()
    await db.close()

    return token


async def get_user_by_token(token: str):
    db = await get_db()

    cursor = await db.execute(
        "SELECT user_id FROM auth_tokens WHERE token=?",
        (token,)
    )

    row = await cursor.fetchone()
    await db.close()

    return row[0] if row else None