import os
from dotenv import load_dotenv

load_dotenv()

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F

from db import *
from ai import generate_plan

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from aiogram.types import ( 
    KeyboardButton,
    ReplyKeyboardMarkup,
    Message,
    ReactionTypeEmoji
)

class PlanState(StatesGroup):
    waiting_for_task = State()

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


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.react([ReactionTypeEmoji(emoji = "❤")])
    await message.answer(
        "👋 Привіт! Я AI Task Planner\n\n"
        "Команди:\n"
        "/plan \n"
        "/mytasks\n"
    )

@dp.message(Command("plan"))
async def plan(message: types.Message, state: FSMContext):
    await message.react([ReactionTypeEmoji(emoji = "❤")])
    await state.set_state(PlanState.waiting_for_task)
    await message.answer("📝 Напиши задачу:")

@dp.message(PlanState.waiting_for_task)
async def process_task(message: types.Message, state: FSMContext):
    task_text = message.text.strip()

    if not task_text:
        await message.answer("❌ Напиши нормальну задачу")
        return

    await message.answer("🤖 Думаю...")

    typing_task = asyncio.create_task(send_typing(message.chat.id))

    try:
        steps = await generate_plan(task_text)
    finally:
        typing_task.cancel()

    if not steps:
        await message.answer("❌ Помилка генерації плану")
        await state.clear()
        return

    task_id = await create_task(message.from_user.id, task_text, steps)

    text = f"📌 Задача (ID {task_id}): {task_text}\n\n"

    total = 0
    for i, step in enumerate(steps, 1):
        title = step.get("title", "Без назви")
        minutes = step.get("minutes", 10)

        total += minutes
        text += f"{i}. {title} ({minutes} хв)\n"

    text += f"\n⏱ Загальний час: {total} хв"

    await message.answer(text)

    await state.clear()

@dp.message(Command("mytasks"))
async def mytasks(message: types.Message):
    await message.react([ReactionTypeEmoji(emoji = "❤")])
    tasks = await get_tasks(message.from_user.id)

    if not tasks:
        await message.answer("📭 У тебе немає задач")
        return

    text = "📋 Ось твої завдання:\n\n"
    keyboard = []

    for index, (task_id, title, is_done) in enumerate(tasks, start=1):
        status = "✅" if is_done else "⏳"
        text += f"{index}. {title} {status}\n"

        keyboard.append([
            InlineKeyboardButton(
                text=f"📌 {index}",
                callback_data=f"task:{index}"
            )
        ])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(text, reply_markup=markup)

@dp.callback_query(F.data.startswith("task:"))
async def open_task(callback: types.CallbackQuery):
    index = int(callback.data.split(":")[1])
    tasks = await get_tasks(callback.from_user.id)

    if index < 1 or index > len(tasks):
        await callback.answer("❌ Помилка")
        return

    task_id, title, is_done = tasks[index - 1]

    status = "✅" if is_done else "⏳"

    steps = await get_steps(task_id)

    text = f"📌 Завдання {index}:\n{title}\n\nСтатус: {status}\n\n"

    if steps:
        text += "🧠 План:\n"
        total = 0

        for i, step in enumerate(steps, 1):
            step_title, step_description, step_minutes = step

            text += f"{i}. {step_title} ({step_minutes} хв)\n"

            if step_description:
                text += f"   └ {step_description}\n"

            total += step_minutes

        text += f"\n⏱ Загальний час: {total} хв"
    else:
        text += "❌ Немає кроків"

    buttons = []

    if not is_done:
        buttons.append(
            InlineKeyboardButton(
                text="✅ Виконати",
                callback_data=f"done:{index}"
            )
        )

    buttons.append(
        InlineKeyboardButton(
            text="🗑 Видалити",
            callback_data=f"delete:{index}"
        )
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="back_to_tasks"
            )
        ]
    ])

    await callback.message.delete()
    await callback.message.answer(text, reply_markup=keyboard)

# @dp.message(Command("done"))
# async def done(message: types.Message):
#     try:
#         task_id = int(message.text.split()[1])
#         await mark_done(task_id)
#         await message.answer("✅ Задача виконана")
#     except:
#         await message.answer("❌ Використання: /done <id>")

@dp.callback_query(F.data.startswith("done:"))
async def done_callback(callback: types.CallbackQuery):
    index = int(callback.data.split(":")[1])
    tasks = await get_tasks(callback.from_user.id)

    if index < 1 or index > len(tasks):
        await callback.answer("❌ Помилка")
        return

    task_id, _, is_done = tasks[index - 1]

    if is_done:
        await callback.answer("⚠️ Вже виконано")
        return

    await mark_done(task_id)

    await callback.answer("✅ Завдання виконано")

    await callback.answer("✅ Виконано")
    await callback.message.edit_text(
        callback.message.text + "\n\n✅ Завершено"
    )

# @dp.message(Command("delete"))
# async def delete(message: types.Message):
#     try:
#         task_id = int(message.text.split()[1])
#         await delete_task(task_id)
#         await message.answer("🗑 Задача видалена")
#     except:
#         await message.answer("❌ Використання: /delete <id>")

@dp.callback_query(F.data.startswith("delete:"))
async def delete_callback(callback: types.CallbackQuery):
    index = int(callback.data.split(":")[1])
    tasks = await get_tasks(callback.from_user.id)

    if index < 1 or index > len(tasks):
        await callback.answer("❌ Помилка")
        return

    task_id, _, _ = tasks[index - 1]

    await delete_task(task_id)

    await callback.answer("🗑 Завдання видалено")

    await callback.answer("🗑 Видалено")
    await callback.message.edit_text("🗑 Задача видалена")

@dp.callback_query(F.data == "back_to_tasks")
async def back_to_tasks(callback: types.CallbackQuery):
    tasks = await get_tasks(callback.from_user.id)

    await callback.answer("⬅️ Назад")

    if not tasks:
        await callback.message.edit_text("📭 У тебе немає задач")
        return

    text = "📋 Ось твої завдання:\n\n"
    keyboard = []

    for index, (task_id, title, is_done) in enumerate(tasks, start=1):
        status = "✅" if is_done else "⏳"
        text += f"{index}. {title} {status}\n"

        keyboard.append([
            InlineKeyboardButton(
                text=f"📌 {index}",
                callback_data=f"task:{index}"
            )
        ])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await callback.message.edit_text(text, reply_markup=markup)

# або можна написати так:
# @dp.callback_query(F.data.startswith("btn_click"))
# async def button_handler(callback: CallbackQuery):
#     action = callback.data.split(":")[1]

#     if action == "done":
#         await callback.answer("✅ Завдання виконано")

#     elif action == "delete":
#         await callback.answer("🗑 Видалено")

#     elif action == "back":
#         await callback.answer("⬅️ Назад")

# callback_data="btn_click:done"
# callback_data="btn_click:delete"
# callback_data="btn_click:back"

async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())