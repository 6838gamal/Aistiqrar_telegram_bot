from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app.utils.translator import translator

def main_menu(lang="ar"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=translator.t("menu_start", lang))],
            [KeyboardButton(text=translator.t("menu_job", lang))],
            [KeyboardButton(text=translator.t("menu_profile", lang))],
            [KeyboardButton(text=translator.t("menu_categories", lang))],
            [KeyboardButton(text=translator.t("menu_suggest", lang))],
            [KeyboardButton(text=translator.t("menu_invite", lang))],
            [KeyboardButton(text=translator.t("menu_help", lang))]
        ],
        resize_keyboard=True
    )
