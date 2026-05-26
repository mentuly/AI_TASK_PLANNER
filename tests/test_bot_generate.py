import pytest

from bot.ai import generate


class DummyMessage:
    def __init__(self, content):
        self.content = content


class DummyChoice:
    def __init__(self, message):
        self.message = message


class DummyResponse:
    def __init__(self, content):
        self.choices = [DummyChoice(DummyMessage(content))]


@pytest.mark.asyncio
async def test_generate_plan_parses_json(monkeypatch):
    async def fake_create(*, model, messages):
        return DummyResponse('[{"title": "Step A", "description": "Desc", "minutes": 10}]')

    monkeypatch.setattr(generate.client.chat.completions, "create", fake_create)

    steps = await generate.generate_plan("Test task")
    assert steps == [{"title": "Step A", "description": "Desc", "minutes": 10}]


@pytest.mark.asyncio
async def test_generate_plan_invalid_json_returns_empty(monkeypatch):
    async def fake_create(*, model, messages):
        return DummyResponse('not json')

    monkeypatch.setattr(generate.client.chat.completions, "create", fake_create)

    steps = await generate.generate_plan("Test task")
    assert steps == []
