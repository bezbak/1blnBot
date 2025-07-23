import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InputMediaPhoto, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_USERNAME, CHANNEL_ID, WELCOME_IMAGE, REGISTRATION_URL, ADMIN_ID
from broadcast import router as broadcast_router
from daily_fake_win import send_daily_fake_win
from database import init_db, get_user, create_user, update_user, save_message_id, get_message_id, mark_user_registered, is_user_authenticated, is_user_has_lang, is_user_sub
from keyboards import language_keyboard, channel_keyboard, main_menu_keyboard, back_keyboard, registration_keyboard, signal_keyboard
from translations import TRANSLATIONS
from database import get_user
import aiocron

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(broadcast_router)
# Инициализация базы данных
init_db()

@aiocron.crontab('0 21 * * *')  # каждый день в 12:00
async def daily_task():
    await send_daily_fake_win(bot)


async def edit_message(user_id: int, text: str, reply_markup=None, photo: str = None):
    message_id = get_message_id(user_id)
    if message_id:
        try:
            if photo:
                await bot.edit_message_media(
                    chat_id=user_id,
                    message_id=message_id,
                    media=InputMediaPhoto(media=photo, caption=text),
                    reply_markup=reply_markup
                )
            else:
                await bot.edit_message_text(
                    chat_id=user_id,
                    message_id=message_id,
                    text=text,
                    reply_markup=reply_markup
                )
            return True
        except Exception as e:
            logger.error(f"Failed to edit message: {e}")

    # Если редактирование не удалось, отправляем новое сообщение
    if photo:
        msg = await bot.send_photo(chat_id=user_id, photo=photo, caption=text, reply_markup=reply_markup)
    else:
        msg = await bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)

    save_message_id(user_id, msg.message_id)
    return True


async def check_channel_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=f"@{CHANNEL_ID}", user_id=user_id)
        
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Subscription check error: {e}")
        return False


@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    create_user(user_id)

    # Удаляем предыдущие сообщения
    try:
        await message.delete()
    except:
        pass
    lang = is_user_has_lang(user_id=user_id)
    if lang and not is_user_sub(user_id=user_id):
        await edit_message(
            user_id=user_id,
            text=TRANSLATIONS[lang]['subscribe_text'],
            reply_markup=channel_keyboard(lang)
        )
    elif is_user_sub(user_id=user_id):
        try:
            await message.delete()
        except:
            pass

        # Путь к изображению
        image_path = os.path.join("images", "main.png")
        photo = FSInputFile(image_path)

        # Отправляем новое сообщение с фото и кнопками
        await bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=TRANSLATIONS[lang]['welcome_text'],
            reply_markup=main_menu_keyboard(lang, message.from_user.id)
        )
    else:
        msg = await message.answer(
            text=TRANSLATIONS['ru']['choose_language'],
            reply_markup=language_keyboard()
        )
        save_message_id(user_id, msg.message_id)

@dp.message(Command("reg_ch"))
async def reg_command(message: types.Message):
    user_id = message.from_user.id
    # Удаляем предыдущие сообщения
    try:
        await message.delete()
    except:
        pass
    user = get_user(user_id)
    reg = is_user_authenticated(user_id=user_id)
    
    lang = user[1] if user else 'ru'
    
    await edit_message(
        user_id=user_id,
        text= f"{'Зареган' if reg else 'Не зареган'}",
        reply_markup=channel_keyboard(lang)
    )

@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def process_language(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang_code = callback.data.split("_")[1]
    lang = {'kg': 'kg', 'ru': 'ru', 'en': 'en'}[lang_code]

    update_user(user_id, lang=lang)
    await edit_message(
        user_id=user_id,
        text=TRANSLATIONS[lang]['subscribe_text'],
        reply_markup=channel_keyboard(lang)
    )


@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'ru'

    is_subscribed = await check_channel_subscription(user_id)
    update_user(user_id, is_subscribed=is_subscribed)

    if is_subscribed:
        try:
            await callback.message.delete()
        except:
            pass

        # Путь к изображению
        image_path = os.path.join("images", "main.png")
        photo = FSInputFile(image_path)

        # Отправляем новое сообщение с фото и кнопками
        await bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=TRANSLATIONS[lang]['welcome_text'],
            reply_markup=main_menu_keyboard(lang, callback.from_user.id)
        )
    else:
        await callback.answer(
            text=TRANSLATIONS[lang]['not_subscribed'],
            show_alert=True
        )


@dp.callback_query(lambda c: c.data == "main_menu")
async def main_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'ru'

    try:
        await callback.message.delete()
    except:
        pass

    # Путь к изображению
    image_path = os.path.join("images", "main.png")
    photo = FSInputFile(image_path)

    # Отправляем новое сообщение с фото и кнопками
    await bot.send_photo(
        chat_id=user_id,
        photo=photo,
        caption=TRANSLATIONS[lang]['welcome_text'],
        reply_markup=main_menu_keyboard(lang, callback.from_user.id)
    )


@dp.callback_query(lambda c: c.data == "registration")
async def registration_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'ru'

    try:
        await callback.message.delete()
    except:
        pass

    image_path = os.path.join("images", "register.png")
    photo = FSInputFile(image_path)

    await bot.send_photo(
        chat_id=user_id,
        photo=photo,
        caption=TRANSLATIONS[lang]['registration_text'],
        reply_markup=registration_keyboard(lang)
    )


@dp.callback_query(lambda c: c.data == "real_registration")
async def real_registration_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    mark_user_registered(user_id)

    lang = get_user(user_id)[1] or 'ru'

    await callback.message.answer(
        text=TRANSLATIONS[lang]['registration_link_msg'],
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=TRANSLATIONS[lang]['open_register_btn'], url=REGISTRATION_URL)]
            ]
        )
    )


@dp.callback_query(lambda c: c.data == "instruction")
async def instruction_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'ru'

    await edit_message(
        user_id=user_id,
        text=TRANSLATIONS[lang]['instruction_text'],
        reply_markup=back_keyboard(lang, 'main_menu')
    )


@dp.callback_query(lambda c: c.data == "help")
async def help_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'ru'

    await edit_message(
        user_id=user_id,
        text=f"{TRANSLATIONS[lang]['contact_admin_text']}: {ADMIN_USERNAME}",
        reply_markup=back_keyboard(lang, 'main_menu')
    )


@dp.callback_query(lambda c: c.data == "change_language")
async def change_language_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await edit_message(
        user_id=user_id,
        text=TRANSLATIONS['ru']['choose_language'],
        reply_markup=language_keyboard()
    )


@dp.callback_query(lambda c: c.data == "get_signal")
async def get_signal_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'ru'
    is_registered = user[3] if user else False

    if not is_registered:
        await callback.answer(
            text=TRANSLATIONS[lang]['not_registered'],
            show_alert=True
        )
        return

    await edit_message(
        user_id=user_id,
        text=TRANSLATIONS[lang]['select_game_text'],
        reply_markup=signal_keyboard(lang)
    )
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
