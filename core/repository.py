from sqlalchemy import text, insert
from core.db import get_db
from core.db_models.tasks import tasks
from core.db_models.steps import steps as steps_table


async def create_task(user_id, title, steps):
    async with get_db() as conn:
        result = await conn.execute(
            insert(tasks).values(user_id=user_id, title=title)
        )
        task_id = result.inserted_primary_key[0]

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

            await conn.execute(
                insert(steps_table).values(
                    task_id=task_id,
                    title=step_title,
                    description=step_description,
                    minutes=step_minutes,
                )
            )

        await conn.commit()

    return task_id


async def get_tasks(user_id):
    async with get_db() as conn:
        result = await conn.execute(
            text("SELECT id, title, is_done FROM tasks WHERE user_id=:user_id ORDER BY id"),
            {"user_id": user_id}
        )
        rows = result.fetchall()

    return [tuple(row) for row in rows]


async def get_steps(task_id):
    async with get_db() as conn:
        result = await conn.execute(
            text("SELECT title, description, minutes FROM steps WHERE task_id=:task_id ORDER BY id"),
            {"task_id": task_id}
        )
        rows = result.fetchall()

    return [tuple(row) for row in rows]


async def mark_done(task_id):
    async with get_db() as conn:
        await conn.execute(
            text("UPDATE tasks SET is_done=1 WHERE id=:task_id"),
            {"task_id": task_id}
        )
        await conn.commit()


async def delete_task(task_id):
    async with get_db() as conn:
        await conn.execute(text("DELETE FROM tasks WHERE id=:task_id"), {"task_id": task_id})
        await conn.execute(text("DELETE FROM steps WHERE task_id=:task_id"), {"task_id": task_id})
        await conn.commit()


async def get_task_by_id(task_id: int):
    """Отримуємо одну таску з кроками"""
    async with get_db() as conn:
        result = await conn.execute(
            text("SELECT id, title, is_done FROM tasks WHERE id=:task_id"),
            {"task_id": task_id}
        )
        task = result.fetchone()

        if not task:
            return None

        result = await conn.execute(
            text("SELECT title, description, minutes FROM steps WHERE task_id=:task_id ORDER BY id"),
            {"task_id": task_id}
        )
        steps = [tuple(row) for row in result.fetchall()]

    return {
        "id": task[0],
        "title": task[1],
        "is_done": task[2],
        "steps": steps
    }


async def get_task_id_by_user_and_index(user_id: int, index: int):
    """Отримуємо task_id за індексом для юзера (для callback_data)"""
    async with get_db() as conn:
        result = await conn.execute(
            text("SELECT id FROM tasks WHERE user_id=:user_id ORDER BY id LIMIT 1 OFFSET :offset"),
            {"user_id": user_id, "offset": index - 1}
        )
        row = result.fetchone()

    return row[0] if row else None


async def get_tasks_with_steps(user_id):
    """Отримуємо всі таски з кроками одним запитом (JOIN)"""
    async with get_db() as conn:
        result = await conn.execute(
            text("""
                SELECT 
                    t.id, t.title, t.is_done,
                    s.title as step_title, 
                    s.description as step_description, 
                    s.minutes as step_minutes
                FROM tasks t
                LEFT JOIN steps s ON t.id = s.task_id
                WHERE t.user_id = :user_id
                ORDER BY t.id, s.id
            """),
            {"user_id": user_id}
        )
        rows = result.fetchall()

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
    async with get_db() as conn:
        result = await conn.execute(
            text("SELECT user_id FROM tasks WHERE id=:task_id"),
            {"task_id": task_id}
        )
        row = result.fetchone()

    return row[0] if row else None
