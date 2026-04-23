import aiosqlite

DB_NAME = "tasks.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
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


async def create_task(user_id, title, steps):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "INSERT INTO tasks (user_id, title) VALUES (?, ?)",
            (user_id, title)
        )
        task_id = cursor.lastrowid

        for step in steps:
            await db.execute(
                "INSERT INTO steps (task_id, title, description, minutes) VALUES (?, ?, ?, ?)",
                (task_id, step["title"], step["description"], step["minutes"])
            )

        await db.commit()
        return task_id


async def get_tasks(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id, title, is_done FROM tasks WHERE user_id=?",
            (user_id,)
        )
        return await cursor.fetchall()


async def get_steps(task_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT title, description, minutes FROM steps WHERE task_id=?",
            (task_id,)
        )
        return await cursor.fetchall()


async def mark_done(task_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE tasks SET is_done=1 WHERE id=?",
            (task_id,)
        )
        await db.commit()


async def delete_task(task_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        await db.execute("DELETE FROM steps WHERE task_id=?", (task_id,))
        await db.commit()