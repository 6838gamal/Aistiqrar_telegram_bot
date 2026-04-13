import hashlib
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from app.database.db import get_user, add_favorite
from app.services.scraper import fetch_projects
from app.utils.translator import translator

router = Router()


def _project_keyboard(link: str, title: str, lang: str) -> InlineKeyboardMarkup:
    fav_id = hashlib.md5(link.encode()).hexdigest()[:16]
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
            InlineKeyboardButton(
                text=btn_fav,
                callback_data=f"fav:{fav_id}:{link[:80]}"
            ),
        ],
    ])


def _format_project(p: dict, lang: str) -> str:
    title     = p.get("title", "—")
    brief     = p.get("brief", "—")
    time_rel  = p.get("time", "—").strip()

    if lang == "ar":
        return (
            f"🚀 *مشروع جديد*\n\n"
            f"📌 *{title}*\n"
            f"⏰ النشر: {time_rel}\n\n"
            f"📝 *الوصف:*\n{brief}"
        )
    else:
        return (
            f"🚀 *New Project*\n\n"
            f"📌 *{title}*\n"
            f"⏰ Posted: {time_rel}\n\n"
            f"📝 *Description:*\n{brief}"
        )


@router.callback_query(F.data == "page_job")
async def page_job(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")

    projects = fetch_projects()

    if not projects:
        no_data = "⚠️ لا توجد مشاريع متاحة حالياً. حاول لاحقاً." if lang == "ar" \
                  else "⚠️ No projects available right now. Try again later."
        await call.message.answer(no_data)
        await call.answer()
        return

    await call.message.delete()

    for p in projects:
        text = _format_project(p, lang)
        kb   = _project_keyboard(p["link"], p["title"], lang)
        await call.message.answer(text, reply_markup=kb, parse_mode="Markdown")

    await call.answer()


@router.callback_query(F.data.startswith("fav:"))
async def save_favorite(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")

    parts = call.data.split(":", 2)
    link  = parts[2] if len(parts) == 3 else ""

    projects = fetch_projects()
    project  = next((p for p in projects if p["link"].startswith(link)), None)
    title    = project["title"] if project else "—"

    added = add_favorite(call.from_user.id, title, project["link"] if project else link)

    if added:
        msg = f"⭐ تمت الإضافة إلى المفضلة:\n📌 {title}" if lang == "ar" \
              else f"⭐ Added to favorites:\n📌 {title}"
    else:
        msg = "✅ هذا المشروع موجود بالفعل في مفضلتك." if lang == "ar" \
              else "✅ This project is already in your favorites."

    await call.answer(msg, show_alert=True)
