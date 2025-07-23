import random
from datetime import datetime
import sqlite3
from config import ADMIN_ID

def generate_fake_win():
    return (
        f"👤Пользователь с ID: {random.randint(10000000, 99999999)}\n"
        f"🎉Выиграл: {random.randint(15000, 500000)}₽ \n"
        f"💰 Ставка: {random.randint(5000, 15000)}₽ \n"
        f"💣Количество мин: {random.randint(2, 8)}\n"
        f"🤖(сигнал был выдан в {datetime.now().strftime('%H:%M')} по мск)\n\n/start"
    )

async def send_daily_fake_win(bot):
    message = generate_fake_win()
    
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id != ?", (ADMIN_ID,))
        users = [row[0] for row in cursor.fetchall()]
    
    for uid in users:
        try:
            await bot.send_message(uid, message)
        except Exception as e:
            print(f"Ошибка при отправке фейкового выигрыша {uid}: {e}")
