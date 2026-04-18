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
from app.services.scraper import fetch_projects
from app.utils.translator import translator
from app.utils.formatting import SEP, SEP2, format_project
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


def _subscription_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == "ar":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 اشترك الآن",     callback_data="page_subscribe")],
            [InlineKeyboardButton(text="📞 تواصل معنا",     callback_data="page_contact")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 Subscribe Now",  callback_data="page_subscribe")],
            [InlineKeyboardButton(text="📞 Contact Us",     callback_data="page_contact")],
        ])


def _subscription_expired_text(lang: str) -> str:
    if lang == "ar":
        return (
            f"{SEP}\n"
            f"⏰ *انتهت فترة التجربة المجانية*\n"
            f"{SEP}\n\n"
            f"📅 مدة التجربة: 72 ساعة مجاناً\n\n"
            f"{SEP2}\n\n"
            f"للاستمرار في الوصول إلى المشاريع والمراقبة المستمرة، يرجى تفعيل الاشتراك.\n\n"
            f"💳 *طرق الدفع المتاحة:*\n"
            f"• 🟡 Binance Pay\n"
            f"• 💵 صرافة كريمي\n"
            f"• 📱 تطبيقات الصرافة الأخرى\n\n"
            f"{SEP2}\n\n"
            f"اضغط *اشترك الآن* للاطلاع على التفاصيل كاملة 👇\n"
            f"{SEP}"
        )
    else:
        return (
            f"{SEP}\n"
            f"⏰ *Free Trial Ended*\n"
            f"{SEP}\n\n"
            f"📅 Trial duration: 72 hours free\n\n"
            f"{SEP2}\n\n"
            f"To continue accessing projects and monitoring, please activate your subscription.\n\n"
            f"💳 *Available Payment Methods:*\n"
            f"• 🟡 Binance Pay\n"
            f"• 💵 Karimi Exchange\n"
            f"• 📱 Other Exchange Apps\n\n"
            f"{SEP2}\n\n"
            f"Tap *Subscribe Now* for full details 👇\n"
            f"{SEP}"
        )


async def _send_projects(bot: Bot, user_id: int, lang: str, projects: list):
    for p in projects:
        text = format_project(p, lang)
        kb   = _project_keyboard(p, lang)
        await bot.send_message(user_id, text, reply_markup=kb, parse_mode="Markdown")
        await asyncio.sleep(SEND_DELAY)


async def _monitor_loop(bot: Bot, user_id: int, lang: str, feed_started: str):
    all_projects = fetch_projects()
    if all_projects:
        await _send_projects(bot, user_id, lang, all_projects)
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

        status_label = "🔄 جاري السحب..." if lang == "ar" else "🔄 Fetching new projects..."
        status_msg = await bot.send_message(user_id, status_label)

        try:
            fresh_projects = fetch_projects()
            seen           = _user_seen.get(user_id, set())
            new_projects   = [p for p in fresh_projects if p.get("id") and p["id"] not in seen]

            if new_projects:
                await status_msg.delete()
                for p in new_projects:
                    seen.add(p["id"])
                    text = format_project(p, lang)
                    kb   = _project_keyboard(p, lang)
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
        await call.message.edit_text(
            _subscription_expired_text(lang),
            reply_markup=_subscription_keyboard(lang),
            parse_mode="Markdown"
        )
        return

    await call.answer(translator.t("cat_saved", lang))

    start_label = (
        f"{SEP}\n🚀 *جاري تحميل الفرص وبدء المراقبة...*\n{SEP}\n\n"
        f"⏳ سيصلك كل مشروع جديد فور نشره تلقائياً."
    ) if lang == "ar" else (
        f"{SEP}\n🚀 *Loading projects and starting monitoring...*\n{SEP}\n\n"
        f"⏳ Every new project will be sent to you automatically."
    )

    await call.message.edit_text(start_label, reply_markup=None, parse_mode="Markdown")
    await call.message.answer(translator.t("home_text", lang), reply_markup=home_menu(lang))

    _user_monitors[call.from_user.id] = False
    await asyncio.sleep(0.1)

    _user_monitors[call.from_user.id] = True
    asyncio.create_task(
        _monitor_loop(call.bot, call.from_user.id, lang, feed_started)
    )
