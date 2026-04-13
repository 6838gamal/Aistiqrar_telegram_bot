from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.data.categories import CATEGORIES
from app.utils.translator import translator


def categories_keyboard(lang: str, selected: list[int]) -> InlineKeyboardMarkup:
    cats = CATEGORIES.get(lang, CATEGORIES["ar"])
    rows = []

    items = list(enumerate(cats))
    for i in range(0, len(items), 2):
        row = []
        for idx, (emoji, name) in items[i:i+2]:
            check = "✅" if idx in selected else "☐"
            row.append(InlineKeyboardButton(
                text=f"{check} {emoji} {name}",
                callback_data=f"cat_toggle:{idx}"
            ))
        rows.append(row)

    rows.append([
        InlineKeyboardButton(
            text=translator.t("cat_save", lang),
            callback_data="cat_save"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)
