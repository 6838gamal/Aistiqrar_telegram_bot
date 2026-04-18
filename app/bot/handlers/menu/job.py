from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.database.db import get_user, add_favorite
from app.services.scraper import fetch_projects
from app.utils.translator import translator
from app.utils.formatting import SEP, SEP2, format_project

router = Router()


def _project_keyboard(project: dict, lang: str) -> InlineKeyboardMarkup:
    link = project["link"]
    pid  = project.get("id") or link.split("/")[-1][:20]
    if lang == "ar":
        btn_open    = "🔗 الذهاب إلى المشروع"
        btn_propose = "✍️ كتابة عرض"
        btn_fav     = "⭐ إضافة إلى المفضلة"
    else:
        btn_open    = "🔗 Open Project"
        btn_propose = "✍️ Write Proposal"
        btn_fav     = "⭐ Add to Favorites"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=btn_open,    url=link),
            InlineKeyboardButton(text=btn_propose, url=link),
        ],
        [
            InlineKeyboardButton(text=btn_fav, callback_data=f"fav:{pid}"),
        ],
    ])


@router.callback_query(F.data == "page_job")
async def page_job(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")

    projects = fetch_projects()

    if not projects:
        no_data = (
            f"{SEP}\n"
            f"⚠️ *لا توجد مشاريع متاحة*\n"
            f"{SEP}\n\n"
            f"لا تتوفر مشاريع حالياً، يرجى المحاولة لاحقاً."
        ) if lang == "ar" else (
            f"{SEP}\n"
            f"⚠️ *No Projects Available*\n"
            f"{SEP}\n\n"
            f"No projects available right now. Please try again later."
        )
        await call.message.answer(no_data, parse_mode="Markdown")
        await call.answer()
        return

    await call.message.delete()

    for p in projects:
        text = format_project(p, lang)
        kb   = _project_keyboard(p, lang)
        await call.message.answer(text, reply_markup=kb, parse_mode="Markdown")

    await call.answer()


@router.callback_query(F.data.startswith("fav:"))
async def save_favorite(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")

    pid      = call.data.split(":", 1)[1]
    projects = fetch_projects()
    project  = next((p for p in projects if p.get("id") == pid), None)

    if not project:
        msg = "⚠️ لم يُعثر على المشروع." if lang == "ar" else "⚠️ Project not found."
        await call.answer(msg, show_alert=True)
        return

    added = add_favorite(call.from_user.id, project["title"], project["link"])

    if added:
        msg = f"⭐ تمت الإضافة!\n📌 {project['title'][:50]}" if lang == "ar" \
              else f"⭐ Added to favorites!\n📌 {project['title'][:50]}"
    else:
        msg = "✅ المشروع موجود بالفعل في مفضلتك." if lang == "ar" \
              else "✅ Already in your favorites."

    await call.answer(msg, show_alert=True)
