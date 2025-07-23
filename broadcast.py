from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID
import sqlite3
import asyncio

router = Router()

class Broadcast(StatesGroup):
    waiting_for_message = State()

@router.message(Command("broadcast"))
async def broadcast_start(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return await msg.answer("⛔ Только админ может использовать эту команду.")
    
    await state.set_state(Broadcast.waiting_for_message)
    await msg.answer("📨 Отправьте сообщение для рассылки (можно с фото).")

@router.message(Broadcast.waiting_for_message)
async def broadcast_send(msg: Message, state: FSMContext, bot):
    await state.clear()
    text = msg.text or msg.caption
    photo = msg.photo[-1].file_id if msg.photo else None

    with sqlite3.connect('bot.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id != ?", (ADMIN_ID,))
        user_ids = [row[0] for row in cursor.fetchall()]
    
    sent = 0
    for uid in user_ids:
        try:
            if photo:
                await bot.send_photo(uid, photo, caption=text)
            else:
                await bot.send_message(uid, text)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            print(f"Ошибка отправки пользователю {uid}: {e}")
    
    await msg.answer(f"✅ Рассылка завершена. Успешно отправлено: {sent}")
