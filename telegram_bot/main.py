import os
from dotenv import load_dotenv

load_dotenv()

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from db import *
from ai import generate_plan

async def send_typing(chat_id: int):
    try:
        while True:
            await bot.send_chat_action(chat_id, "typing")
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass


logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()


# /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Привіт! Я AI Task Planner\n\n"
        "Команди:\n"
        "/plan <задача>\n"
        "/mytasks\n"
        "/done <id>\n"
        "/delete <id>"
    )

@dp.message(Command("plan"))
async def plan(message: types.Message):
    task_text = message.text.replace("/plan", "").strip()

    if not task_text:
        await message.answer("Напиши задачу після /plan")
        return
    #це робив гпт
    
    # повідомлення + typing
    await message.answer("🤖 Думаю...")

    typing_task = asyncio.create_task(send_typing(message.chat.id))

    try:
        steps = await generate_plan(task_text)
    finally:
        typing_task.cancel()  # зупиняємо typing

    if not steps:
        await message.answer("❌ Помилка генерації плану")
        return

    task_id = await create_task(message.from_user.id, task_text, steps)

    text = f"📌 Задача (ID {task_id}): {task_text}\n\n"

    total = 0
    for i, step in enumerate(steps, 1):
        total += step["minutes"]
        text += f"{i}. {step['title']} ({step['minutes']} хв)\n"

    text += f"\n⏱ Загальний час: {total} хв"

    await message.answer(text)

@dp.message(Command("mytasks"))
async def mytasks(message: types.Message):
    tasks = await get_tasks(message.from_user.id)

    if not tasks:
        await message.answer("У тебе немає задач")
        return

    text = "📋 Твої задачі:\n\n"

    for task_id, title, is_done in tasks:
        status = "✅" if is_done else "⏳"
        text += f"{task_id}. {title} {status}\n"

    await message.answer(text)

@dp.message(Command("done"))
async def done(message: types.Message):
    try:
        task_id = int(message.text.split()[1])
        await mark_done(task_id)
        await message.answer("✅ Задача виконана")
    except:
        await message.answer("❌ Використання: /done <id>")

@dp.message(Command("delete"))
async def delete(message: types.Message):
    try:
        task_id = int(message.text.split()[1])
        await delete_task(task_id)
        await message.answer("🗑 Задача видалена")
    except:
        await message.answer("❌ Використання: /delete <id>")

async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())