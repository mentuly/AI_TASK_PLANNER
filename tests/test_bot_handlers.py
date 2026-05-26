import asyncio

import pytest

from bot import handlers


class DummyUser:
    def __init__(self, user_id=1, username="tester"):
        self.id = user_id
        self.username = username


class DummyChat:
    def __init__(self, chat_id=10):
        self.id = chat_id


class DummyMessage:
    def __init__(self, text="", user_id=1, username="tester"):
        self.from_user = DummyUser(user_id, username)
        self.chat = DummyChat()
        self.bot = object()
        self.text = text
        self.answers = []
        self.reactions = []

    async def answer(self, text, reply_markup=None):
        self.answers.append((text, reply_markup))

    async def react(self, reactions):
        self.reactions.append(reactions)


class DummyState:
    def __init__(self):
        self.state = None
        self.cleared = False

    async def set_state(self, state):
        self.state = state

    async def clear(self):
        self.cleared = True


class DummyTask:
    def __init__(self):
        self.cancelled = False

    def cancel(self):
        self.cancelled = True


class DummyCallbackMessage:
    def __init__(self, text="task text"):
        self.text = text
        self.edited_text = None

    async def edit_text(self, text, reply_markup=None):
        self.edited_text = text


class DummyCallback:
    def __init__(self, data, user_id=1, message_text="task text"):
        self.data = data
        self.from_user = DummyUser(user_id)
        self.message = DummyCallbackMessage(message_text)
        self.answers = []

    async def answer(self, text="", show_alert=False):
        self.answers.append((text, show_alert))


@pytest.mark.asyncio
async def test_build_tasks_markup_empty(monkeypatch):
    async def fake_get_tasks(user_id):
        return []

    monkeypatch.setattr("bot.handlers.get_tasks", fake_get_tasks)

    text, markup = await handlers.build_tasks_markup(1)

    assert "немає задач" in text
    assert markup is None


@pytest.mark.asyncio
async def test_build_tasks_markup_with_tasks(monkeypatch):
    async def fake_get_tasks(user_id):
        return [(101, "Task A", 0)]

    monkeypatch.setattr("bot.handlers.get_tasks", fake_get_tasks)

    text, markup = await handlers.build_tasks_markup(1)

    assert "Task A" in text
    assert markup is not None
    assert markup.inline_keyboard[0][0].callback_data == "task:101"


@pytest.mark.asyncio
async def test_process_task_empty_text():
    message = DummyMessage(text="   ")
    state = DummyState()

    await handlers.process_task(message, state)

    assert any("❌ Напиши нормальну задачу" in answer for answer, _ in message.answers)
    assert state.cleared is False


@pytest.mark.asyncio
async def test_process_task_success(monkeypatch):
    message = DummyMessage(text="Write a plan", user_id=5)
    state = DummyState()
    dummy_task = DummyTask()

    async def fake_generate_plan(task_text):
        return [{"title": "Step 1", "description": "Desc", "minutes": 20}]

    async def fake_create_task(user_id, task_text, steps):
        return 77

    def make_task(coro):
        coro.close()
        return dummy_task

    monkeypatch.setattr("bot.handlers.generate_plan", fake_generate_plan)
    monkeypatch.setattr("bot.handlers.create_task", fake_create_task)
    monkeypatch.setattr("bot.handlers.asyncio.create_task", make_task)

    await handlers.process_task(message, state)

    assert any("Задача:" in answer for answer, _ in message.answers)
    assert state.cleared is True
    assert dummy_task.cancelled is True


@pytest.mark.asyncio
async def test_done_callback_already_done(monkeypatch):
    callback = DummyCallback("done:1", user_id=1)

    async def fake_get_task_owner(task_id):
        return 1

    async def fake_get_task_by_id(task_id):
        return {"id": 1, "is_done": True}

    monkeypatch.setattr("bot.handlers.get_task_owner", fake_get_task_owner)
    monkeypatch.setattr("bot.handlers.get_task_by_id", fake_get_task_by_id)

    await handlers.done_callback(callback)

    assert callback.answers[-1][0] == "⚠️ Вже виконано"


@pytest.mark.asyncio
async def test_done_callback_success(monkeypatch):
    callback = DummyCallback("done:1", user_id=1, message_text="Original")

    async def fake_get_task_owner(task_id):
        return 1

    async def fake_get_task_by_id(task_id):
        return {"id": 1, "is_done": False}

    async def fake_mark_done(task_id):
        callback.marked = task_id

    monkeypatch.setattr("bot.handlers.get_task_owner", fake_get_task_owner)
    monkeypatch.setattr("bot.handlers.get_task_by_id", fake_get_task_by_id)
    monkeypatch.setattr("bot.handlers.mark_done", fake_mark_done)

    await handlers.done_callback(callback)

    assert callback.answers[-1][0] == "✅ Виконано"
    assert "✅ Завершено" in callback.message.edited_text


