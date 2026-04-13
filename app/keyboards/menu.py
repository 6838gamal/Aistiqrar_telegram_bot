from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from app.utils.translator import translator


def home_menu(lang="ar"):
    t = lambda key: translator.t(key, lang)
    keyboard = [
        [KeyboardButton(text=t("menu_job")),       KeyboardButton(text=t("menu_profile"))],
        [KeyboardButton(text=t("menu_categories")), KeyboardButton(text=t("menu_invite"))],
        [KeyboardButton(text=t("menu_channels")),   KeyboardButton(text=t("menu_settings"))],
        [KeyboardButton(text=t("menu_suggest")),    KeyboardButton(text=t("menu_help"))],
        [KeyboardButton(text=t("menu_start"))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def back_button(lang="ar"):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=translator.t("menu_back", lang))]],
        resize_keyboard=True
    )


def lang_keyboard(lang="ar"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=translator.t("lang_btn_ar", lang),
                callback_data="set_lang:ar"
            ),
            InlineKeyboardButton(
                text=translator.t("lang_btn_en", lang),
                callback_data="set_lang:en"
            ),
        ],
        [
            InlineKeyboardButton(
                text=translator.t("lang_btn_back", lang),
                callback_data="set_lang:back"
            ),
        ]
    ])
