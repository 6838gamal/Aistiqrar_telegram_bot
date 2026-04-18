from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from app.database.db import get_user
from app.utils.formatting import SEP, SEP2
from app.utils.translator import translator

router = Router()


def _profile_display(user: dict, lang: str) -> str:
    spec      = user.get("specialization", "") or ("—" if lang == "ar" else "—")
    skills    = user.get("skills", "")          or ("—" if lang == "ar" else "—")
    exp       = user.get("experience_years", "") or ("—" if lang == "ar" else "—")
    portfolio = user.get("portfolio_link", "")   or ("—" if lang == "ar" else "—")
    rate      = user.get("hourly_rate", "")      or ("—" if lang == "ar" else "—")
    referrals = user.get("referral_count", 0)
    join_type = user.get("join_type", "direct")
    completed = bool(user.get("profile_completed"))

    status = "✅ مكتمل" if completed else "⚠️ غير مكتمل"

    if lang == "ar":
        join_label = "عبر إحالة 🎁" if join_type == "referral" else "مباشر ✅"
        return (
            f"{SEP}\n"
            f"👤 *ملفك الشخصي*\n"
            f"{SEP}\n\n"
            f"🆔 المعرف: `{user.get('user_id', '')}`\n"
            f"👋 الاسم: {user.get('name', '')}\n"
            f"📥 الانضمام: {join_label}\n"
            f"👥 الإحالات: {referrals}\n"
            f"📋 حالة الملف: {status}\n"
            f"\n{SEP2}\n\n"
            f"🎯 *التخصص:* {spec}\n"
            f"🛠️ *المهارات:* {skills}\n"
            f"📅 *الخبرة:* {exp}\n"
            f"🔗 *المحفظة:* {portfolio}\n"
            f"💰 *السعر:* {rate}\n"
            f"{SEP}"
        )
    else:
        join_label = "Via Referral 🎁" if join_type == "referral" else "Direct ✅"
        return (
            f"{SEP}\n"
            f"👤 *My Profile*\n"
            f"{SEP}\n\n"
            f"🆔 ID: `{user.get('user_id', '')}`\n"
            f"👋 Name: {user.get('name', '')}\n"
            f"📥 Joined: {join_label}\n"
            f"👥 Referrals: {referrals}\n"
            f"📋 Profile Status: {status}\n"
            f"\n{SEP2}\n\n"
            f"🎯 *Specialization:* {spec}\n"
            f"🛠️ *Skills:* {skills}\n"
            f"📅 *Experience:* {exp}\n"
            f"🔗 *Portfolio:* {portfolio}\n"
            f"💰 *Rate:* {rate}\n"
            f"{SEP}"
        )


def _profile_keyboard(lang: str, completed: bool) -> InlineKeyboardMarkup:
    back_label = translator.t("menu_back", lang)
    buttons = []
    if completed:
        edit_label = "✏️ تعديل الملف الشخصي" if lang == "ar" else "✏️ Edit Profile"
        buttons.append([InlineKeyboardButton(text=edit_label, callback_data="profile_edit")])
    else:
        setup_label = "🚀 إكمال الملف الشخصي" if lang == "ar" else "🚀 Complete Profile"
        buttons.append([InlineKeyboardButton(text=setup_label, callback_data="profile_edit")])
    buttons.append([InlineKeyboardButton(text=back_label, callback_data="back_home")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "page_profile")
async def page_profile(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    completed = bool(user.get("profile_completed"))
    text = _profile_display(user, lang)
    await call.message.edit_text(
        text,
        reply_markup=_profile_keyboard(lang, completed),
        parse_mode="Markdown"
    )
    await call.answer()


@router.callback_query(F.data == "profile_edit")
async def profile_edit(call: CallbackQuery, state: FSMContext):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    from app.bot.handlers.profile_setup import start_profile_setup
    await call.answer()
    await start_profile_setup(call, state, lang)
