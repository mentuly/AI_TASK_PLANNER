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
    
    # user_id
    cursor = await db.execute(
        "SELECT user_id FROM auth_tokens WHERE token=?",
        (token,)
    )
    row = await cursor.fetchone()
    
    if row:
        user_id = row[0]
        # видалення токену після використання
        await db.execute(
            "DELETE FROM auth_tokens WHERE token=?",
            (token,)
        )
        await db.commit()
        await db.close()
        return user_id
    
    await db.close()
    return None