@pytest.mark.asyncio
async def test_delete_callback_forbidden(monkeypatch):
    callback = DummyCallback("delete:1", user_id=2)

    async def fake_get_task_owner(task_id):
        return 1

    monkeypatch.setattr("bot.handlers.get_task_owner", fake_get_task_owner)

    await handlers.delete_callback(callback)

    assert callback.answers[-1][0] == "❌ Це не твоя задача"
    assert callback.answers[-1][1] is True


@pytest.mark.asyncio
async def test_open_site_sends_auth_link(monkeypatch):
    message = DummyMessage(text="", user_id=11)

    async def fake_create_auth_token(user_id):
        return "token-abc"

    monkeypatch.setattr("bot.handlers.create_auth_token", fake_create_auth_token)

    await handlers.open_site(message)

    assert any("Твій доступ до сайту" in text for text, _ in message.answers)
    assert any(reply_markup is not None for _, reply_markup in message.answers)


@pytest.mark.asyncio
async def test_start_registers_user_and_sends_greeting(monkeypatch):
    message = DummyMessage(text="", user_id=12, username="hello")
    called = {}

    async def fake_register_user(user_id, username):
        called["user_id"] = user_id
        called["username"] = username

    monkeypatch.setattr("bot.handlers.register_user", fake_register_user)

    await handlers.start(message)

    assert called == {"user_id": 12, "username": "hello"}
    assert any("👋 Привіт" in text for text, _ in message.answers)


@pytest.mark.asyncio
async def test_plan_sets_state_and_prompts():
    message = DummyMessage(text="", user_id=15)
    state = DummyState()

    await handlers.plan(message, state)

    assert state.state == handlers.PlanState.waiting_for_task
    assert any("📝 Напиши задачу:" in text for text, _ in message.answers)


@pytest.mark.asyncio
async def test_mytasks_uses_build_tasks_markup(monkeypatch):
    message = DummyMessage(text="", user_id=21)

    async def fake_build_tasks_markup(user_id):
        return "content", object()

    monkeypatch.setattr("bot.handlers.build_tasks_markup", fake_build_tasks_markup)

    await handlers.mytasks(message)
    assert any("content" in text for text, _ in message.answers)


@pytest.mark.asyncio
async def test_back_to_tasks_edits_text(monkeypatch):
    callback = DummyCallback("back_to_tasks", user_id=2)

    async def fake_build_tasks_markup(user_id):
        return "tasks text", object()

    monkeypatch.setattr("bot.handlers.build_tasks_markup", fake_build_tasks_markup)

    await handlers.back_to_tasks(callback)

    assert callback.message.edited_text == "tasks text"


@pytest.mark.asyncio
async def test_open_task_success(monkeypatch):
    callback = DummyCallback("task:1", user_id=2, message_text="Original")

    async def fake_get_task_id_by_user_and_index(user_id, index):
        return 1

    async def fake_get_task_by_id(task_id):
        return {
            "id": 1,
            "title": "Task One",
            "is_done": False,
            "steps": [("Step A", "Desc", 10)]
        }

    monkeypatch.setattr("bot.handlers.get_task_id_by_user_and_index", fake_get_task_id_by_user_and_index)
    monkeypatch.setattr("bot.handlers.get_task_by_id", fake_get_task_by_id)

    await handlers.open_task(callback)

    assert "Task One" in callback.message.edited_text
    assert "Step A" in callback.message.edited_text


@pytest.mark.asyncio
async def test_delete_callback_success(monkeypatch):
    callback = DummyCallback("delete:1", user_id=2)

    async def fake_get_task_owner(task_id):
        return 2

    async def fake_get_task_by_id(task_id):
        return {"id": 1}

    async def fake_delete_task(task_id):
        callback.deleted = task_id

    monkeypatch.setattr("bot.handlers.get_task_owner", fake_get_task_owner)
    monkeypatch.setattr("bot.handlers.get_task_by_id", fake_get_task_by_id)
    monkeypatch.setattr("bot.handlers.delete_task", fake_delete_task)

    await handlers.delete_callback(callback)

    assert callback.answers[-1][0] == "🗑 Видалено"
    assert callback.message.edited_text == "🗑 Задача видалена"
