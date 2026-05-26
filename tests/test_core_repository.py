import pytest
from core import db
from core.models import init_db
from core.repository import (
    create_task,
    get_tasks,
    get_steps,
    mark_done,
    delete_task,
    get_task_by_id,
    get_task_id_by_user_and_index,
    get_tasks_with_steps,
    get_task_owner,
)
from core.users import register_user, get_user_by_username


@pytest.fixture(autouse=True)
def temp_db(monkeypatch, tmp_path):
    temp_db_path = tmp_path / "test_tasks.db"
    monkeypatch.setattr(db, "DB_NAME", str(temp_db_path))
    yield


@pytest.mark.asyncio
async def test_repository_task_lifecycle():
    await init_db()

    await register_user(55, "tester")
    user_row = await get_user_by_username("tester")

    assert user_row is not None
    assert user_row[1] == 55

    task_id = await create_task(55, "My Task", [{"title": "Step One", "description": "Desc", "minutes": 5}])
    assert task_id > 0

    task_list = await get_tasks(55)
    assert len(task_list) == 1
    assert task_list[0][1] == "My Task"

    steps = await get_steps(task_id)
    assert steps == [("Step One", "Desc", 5)]

    owner = await get_task_owner(task_id)
    assert owner == 55

    task_id_by_index = await get_task_id_by_user_and_index(55, 1)
    assert task_id_by_index == task_id

    task = await get_task_by_id(task_id)
    assert task["id"] == task_id
    assert task["title"] == "My Task"
    assert task["steps"][0][0] == "Step One"

    tasks_with_steps = await get_tasks_with_steps(55)
    assert len(tasks_with_steps) == 1
    assert tasks_with_steps[0]["id"] == task_id
    assert tasks_with_steps[0]["steps"][0]["title"] == "Step One"

    await mark_done(task_id)
    task_after_done = await get_task_by_id(task_id)
    assert task_after_done["is_done"] == 1

    await delete_task(task_id)
    assert await get_task_by_id(task_id) is None
