import asyncio
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from datetime import datetime, timedelta
from app.database.db import (
    get_user, get_selected_categories, update_selected_categories,
    get_feed_started_at, set_feed_started_at
)
from app.keyboards.menu import home_menu
from app.keyboards.categories import categories_keyboard
from app.services.job_service import generate_jobs_by_categories
from app.utils.translator import translator
from app.data.categories import CATEGORIES

router = Router()

TRIAL_HOURS = 72
SEND_DELAY = 0.07


def _is_trial_expired(feed_started_at: str) -> bool:
    if not feed_started_at:
        return False
    started = datetime.fromisoformat(feed_started_at)
    return datetime.now() - started > timedelta(hours=TRIAL_HOURS)


def _format_job(job: dict, lang: str, seq: int, total: int) -> str:
    cats = CATEGORIES.get(lang, CATEGORIES["ar"])
    cat_idx = job.get("category")
    cat_label = ""
    if cat_idx is not None and cat_idx < len(cats):
        emoji, name = cats[cat_idx]
        cat_label = f"{emoji} {name}"

    title = job["title_ar"] if lang == "ar" else job["title_en"]
    platform = job["platform_ar"] if lang == "ar" else job["platform_en"]
    counter = translator.t("job_counter", lang).format(current=seq, total=total)

    return (
        f"{counter}\n"
        f"{'─' * 22}\n"
        f"🏷️ {cat_label}\n\n"
        f"📌 {title}\n"
        f"💰 {job['price']}\n"
        f"🌐 {platform}\n\n"
        f"✅ {translator.t('verified', lang)}"
    )


async def _auto_send_jobs(bot: Bot, user_id: int, lang: str, jobs: list, feed_started: str):
    total = len(jobs)
    for i, job in enumerate(jobs):
        if i % 50 == 0 and _is_trial_expired(feed_started):
            await bot.send_message(
                user_id,
                translator.t("subscription_required", lang)
            )
            return

        text = _format_job(job, lang, i + 1, total)
        await bot.send_message(user_id, text)
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

    jobs = generate_jobs_by_categories(selected, per_category=1000)
    asyncio.create_task(
        _auto_send_jobs(call.bot, call.from_user.id, lang, jobs, feed_started)
    )
