from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo, InlineKeyboardButton
from translations import TRANSLATIONS
from config import CHANNEL_ID, REGISTRATION_URL, MINI_APP_URL


def language_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Кыргызский", callback_data="lang_kg"),
        InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="English", callback_data="lang_en")
    )
    return builder.as_markup()


def channel_keyboard(lang):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=TRANSLATIONS[lang]['channel_btn'],
            url=f"https://t.me/{CHANNEL_ID}"),
        InlineKeyboardButton(
            text=TRANSLATIONS[lang]['check_btn'],
            callback_data="check_subscription"
        )
    )
    return builder.as_markup()


def main_menu_keyboard(lang):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=TRANSLATIONS[lang]['register_btn'],
            callback_data="registration"
        ),
        InlineKeyboardButton(
            text=TRANSLATIONS[lang]['instruction_btn'],
            callback_data="instruction"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=TRANSLATIONS[lang]['language_btn'],
            callback_data="change_language"
        ),
        InlineKeyboardButton(
            text=TRANSLATIONS[lang]['help_btn'],
            callback_data="help"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=TRANSLATIONS[lang]['signal_btn'],
            callback_data="get_signal"
        )
    )
    return builder.as_markup()


def back_keyboard(lang, to='main_menu'):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text=TRANSLATIONS[lang]['back_btn'],
        callback_data=to
    ))
    return builder.as_markup()


def registration_keyboard(lang):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=TRANSLATIONS[lang]['register_btn'],
            callback_data="real_registration"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=TRANSLATIONS[lang]['back_btn'],
            callback_data="main_menu"
        )
    )
    return builder.as_markup()


def signal_keyboard(lang):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=TRANSLATIONS[lang]['select_game_btn'],
            web_app=WebAppInfo(url=MINI_APP_URL)
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=TRANSLATIONS[lang]['back_btn'],
            callback_data="main_menu"
        )
    )
    return builder.as_markup()
