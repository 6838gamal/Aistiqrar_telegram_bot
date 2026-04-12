from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app.utils.translator import translator


def home_menu(lang="ar"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=f"🚀 start | {translator.t('menu_start', lang)}"
                )
            ],
            [
                KeyboardButton(
                    text=f"💼 job | {translator.t('menu_job', lang)}"
                )
            ],
            [
                KeyboardButton(
                    text=f"📁 profile | {translator.t('menu_profile', lang)}"
                )
            ],
            [
                KeyboardButton(
                    text=f"🧭 categories | {translator.t('menu_categories', lang)}"
                )
            ],
            [
                KeyboardButton(
                    text=f"💡 suggest | {translator.t('menu_suggest', lang)}"
                )
            ],
            [
                KeyboardButton(
                    text=f"👥 invite | {translator.t('menu_invite', lang)}"
                )
            ],
            [
                KeyboardButton(
                    text=f"❓ help | {translator.t('menu_help', lang)}"
                )
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def back_button(lang="ar"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🔙 back | رجوع"
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
