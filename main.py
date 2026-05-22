import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from aiogram import Bot
from bot.handlers import dp

from core.models import init_db

import uvicorn


def load_secret(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value:
        return value

    secret_path = os.getenv(f"{name}_FILE", f"/run/secrets/{name.lower()}")
    secret_file = Path(secret_path)
    if secret_file.exists():
        return secret_file.read_text().strip()

    return default

load_dotenv()

BOT_TOKEN = load_secret("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is required")

bot = Bot(token=BOT_TOKEN)


async def start_bot():
    await dp.start_polling(bot)


async def start_site():
    config = uvicorn.Config(
        "site_F.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await init_db()

    await asyncio.gather(
        start_bot(),
        start_site()
    )


if __name__ == "__main__":
    asyncio.run(main())