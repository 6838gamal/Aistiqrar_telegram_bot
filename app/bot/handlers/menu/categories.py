import asyncio
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from app.database.db import (
    get_user, get_profile, get_selected_categories, update_selected_categories,
    get_feed_started_at, set_feed_started_at, is_profile_complete
)
from app.keyboards.menu import home_menu
from app.keyboards.categories import categories_keyboard
from app.services.scraper import fetch_projects
from app.utils.translator import translator
from app.utils.formatting import SEP, SEP2, format_project
from app.utils.matching import calc_match
from app.data.categories import CATEGORIES

router = Router()

TRIAL_HOURS   = 72
MONITOR_DELAY = 30
SEND_DELAY    = 0.5

_user_monitors: dict[int, bool]     = {}
_user_seen:     dict[int, set[str]] = {}


def _is_trial_expired(feed_started_at: str) -> bool:
    if not feed_started_at:
        return False
    started = datetime.fromisoformat(feed_started_at)
    return datetime.now() - started > timedelta(hours=TRIAL_HOURS)


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
    label = "🚀 إكمال الملف الشخصي" if lang == "ar" else "🚀 Complete My Profile"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, callback_data="profile_edit")]
    ])


def _subscription_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💎 اشترك الآن" if lang == "ar" else "💎 Subscribe Now",
            callback_data="page_subscribe"
        )],
        [InlineKeyboardButton(
            text="📞 تواصل معنا" if lang == "ar" else "📞 Contact Us",
            callback_data="page_contact"
        )],
    ])


def _subscription_expired_text(lang: str) -> str:
    if lang == "ar":
        return (
            f"{SEP}\n⏰ *انتهت فترة التجربة المجانية*\n{SEP}\n\n"
            f"📅 مدة التجربة: 72 ساعة\n\n{SEP2}\n\n"
            f"للاستمرار يرجى تفعيل الاشتراك.\n\n"
            f"💳 Binance Pay · صرافة كريمي · تطبيقات الصرافة\n\n"
            f"اضغط *اشترك الآن* للتفاصيل 👇\n{SEP}"
        )
    return (
        f"{SEP}\n⏰ *Free Trial Ended*\n{SEP}\n\n"
        f"📅 Trial: 72 hours\n\n{SEP2}\n\n"
        f"Please activate your subscription to continue.\n\n"
        f"💳 Binance Pay · Karimi Exchange · Other Apps\n\n"
        f"Tap *Subscribe Now* for details 👇\n{SEP}"
    )


async def _send_projects(bot: Bot, user_id: int, lang: str,
                         profile: dict, projects: list):
    for p in projects:
        match = calc_match(profile, p)
        text  = format_project(p, lang, match=match)
        kb    = _project_keyboard(p, lang)
        await bot.send_message(user_id, text, reply_markup=kb, parse_mode="Markdown")
        await asyncio.sleep(SEND_DELAY)


async def _monitor_loop(bot: Bot, user_id: int, lang: str,
                        profile: dict, feed_started: str):
    all_projects = fetch_projects()
    if all_projects:
        await _send_projects(bot, user_id, lang, profile, all_projects)
        _user_seen[user_id] = {p["id"] for p in all_projects if p.get("id")}
    else:
        _user_seen.setdefault(user_id, set())

    while _user_monitors.get(user_id):
        await asyncio.sleep(MONITOR_DELAY)
        if not _user_monitors.get(user_id):
            break

        if _is_trial_expired(feed_started):
            await bot.send_message(
                user_id,
                _subscription_expired_text(lang),
                reply_markup=_subscription_keyboard(lang),
                parse_mode="Markdown"
            )
            _user_monitors[user_id] = False
            return

        status_label = "🔄 جاري السحب..." if lang == "ar" else "🔄 Fetching..."
        status_msg = await bot.send_message(user_id, status_label)

        try:
            fresh_projects = fetch_projects()
            seen           = _user_seen.get(user_id, set())
            new_projects   = [p for p in fresh_projects
                              if p.get("id") and p["id"] not in seen]

            if new_projects:
                await status_msg.delete()
                for p in new_projects:
                    seen.add(p["id"])
                    match = calc_match(profile, p)
                    text  = format_project(p, lang, match=match)
                    kb    = _project_keyboard(p, lang)
                    await bot.send_message(user_id, text, reply_markup=kb, parse_mode="Markdown")
                    await asyncio.sleep(SEND_DELAY)
                _user_seen[user_id] = seen
            else:
                await status_msg.delete()
        except Exception:
            try:
                await status_msg.delete()
            except Exception:
                pass


