import pytest
from core import db
from core.models import init_db
from core.auth import create_auth_token, get_user_by_token


@pytest.fixture(autouse=True)
def temp_auth_db(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "DB_NAME", str(tmp_path / "test_auth.db"))
    yield


@pytest.mark.asyncio
async def test_auth_token_lifecycle():
    await init_db()

    token = await create_auth_token(123)
    assert isinstance(token, str)
    assert token

    user_id = await get_user_by_token(token)
    assert user_id == 123

    user_id_after = await get_user_by_token(token)
    assert user_id_after is None
