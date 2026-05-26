import importlib
import os


def test_load_secret_prefers_env(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "123456:TEST_TOKEN")
    monkeypatch.delenv("BOT_TOKEN_FILE", raising=False)

    module = importlib.reload(importlib.import_module("bot.main"))

    assert module.BOT_TOKEN == "123456:TEST_TOKEN"
    assert module.load_secret("NON_EXISTENT", "fallback") == "fallback"
