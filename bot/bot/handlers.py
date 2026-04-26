import asyncio
import logging

from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReactionTypeEmoji
from aiogram.fsm.context import FSMContext

from core.repository import *
from ai.generate import generate_plan
from bot.states import PlanState
from core.users import register_user

dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


async def send_typing(bot, chat_id: int):
    try:
        while True:
            await bot.send_chat_action(chat_id, "typing")
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass

@dp.message(Command("start"))
async def start(message: types.Message):
    username = message.from_user.username or "no_username"

    await register_user(
        message.from_user.id,
        username
    )

    await message.react([ReactionTypeEmoji(emoji="❤")])

    await message.answer(
        "👋 Привіт! Я AI Task Planner\n\n"
        "Команди:\n"
        "/plan\n"
        "/mytasks\n"
    )
@dp.message(Command("plan"))
async def plan(message: types.Message, state: FSMContext):
    await message.react([ReactionTypeEmoji(emoji="❤")])
    await state.set_state(PlanState.waiting_for_task)
    await message.answer("📝 Напиши задачу:")


@dp.message(PlanState.waiting_for_task)
async def process_task(message: types.Message, state: FSMContext):
    bot = message.bot
    task_text = message.text.strip()

    if not task_text:
        await message.answer("❌ Напиши нормальну задачу")
        return

    await message.answer("🤖 Думаю...")

    typing_task = asyncio.create_task(send_typing(bot, message.chat.id))

    try:
        steps = await generate_plan(task_text)
    finally:
        typing_task.cancel()

    if not steps:
        await message.answer("❌ Помилка генерації плану")
        await state.clear()
        return

    task_id = await create_task(message.from_user.id, task_text, steps)

    text = f"📌 Задача: {task_text}\n\n"

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
    await message.react([ReactionTypeEmoji(emoji="❤")])
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

    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.callback_query(F.data.startswith("task:"))
async def open_task(callback: types.CallbackQuery):
    index = int(callback.data.split(":")[1])
    tasks = await get_tasks(callback.from_user.id)

    if index < 1 or index > len(tasks):
        await callback.answer("❌ Помилка")
        return

    task_id, title, is_done = tasks[index - 1]
    steps = await get_steps(task_id)

    status = "✅" if is_done else "⏳"
    text = f"📌 Завдання {index}:\n{title}\n\nСтатус: {status}\n\n"

    if steps:
        text += "🧠 План:\n"
        total = 0

        for i, (t, d, m) in enumerate(steps, 1):
            text += f"{i}. {t} ({m} хв)\n"
            if d:
                text += f"   └ {d}\n"
            total += m

        text += f"\n⏱ Загальний час: {total} хв"
    else:
        text += "❌ Немає кроків"

    buttons = []

    if not is_done:
        buttons.append(InlineKeyboardButton(text="✅ Виконати", callback_data=f"done:{index}"))

    buttons.append(InlineKeyboardButton(text="🗑 Видалити", callback_data=f"delete:{index}"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_tasks")]
    ])

    await callback.answer()
    await callback.message.edit_text(text, reply_markup=keyboard)

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

    await callback.answer("✅ Виконано")
    await callback.message.edit_text(callback.message.text + "\n\n✅ Завершено")

@dp.callback_query(F.data.startswith("delete:"))
async def delete_callback(callback: types.CallbackQuery):
    index = int(callback.data.split(":")[1])
    tasks = await get_tasks(callback.from_user.id)

    if index < 1 or index > len(tasks):
        await callback.answer("❌ Помилка")
        return

    task_id, _, _ = tasks[index - 1]

    await delete_task(task_id)

    await callback.answer("🗑 Видалено")
    await callback.message.edit_text("🗑 Задача видалена")

@dp.callback_query(F.data == "back_to_tasks")
async def back_to_tasks(callback: types.CallbackQuery):
    tasks = await get_tasks(callback.from_user.id)

    await callback.answer()

    if not tasks:
        await callback.message.edit_text("📭 У тебе немає задач")
        return

    text = "📋 Ось твої завдання:\n\n"
    keyboard = []

    for index, (_, title, is_done) in enumerate(tasks, start=1):
        status = "✅" if is_done else "⏳"
        text += f"{index}. {title} {status}\n"

        keyboard.append([
            InlineKeyboardButton(text=f"📌 {index}", callback_data=f"task:{index}")
        ])

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))