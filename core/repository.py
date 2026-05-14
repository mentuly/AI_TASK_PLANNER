from core.db import get_db


async def create_task(user_id, title, steps):
    db = await get_db()

    cursor = await db.execute(
        "INSERT INTO tasks (user_id, title) VALUES (?, ?)",
        (user_id, title)
    )
    task_id = cursor.lastrowid

    if not steps:
        steps = [{
            "title": "Розбити задачу",
            "description": "Спробуй ще раз або зроби вручну",
            "minutes": 10
        }]

    for step in steps:
        step_title = step.get("title") or step.get("name") or "Без назви"
        step_description = step.get("description", "")
        step_minutes = step.get("minutes") or step.get("time") or 10

        await db.execute(
            "INSERT INTO steps (task_id, title, description, minutes) VALUES (?, ?, ?, ?)",
            (task_id, step_title, step_description, step_minutes)
        )

    await db.commit()
    await db.close()

    return task_id


async def get_tasks(user_id):
    db = await get_db()

    cursor = await db.execute(
        "SELECT id, title, is_done FROM tasks WHERE user_id=? ORDER BY id",
        (user_id,)
    )

    result = await cursor.fetchall()
    await db.close()

    return result


async def get_steps(task_id):
    db = await get_db()

    cursor = await db.execute(
        "SELECT title, description, minutes FROM steps WHERE task_id=? ORDER BY id",
        (task_id,)
    )

    result = await cursor.fetchall()
    await db.close()

    return result


async def mark_done(task_id):
    db = await get_db()

    await db.execute(
        "UPDATE tasks SET is_done=1 WHERE id=?",
        (task_id,)
    )

    await db.commit()
    await db.close()


async def delete_task(task_id):
    db = await get_db()

    await db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    await db.execute("DELETE FROM steps WHERE task_id=?", (task_id,))

    await db.commit()
    await db.close()

async def get_task_by_id(task_id: int):
    """Отримуємо одну таску з кроками"""
    db = await get_db()
    
    cursor = await db.execute(
        "SELECT id, title, is_done FROM tasks WHERE id=?",
        (task_id,)
    )
    task = await cursor.fetchone()
    
    if not task:
        await db.close()
        return None
    
    cursor = await db.execute(
        "SELECT title, description, minutes FROM steps WHERE task_id=? ORDER BY id",
        (task_id,)
    )
    steps = await cursor.fetchall()
    await db.close()
    
    return {
        "id": task[0],
        "title": task[1],
        "is_done": task[2],
        "steps": steps
    }


async def get_task_id_by_user_and_index(user_id: int, index: int):
    """Отримуємо task_id за індексом для юзера (для callback_data)"""
    db = await get_db()
    
    cursor = await db.execute(
        "SELECT id FROM tasks WHERE user_id=? ORDER BY id LIMIT 1 OFFSET ?",
        (user_id, index - 1)
    )
    row = await cursor.fetchone()
    await db.close()
    
    return row[0] if row else None

async def get_task_owner(task_id: int):
    db = await get_db()
    cursor = await db.execute(
        "SELECT user_id FROM tasks WHERE id=?",
        (task_id,)
    )
    row = await cursor.fetchone()
    await db.close()
    return row[0] if row else None

async def get_tasks_with_steps(user_id):
    """Отримуємо всі таски з кроками одним запитом (JOIN)"""
    db = await get_db()
    
    cursor = await db.execute("""
        SELECT 
            t.id, t.title, t.is_done,
            s.title as step_title, 
            s.description as step_description, 
            s.minutes as step_minutes
        FROM tasks t
        LEFT JOIN steps s ON t.id = s.task_id
        WHERE t.user_id = ?
        ORDER BY t.id, s.id
    """, (user_id,))
    
    rows = await cursor.fetchall()
    await db.close()
    
    tasks_dict = {}
    for row in rows:
        task_id, title, is_done, step_title, step_desc, step_minutes = row
        
        if task_id not in tasks_dict:
            tasks_dict[task_id] = {
                "id": task_id,
                "title": title,
                "is_done": is_done,
                "total_minutes": 0,
                "steps": []
            }
        
        if step_title:
            tasks_dict[task_id]["steps"].append({
                "title": step_title,
                "description": step_desc,
                "minutes": step_minutes,
                "is_done": False
            })
            tasks_dict[task_id]["total_minutes"] += step_minutes
    
    return list(tasks_dict.values())

async def get_task_owner(task_id: int):
    """Отримуємо user_id власника таски"""
    db = await get_db()
    cursor = await db.execute(
        "SELECT user_id FROM tasks WHERE id=?",
        (task_id,)
    )
    row = await cursor.fetchone()
    await db.close()
    return row[0] if row else None