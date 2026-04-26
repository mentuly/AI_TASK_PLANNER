import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot

from bot.handlers import dp
from core.models import init_db

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())