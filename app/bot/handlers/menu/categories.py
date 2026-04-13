import asyncio
import hashlib
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from app.database.db import (
    get_user, get_selected_categories, update_selected_categories,
    get_feed_started_at, set_feed_started_at
)
from app.keyboards.menu import home_menu
from app.keyboards.categories import categories_keyboard
from app.services.scraper import fetch_projects, filter_by_categories
from app.utils.translator import translator
from app.data.categories import CATEGORIES

router = Router()

TRIAL_HOURS = 72
SEND_DELAY  = 0.5


def _is_trial_expired(feed_started_at: str) -> bool:
    if not feed_started_at:
        return False
    started = datetime.fromisoformat(feed_started_at)
    return datetime.now() - started > timedelta(hours=TRIAL_HOURS)


def _project_keyboard(link: str, lang: str) -> InlineKeyboardMarkup:
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


def _format_project(p: dict, lang: str, seq: int, total: int) -> str:
    title    = p.get("title", "—")
    brief    = p.get("brief", "—")
    time_rel = p.get("time", "—").strip()
    counter  = translator.t("job_counter", lang).format(current=seq, total=total)

    if lang == "ar":
        return (
            f"{counter}\n"
            f"{'─' * 22}\n"
            f"🚀 *مشروع جديد*\n\n"
            f"📌 *{title}*\n"
            f"⏰ النشر: {time_rel}\n\n"
            f"📝 *الوصف:*\n{brief}"
        )
    else:
        return (
            f"{counter}\n"
            f"{'─' * 22}\n"
            f"🚀 *New Project*\n\n"
            f"📌 *{title}*\n"
            f"⏰ Posted: {time_rel}\n\n"
            f"📝 *Description:*\n{brief}"
        )


async def _auto_send_projects(
    bot: Bot, user_id: int, lang: str,
    projects: list, feed_started: str
):
    total = len(projects)
    for i, project in enumerate(projects):
        if _is_trial_expired(feed_started):
            await bot.send_message(
                user_id,
                translator.t("subscription_required", lang)
            )
            return

        text = _format_project(project, lang, i + 1, total)
        kb   = _project_keyboard(project["link"], lang)
        await bot.send_message(user_id, text, reply_markup=kb, parse_mode="Markdown")
        await asyncio.sleep(SEND_DELAY)

    await bot.send_message(
        user_id,
        translator.t("feed_completed", lang),
        reply_markup=home_menu(lang)
    )


@router.callback_query(F.data == "page_categories")
async def page_categories(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    selected = get_selected_categories(call.from_user.id)
    await call.message.edit_text(
        translator.t("categories_text", lang),
        reply_markup=categories_keyboard(lang, selected)
    )
    await call.answer()


@router.callback_query(F.data.startswith("cat_toggle:"))
async def toggle_category(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    idx = int(call.data.split(":")[1])

    selected = get_selected_categories(call.from_user.id)
    if idx in selected:
        selected.remove(idx)
    else:
        selected.append(idx)

    update_selected_categories(call.from_user.id, selected)

    await call.message.edit_reply_markup(
        reply_markup=categories_keyboard(lang, selected)
    )
    await call.answer()


@router.callback_query(F.data == "cat_save")
async def save_categories(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    selected = get_selected_categories(call.from_user.id)

    if not selected:
        await call.answer(translator.t("cat_none_selected", lang), show_alert=True)
        return

    feed_started = get_feed_started_at(call.from_user.id)
    if not feed_started:
        set_feed_started_at(call.from_user.id)
        feed_started = datetime.now().isoformat()

    if _is_trial_expired(feed_started):
        await call.answer()
        await call.message.edit_text(
            translator.t("subscription_required", lang),
            reply_markup=None
        )
        await call.message.answer(
            translator.t("home_text", lang),
            reply_markup=home_menu(lang)
        )
        return

    await call.answer(translator.t("cat_saved", lang))
    await call.message.edit_text(
        translator.t("feed_starting", lang),
        reply_markup=None
    )
    await call.message.answer(
        translator.t("home_text", lang),
        reply_markup=home_menu(lang)
    )

    all_projects     = fetch_projects()
    matched_projects = filter_by_categories(all_projects, selected)

    if not matched_projects:
        no_jobs_msg = translator.t("cat_no_jobs", lang)
        await call.message.answer(no_jobs_msg)
        return

    asyncio.create_task(
        _auto_send_projects(call.bot, call.from_user.id, lang, matched_projects, feed_started)
    )
