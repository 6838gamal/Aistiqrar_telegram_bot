from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.translator import translator


def home_menu(lang="ar"):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=translator.t("menu_start", lang), callback_data="page_start")],
            [InlineKeyboardButton(text=translator.t("menu_job", lang), callback_data="page_job")],
            [InlineKeyboardButton(text=translator.t("menu_profile", lang), callback_data="page_profile")],
            [InlineKeyboardButton(text=translator.t("menu_categories", lang), callback_data="page_categories")],
            [InlineKeyboardButton(text=translator.t("menu_suggest", lang), callback_data="page_suggest")],
            [InlineKeyboardButton(text=translator.t("menu_invite", lang), callback_data="page_invite")],
            [InlineKeyboardButton(text=translator.t("menu_help", lang), callback_data="page_help")]
        ]
    )


def back_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="back_home")]
        ]
    )
