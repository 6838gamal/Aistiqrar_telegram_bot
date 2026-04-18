from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from app.database.db import get_user, add_favorite, is_profile_complete, get_profile
from app.services.scraper import fetch_projects
from app.utils.translator import translator
from app.utils.formatting import SEP, SEP2, format_project
from app.utils.matching import calc_match

router = Router()


def _project_keyboard(project: dict, lang: str) -> InlineKeyboardMarkup:
    link = project["link"]
    pid  = project.get("id") or project.get("project_id") or link.split("/")[-1][:20]
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
        [InlineKeyboardButton(text=btn_fav, callback_data=f"fav:{pid}")],
    ])


def _profile_incomplete_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == "ar":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 إكمال الملف الشخصي", callback_data="profile_edit")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Complete My Profile", callback_data="profile_edit")],
    ])


@router.callback_query(F.data == "page_job")
async def page_job(call: CallbackQuery, state: FSMContext):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")

    # ── Profile check ─────────────────────────────────────────────────
    if not is_profile_complete(call.from_user.id):
        if lang == "ar":
            text = (
                f"{SEP}\n"
                f"⚠️ *الملف الشخصي غير مكتمل*\n"
                f"{SEP}\n\n"
                f"لعرض الفرص مع نسبة توافق دقيقة،\n"
                f"يجب إكمال ملفك الشخصي أولاً.\n\n"
                f"سيستغرق ذلك أقل من دقيقتين ⏱️"
            )
        else:
            text = (
                f"{SEP}\n"
                f"⚠️ *Profile Incomplete*\n"
                f"{SEP}\n\n"
                f"To view opportunities with accurate match scores,\n"
                f"please complete your profile first.\n\n"
                f"It takes less than 2 minutes ⏱️"
            )
        await call.message.answer(
            text,
            reply_markup=_profile_incomplete_keyboard(lang),
            parse_mode="Markdown"
        )
        await call.answer()
        return

    # ── Fetch projects ────────────────────────────────────────────────
    projects = fetch_projects()
    if not projects:
        no_data = (
            f"{SEP}\n⚠️ *لا توجد مشاريع متاحة*\n{SEP}\n\nيرجى المحاولة لاحقاً."
        ) if lang == "ar" else (
            f"{SEP}\n⚠️ *No Projects Available*\n{SEP}\n\nPlease try again later."
        )
        await call.message.answer(no_data, parse_mode="Markdown")
        await call.answer()
        return

    await call.message.delete()

    profile = get_profile(call.from_user.id)
    for p in projects:
        match = calc_match(profile, p)
        text  = format_project(p, lang, match=match)
        kb    = _project_keyboard(p, lang)
        await call.message.answer(text, reply_markup=kb, parse_mode="Markdown")

    await call.answer()


@router.callback_query(F.data.startswith("fav:"))
async def save_favorite(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")

    pid      = call.data.split(":", 1)[1]
    projects = fetch_projects()
    project  = next((p for p in projects if
                     (p.get("id") == pid or p.get("project_id") == pid)), None)

    if not project:
        msg = "⚠️ لم يُعثر على المشروع." if lang == "ar" else "⚠️ Project not found."
        await call.answer(msg, show_alert=True)
        return

    added = add_favorite(call.from_user.id, project["title"], project["link"])
    if added:
        msg = f"⭐ تمت الإضافة!\n📌 {project['title'][:50]}" if lang == "ar" \
              else f"⭐ Added!\n📌 {project['title'][:50]}"
    else:
        msg = "✅ المشروع موجود بالفعل في مفضلتك." if lang == "ar" \
              else "✅ Already in your favorites."
    await call.answer(msg, show_alert=True)
