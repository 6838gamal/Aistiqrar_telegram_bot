import asyncio
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

TRIAL_HOURS   = 72
MONITOR_DELAY = 30      # seconds between each check
SEND_DELAY    = 0.5     # seconds between sending each project
MAX_MSG_LEN   = 4000    # Telegram limit is 4096

# in-memory per-user state
_user_monitors: dict[int, bool]      = {}
_user_seen:     dict[int, set[str]]  = {}


def _is_trial_expired(feed_started_at: str) -> bool:
    if not feed_started_at:
        return False
    started = datetime.fromisoformat(feed_started_at)
    return datetime.now() - started > timedelta(hours=TRIAL_HOURS)


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


def _format_project(p: dict, lang: str) -> str:
    title    = p.get("title", "—")
    brief    = p.get("brief", "—")
    time_rel = p.get("time", "—").strip()
    timestamp = p.get("timestamp", "")

    if lang == "ar":
        text = (
            f"🚀 *مشروع جديد*\n\n"
            f"📌 *{title}*\n"
            f"⏰ النشر: {time_rel}\n"
            f"🕐 {timestamp}\n\n"
            f"📝 *الوصف:*\n{brief}"
        )
    else:
        text = (
            f"🚀 *New Project*\n\n"
            f"📌 *{title}*\n"
            f"⏰ Posted: {time_rel}\n"
            f"🕐 {timestamp}\n\n"
            f"📝 *Description:*\n{brief}"
        )

    # respect Telegram's message length limit
    if len(text) > MAX_MSG_LEN:
        overflow = len(text) - MAX_MSG_LEN + 3
        brief = brief[:-overflow] + "..."
        if lang == "ar":
            text = (
                f"🚀 *مشروع جديد*\n\n"
                f"📌 *{title}*\n"
                f"⏰ النشر: {time_rel}\n"
                f"🕐 {timestamp}\n\n"
                f"📝 *الوصف:*\n{brief}"
            )
        else:
            text = (
                f"🚀 *New Project*\n\n"
                f"📌 *{title}*\n"
                f"⏰ Posted: {time_rel}\n"
                f"🕐 {timestamp}\n\n"
                f"📝 *Description:*\n{brief}"
            )
    return text


async def _send_projects(bot: Bot, user_id: int, lang: str, projects: list):
    for p in projects:
        text = _format_project(p, lang)
        kb   = _project_keyboard(p, lang)
        await bot.send_message(user_id, text, reply_markup=kb, parse_mode="Markdown")
        await asyncio.sleep(SEND_DELAY)


async def _monitor_loop(bot: Bot, user_id: int, lang: str, feed_started: str):
    # ── first run: send all current projects ──────────────────────────
    all_projects = fetch_projects()
    if all_projects:
        await _send_projects(bot, user_id, lang, all_projects)
        _user_seen[user_id] = {p["id"] for p in all_projects if p.get("id")}
    else:
        _user_seen.setdefault(user_id, set())

    # ── continuous monitoring loop ────────────────────────────────────
    while _user_monitors.get(user_id):
        await asyncio.sleep(MONITOR_DELAY)

        if not _user_monitors.get(user_id):
            break

        # trial check
        if _is_trial_expired(feed_started):
            await bot.send_message(user_id, translator.t("subscription_required", lang))
            _user_monitors[user_id] = False
            return

        # send "fetching" status
        if lang == "ar":
            status_msg = await bot.send_message(user_id, "🔄 جاري السحب...")
        else:
            status_msg = await bot.send_message(user_id, "🔄 Fetching new projects...")

        try:
            fresh_projects = fetch_projects()
            seen           = _user_seen.get(user_id, set())
            new_projects   = [p for p in fresh_projects if p.get("id") and p["id"] not in seen]

            if new_projects:
                # delete status then send new projects
                await status_msg.delete()
                for p in new_projects:
                    seen.add(p["id"])
                    text = _format_project(p, lang)
                    kb   = _project_keyboard(p, lang)
                    await bot.send_message(user_id, text, reply_markup=kb, parse_mode="Markdown")
                    await asyncio.sleep(SEND_DELAY)
                _user_seen[user_id] = seen
            else:
                # no new projects — delete status silently and keep watching
                await status_msg.delete()

        except Exception:
            try:
                await status_msg.delete()
            except Exception:
                pass


# ── Aiogram handlers ──────────────────────────────────────────────────

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
    idx  = int(call.data.split(":")[1])

    selected = get_selected_categories(call.from_user.id)
    if idx in selected:
        selected.remove(idx)
    else:
        selected.append(idx)

    update_selected_categories(call.from_user.id, selected)
    await call.message.edit_reply_markup(reply_markup=categories_keyboard(lang, selected))
    await call.answer()


@router.callback_query(F.data == "cat_save")
async def save_categories(call: CallbackQuery):
    user     = get_user(call.from_user.id)
    lang     = user.get("lang", "ar")
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
        await call.message.edit_text(translator.t("subscription_required", lang), reply_markup=None)
        await call.message.answer(translator.t("home_text", lang), reply_markup=home_menu(lang))
        return

    await call.answer(translator.t("cat_saved", lang))
    await call.message.edit_text(translator.t("feed_starting", lang), reply_markup=None)
    await call.message.answer(translator.t("home_text", lang), reply_markup=home_menu(lang))

    # stop any existing monitor for this user
    _user_monitors[call.from_user.id] = False
    await asyncio.sleep(0.1)

    # start new monitor
    _user_monitors[call.from_user.id] = True
    asyncio.create_task(
        _monitor_loop(call.bot, call.from_user.id, lang, feed_started)
    )
