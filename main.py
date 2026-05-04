import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot
from bot.handlers import dp

from core.models import init_db

import uvicorn

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

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