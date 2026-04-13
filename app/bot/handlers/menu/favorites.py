from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.database.db import get_user, get_favorites
from app.utils.translator import translator
from app.utils.formatting import SEP, SEP2

router = Router()


@router.callback_query(F.data == "page_favorites")
async def page_favorites(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    favs = get_favorites(call.from_user.id)
    back_label = translator.t("menu_back", lang)

    if not favs:
        if lang == "ar":
            text = (
                f"{SEP}\n"
                f"⭐ *مفضلتك*\n"
                f"{SEP}\n\n"
                f"لم تقم بإضافة أي مشروع إلى المفضلة بعد.\n\n"
                f"💡 *كيف تضيف مشروعاً؟*\n"
                f"{SEP2}\n"
                f"① افتح أي مشروع من قسم *فرصة اليوم* أو *الفئات*\n"
                f"② اضغط على زر ⭐ *إضافة إلى المفضلة*\n"
                f"③ سيُحفظ المشروع هنا تلقائياً\n"
                f"{SEP}"
            )
        else:
            text = (
                f"{SEP}\n"
                f"⭐ *Your Favorites*\n"
                f"{SEP}\n\n"
                f"You haven't saved any projects yet.\n\n"
                f"💡 *How to add a project?*\n"
                f"{SEP2}\n"
                f"① Open any project from *Today's Job* or *Categories*\n"
                f"② Tap the ⭐ *Add to Favorites* button\n"
                f"③ The project will be saved here automatically\n"
                f"{SEP}"
            )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=back_label, callback_data="back_home")]
        ])
        await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        await call.answer()
        return

    if lang == "ar":
        header = (
            f"{SEP}\n"
            f"⭐ *مفضلتك*\n"
            f"{SEP}\n\n"
            f"📊 العدد: *{len(favs)}* مشروع محفوظ\n\n"
            f"اضغط على أي مشروع لفتحه مباشرة:\n"
            f"{SEP2}\n"
        )
    else:
        header = (
            f"{SEP}\n"
            f"⭐ *Your Favorites*\n"
            f"{SEP}\n\n"
            f"📊 Count: *{len(favs)}* saved projects\n\n"
            f"Tap any project to open it:\n"
            f"{SEP2}\n"
        )

    buttons = []
    for i, fav in enumerate(favs[:20], 1):
        title = fav["title"]
        short = (title[:38] + "...") if len(title) > 38 else title
        saved = fav.get("saved_at", "")[:10]
        label = f"📌 {i}. {short}"
        if saved:
            label += f"  •  {saved}"
        buttons.append([InlineKeyboardButton(text=label, url=fav["link"])])

    buttons.append([InlineKeyboardButton(text=back_label, callback_data="back_home")])

    await call.message.edit_text(
        header,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="Markdown"
    )
    await call.answer()