# ── Handlers ──────────────────────────────────────────────────────────

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
async def save_categories(call: CallbackQuery, state: FSMContext):
    user     = get_user(call.from_user.id)
    lang     = user.get("lang", "ar")
    selected = get_selected_categories(call.from_user.id)

    if not selected:
        await call.answer(translator.t("cat_none_selected", lang), show_alert=True)
        return

    # ── Profile check ─────────────────────────────────────────────────
    if not is_profile_complete(call.from_user.id):
        await call.answer()
        if lang == "ar":
            text = (
                f"{SEP}\n"
                f"⚠️ *أكمل ملفك الشخصي أولاً*\n"
                f"{SEP}\n\n"
                f"الملف الشخصي يساعدنا في:\n"
                f"✅ إرسال الفرص المناسبة لمهاراتك\n"
                f"📊 حساب نسبة توافقك مع كل مشروع\n"
                f"💡 تقديم نصائح لرفع فرص القبول\n\n"
                f"اضغط أدناه لإكمال ملفك (أقل من دقيقتين) ⏱️"
            )
        else:
            text = (
                f"{SEP}\n"
                f"⚠️ *Complete Your Profile First*\n"
                f"{SEP}\n\n"
                f"Your profile helps us:\n"
                f"✅ Send opportunities matching your skills\n"
                f"📊 Calculate your match score for each project\n"
                f"💡 Give tips to improve acceptance chances\n\n"
                f"Tap below to complete your profile (< 2 min) ⏱️"
            )
        await call.message.edit_text(
            text,
            reply_markup=_profile_incomplete_keyboard(lang),
            parse_mode="Markdown"
        )
        return

    # ── Trial check ───────────────────────────────────────────────────
    feed_started = get_feed_started_at(call.from_user.id)
    if not feed_started:
        set_feed_started_at(call.from_user.id)
        feed_started = datetime.now().isoformat()

    if _is_trial_expired(feed_started):
        await call.answer()
        await call.message.edit_text(
            _subscription_expired_text(lang),
            reply_markup=_subscription_keyboard(lang),
            parse_mode="Markdown"
        )
        return

    await call.answer(translator.t("cat_saved", lang))

    profile = get_profile(call.from_user.id)

    start_label = (
        f"{SEP}\n🚀 *جاري تحميل الفرص وبدء المراقبة...*\n{SEP}\n\n"
        f"📊 ستظهر نسبة التوافق مع كل مشروع تلقائياً\n"
        f"⏳ سيصلك كل مشروع جديد فور نشره"
    ) if lang == "ar" else (
        f"{SEP}\n🚀 *Loading projects and starting monitoring...*\n{SEP}\n\n"
        f"📊 Match score will appear with every project\n"
        f"⏳ Every new project will be sent automatically"
    )

    await call.message.edit_text(start_label, reply_markup=None, parse_mode="Markdown")
    await call.message.answer(translator.t("home_text", lang), reply_markup=home_menu(lang))

    _user_monitors[call.from_user.id] = False
    await asyncio.sleep(0.1)
    _user_monitors[call.from_user.id] = True
    asyncio.create_task(
        _monitor_loop(call.bot, call.from_user.id, lang, profile, feed_started)
    )
