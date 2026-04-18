"""
Multi-step profile setup using aiogram FSM.
Called when user tries to start feed without a completed profile.
"""
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from app.bot.states.profile_setup import ProfileSetup
from app.database.db import get_user, save_profile
from app.keyboards.menu import home_menu
from app.utils.formatting import SEP, SEP2

router = Router()

SKIP_WORDS = {"تخطي", "skip", "-", "."}


def _is_skip(text: str) -> bool:
    return text.strip().lower() in SKIP_WORDS


def _skip_keyboard(lang: str) -> ReplyKeyboardMarkup:
    label = "⏭️ تخطي" if lang == "ar" else "⏭️ Skip"
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=label)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def step_text(step: int, total: int, lang: str) -> str:
    if lang == "ar":
        return f"الخطوة {step} من {total}"
    return f"Step {step} of {total}"


# ─────────────────────────────────────────────────────────────────────
# Entry point (called externally to start the flow)
# ─────────────────────────────────────────────────────────────────────

async def start_profile_setup(message_or_call, state: FSMContext, lang: str):
    """Start the profile setup flow from a Message or CallbackQuery."""
    if isinstance(message_or_call, CallbackQuery):
        send = message_or_call.message.answer
    else:
        send = message_or_call.answer

    text = (
        f"{SEP}\n"
        f"👤 *إعداد ملفك الشخصي*\n"
        f"{SEP}\n\n"
        f"لتحصل على فرص مخصصة لك مع نسبة توافق دقيقة،\n"
        f"نحتاج بعض المعلومات عن مهاراتك وخبرتك.\n\n"
        f"سيستغرق ذلك أقل من دقيقتين ⏱️\n"
        f"{SEP}"
    ) if lang == "ar" else (
        f"{SEP}\n"
        f"👤 *Profile Setup*\n"
        f"{SEP}\n\n"
        f"To get personalized opportunities with accurate match scores,\n"
        f"we need a few details about your skills and experience.\n\n"
        f"This takes less than 2 minutes ⏱️\n"
        f"{SEP}"
    )

    await send(text, parse_mode="Markdown")
    await ask_specialization(send, lang)
    await state.set_state(ProfileSetup.specialization)


async def ask_specialization(send_fn, lang: str):
    if lang == "ar":
        text = (
            f"🎯 *{step_text(1, 5, lang)}*\n\n"
            f"ما هو *تخصصك الرئيسي*؟\n\n"
            f"مثال: مطور ويب · مصمم جرافيك · كاتب محتوى\n"
            f"مبرمج تطبيقات · مسوّق رقمي · محلل بيانات..."
        )
    else:
        text = (
            f"🎯 *{step_text(1, 5, lang)}*\n\n"
            f"What is your *main specialization*?\n\n"
            f"e.g., Web Developer · Graphic Designer · Content Writer\n"
            f"Mobile Developer · Digital Marketer · Data Analyst..."
        )
    await send_fn(text, parse_mode="Markdown")


# ─────────────────────────────────────────────────────────────────────
# Step 1 — Specialization
# ─────────────────────────────────────────────────────────────────────

@router.message(ProfileSetup.specialization)
async def handle_specialization(message: Message, state: FSMContext):
    lang = get_user(message.from_user.id).get("lang", "ar")
    await state.update_data(specialization=message.text.strip())

    if lang == "ar":
        text = (
            f"🛠️ *{step_text(2, 5, lang)}*\n\n"
            f"ما هي *مهاراتك التقنية*؟\n\n"
            f"اكتبها مفصولة بفواصل\n"
            f"مثال: Python, React, Figma, SEO, WordPress, After Effects"
        )
    else:
        text = (
            f"🛠️ *{step_text(2, 5, lang)}*\n\n"
            f"What are your *technical skills*?\n\n"
            f"List them separated by commas\n"
            f"e.g., Python, React, Figma, SEO, WordPress, After Effects"
        )
    await message.answer(text, parse_mode="Markdown")
    await state.set_state(ProfileSetup.skills)


# ─────────────────────────────────────────────────────────────────────
# Step 2 — Skills
# ─────────────────────────────────────────────────────────────────────

@router.message(ProfileSetup.skills)
async def handle_skills(message: Message, state: FSMContext):
    lang = get_user(message.from_user.id).get("lang", "ar")
    await state.update_data(skills=message.text.strip())

    if lang == "ar":
        text = (
            f"📅 *{step_text(3, 5, lang)}*\n\n"
            f"كم *سنة من الخبرة* لديك في مجالك؟\n\n"
            f"مثال: أقل من سنة · سنة · سنتان · 3 سنوات · 5+ سنوات"
        )
    else:
        text = (
            f"📅 *{step_text(3, 5, lang)}*\n\n"
            f"How many *years of experience* do you have?\n\n"
            f"e.g., Less than a year · 1 year · 2 years · 3 years · 5+ years"
        )
    await message.answer(text, parse_mode="Markdown")
    await state.set_state(ProfileSetup.experience)


