from core.db import get_db

async def init_db():
    db = await get_db()

    await db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        is_done INTEGER DEFAULT 0
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER,
        title TEXT,
        description TEXT,
        minutes INTEGER,
        is_done INTEGER DEFAULT 0
    )
    """)

    await db.commit()
    await db.close()