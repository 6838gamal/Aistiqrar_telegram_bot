from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.database.db import get_user, get_favorites
from app.keyboards.menu import back_button
from app.utils.translator import translator

router = Router()


@router.callback_query(F.data == "page_favorites")
async def page_favorites(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")

    favs = get_favorites(call.from_user.id)

    if not favs:
        text = "⭐ *مفضلتك فارغة*\n\nلم تقم بإضافة أي مشروع إلى المفضلة بعد." \
               if lang == "ar" else \
               "⭐ *Your favorites list is empty*\n\nYou haven't saved any projects yet."
        await call.message.edit_text(text, reply_markup=back_button(lang), parse_mode="Markdown")
        await call.answer()
        return

    header = f"⭐ *مفضلتك* — {len(favs)} مشروع\n\n" if lang == "ar" \
             else f"⭐ *Your Favorites* — {len(favs)} projects\n\n"

    buttons = []
    for i, fav in enumerate(favs[:20], 1):
        title = fav["title"][:40] + ("..." if len(fav["title"]) > 40 else "")
        saved = fav.get("saved_at", "")[:10]
        buttons.append([
            InlineKeyboardButton(text=f"📌 {title}", url=fav["link"])
        ])

    back_label = translator.t("menu_back", lang)
    buttons.append([InlineKeyboardButton(text=back_label, callback_data="back_home")])

    await call.message.edit_text(
        header + "\n".join(
            f"{i}. [{fav['title'][:35]}...]({fav['link']})"
            if len(fav["title"]) > 35
            else f"{i}. [{fav['title']}]({fav['link']})"
            for i, fav in enumerate(favs[:20], 1)
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    await call.answer()
