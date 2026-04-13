from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.database.db import get_user
from app.keyboards.menu import back_button
from app.services.mostaql_scraper import fetch_projects
from app.utils.translator import translator

router = Router()


def projects_keyboard(projects: list, lang: str) -> InlineKeyboardMarkup:
    buttons = []
    for i, p in enumerate(projects[:5]):
        title = p["title"][:35] + ("..." if len(p["title"]) > 35 else "")
        buttons.append([InlineKeyboardButton(text=f"🔗 {title}", url=p["link"])])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "page_job")
async def page_job(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")

    projects = fetch_projects()

    if not projects:
        await call.message.edit_text(
            "⚠️ لا توجد مشاريع متاحة حالياً. حاول لاحقاً." if lang == "ar"
            else "⚠️ No projects available right now. Try again later.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[])
        )
        await call.answer()
        return

    header = "🚀 *المشاريع الحية من مستقل*\n\n" if lang == "ar" else "🚀 *Live Projects from Mostaql*\n\n"

    lines = []
    for i, p in enumerate(projects[:5], 1):
        time_str = p.get("time", "").strip()
        brief_short = p["brief"][:120] + ("..." if len(p["brief"]) > 120 else "")
        lines.append(
            f"*{i}. {p['title']}*\n"
            f"📝 {brief_short}\n"
            f"🕒 {time_str}\n"
        )

    text = header + "\n".join(lines)

    await call.message.edit_text(
        text,
        reply_markup=projects_keyboard(projects, lang),
        parse_mode="Markdown"
    )
    await call.answer()