# ─────────────────────────────────────────────────────────────────────
# Step 3 — Experience
# ─────────────────────────────────────────────────────────────────────

@router.message(ProfileSetup.experience)
async def handle_experience(message: Message, state: FSMContext):
    lang = get_user(message.from_user.id).get("lang", "ar")
    await state.update_data(experience_years=message.text.strip())

    if lang == "ar":
        text = (
            f"🔗 *{step_text(4, 5, lang)}*\n\n"
            f"رابط *محفظة أعمالك* (اختياري)\n\n"
            f"GitHub · Behance · LinkedIn · Dribbble · أي رابط آخر\n\n"
            f"💡 وجود محفظة يرفع نسبة توافقك +15%\n"
            f"اكتب *تخطي* إذا لم يكن لديك رابط الآن"
        )
    else:
        text = (
            f"🔗 *{step_text(4, 5, lang)}*\n\n"
            f"Your *portfolio link* (optional)\n\n"
            f"GitHub · Behance · LinkedIn · Dribbble · Any link\n\n"
            f"💡 Having a portfolio adds +15% to your match score\n"
            f"Type *skip* if you don't have one yet"
        )
    await message.answer(text, parse_mode="Markdown", reply_markup=_skip_keyboard(lang))
    await state.set_state(ProfileSetup.portfolio)


# ─────────────────────────────────────────────────────────────────────
# Step 4 — Portfolio
# ─────────────────────────────────────────────────────────────────────

@router.message(ProfileSetup.portfolio)
async def handle_portfolio(message: Message, state: FSMContext):
    lang = get_user(message.from_user.id).get("lang", "ar")
    val  = "" if _is_skip(message.text) else message.text.strip()
    await state.update_data(portfolio_link=val)

    if lang == "ar":
        text = (
            f"💰 *{step_text(5, 5, lang)}*\n\n"
            f"ما هو *سعرك المطلوب*؟ (اختياري)\n\n"
            f"مثال: 20$/ساعة · 50$/مشروع · 500$ شهرياً\n\n"
            f"اكتب *تخطي* إذا أردت تحديده لاحقاً"
        )
    else:
        text = (
            f"💰 *{step_text(5, 5, lang)}*\n\n"
            f"What is your *expected rate*? (optional)\n\n"
            f"e.g., $20/hr · $50/project · $500/month\n\n"
            f"Type *skip* to decide later"
        )
    await message.answer(text, parse_mode="Markdown", reply_markup=_skip_keyboard(lang))
    await state.set_state(ProfileSetup.rate)


# ─────────────────────────────────────────────────────────────────────
# Step 5 — Rate → Save
# ─────────────────────────────────────────────────────────────────────

@router.message(ProfileSetup.rate)
async def handle_rate(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user.get("lang", "ar")
    val  = "" if _is_skip(message.text) else message.text.strip()
    await state.update_data(hourly_rate=val)

    data = await state.get_data()
    await state.clear()

    save_profile(message.from_user.id, data)

    spec       = data.get("specialization", "")
    skills     = data.get("skills", "")
    exp        = data.get("experience_years", "")
    portfolio  = data.get("portfolio_link", "") or ("—" if lang == "ar" else "—")
    rate_saved = data.get("hourly_rate", "") or ("—" if lang == "ar" else "—")

    # Build profile summary
    if lang == "ar":
        summary = (
            f"{SEP}\n"
            f"✅ *تم حفظ ملفك الشخصي!*\n"
            f"{SEP}\n\n"
            f"🎯 *التخصص:* {spec}\n"
            f"🛠️ *المهارات:* {skills}\n"
            f"📅 *الخبرة:* {exp}\n"
            f"🔗 *المحفظة:* {portfolio}\n"
            f"💰 *السعر:* {rate_saved}\n"
            f"{SEP2}\n\n"
            f"🚀 الآن جاهز لاستقبال الفرص المخصصة لك\n"
            f"مع تحليل توافق دقيق لكل مشروع!\n"
            f"{SEP}"
        )
    else:
        summary = (
            f"{SEP}\n"
            f"✅ *Profile Saved!*\n"
            f"{SEP}\n\n"
            f"🎯 *Specialization:* {spec}\n"
            f"🛠️ *Skills:* {skills}\n"
            f"📅 *Experience:* {exp}\n"
            f"🔗 *Portfolio:* {portfolio}\n"
            f"💰 *Rate:* {rate_saved}\n"
            f"{SEP2}\n\n"
            f"🚀 Ready to receive personalized opportunities\n"
            f"with accurate match analysis for every project!\n"
            f"{SEP}"
        )

    await message.answer(
        summary,
        reply_markup=home_menu(lang),
        parse_mode="Markdown"
    )

    # Tell user to now open categories
    hint = (
        "🧭 افتح *الفئات* لبدء المراقبة المستمرة\n"
        "أو *فرصة اليوم* لعرض المشاريع فوراً."
    ) if lang == "ar" else (
        "🧭 Open *Categories* to start continuous monitoring\n"
        "or *Today's Job* to view projects immediately."
    )
    await message.answer(hint, parse_mode="Markdown")
