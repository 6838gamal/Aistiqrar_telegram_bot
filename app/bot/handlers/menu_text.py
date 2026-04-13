from aiogram import Router, types, F
from app.database.storage import get_user
from app.database.db import get_user as db_get_user, get_selected_categories
from app.services.job_service import get_job
from app.utils.translator import translator
from app.keyboards.menu import back_button, home_menu, lang_keyboard
from app.keyboards.categories import categories_keyboard
from app.utils.commands import match_command
from app.config import WHATSAPP_LINK, TELEGRAM_CHANNEL

router = Router()

@router.message(F.text)
async def text_handler(message: types.Message):
    text = message.text
    user_data = get_user(message.from_user.id)
    lang = user_data.get("lang", "ar")

    if "🚀" in text:
        await message.answer(
            translator.t("start_work", lang),
            reply_markup=back_button(lang)
        )
        return

    cmd = match_command(text)
    if not cmd:
        return

    if cmd == "back":
        await message.answer(
            translator.t("home_text", lang),
            reply_markup=home_menu(lang)
        )

    elif cmd == "job":
        job_data = get_job()
        await message.answer(
            f"{translator.t('job_title', lang)}\n\n"
            f"📌 {job_data['title']}\n"
            f"💰 {job_data['price']}\n"
            f"🌐 {job_data['platform']}\n\n"
            f"{translator.t('verified', lang)}",
            reply_markup=back_button(lang)
        )

    elif cmd == "profile":
        full = db_get_user(message.from_user.id)
        referral_count = full.get("referral_count", 0) if full else 0
        join_type = full.get("join_type", "direct") if full else "direct"
        join_label = translator.t("join_referral", lang) if join_type == "referral" else translator.t("join_direct", lang)
        await message.answer(
            translator.t("profile_text", lang).format(
                id=message.from_user.id,
                name=message.from_user.full_name,
                join_type=join_label,
                referrals=referral_count
            ),
            reply_markup=back_button(lang)
        )

    elif cmd == "categories":
        selected = get_selected_categories(message.from_user.id)
        await message.answer(
            translator.t("categories_text", lang),
            reply_markup=categories_keyboard(lang, selected)
        )

    elif cmd == "suggest":
        await message.answer(
            translator.t("suggest_text", lang),
            reply_markup=back_button(lang)
        )

    elif cmd == "invite":
        me = await message.bot.get_me()
        ref_link = f"https://t.me/{me.username}?start=ref_{message.from_user.id}"
        await message.answer(
            translator.t("invite_text", lang).format(link=ref_link),
            reply_markup=back_button(lang)
        )

    elif cmd == "channels":
        await message.answer(
            translator.t("channels_text", lang).format(
                whatsapp=WHATSAPP_LINK,
                telegram=TELEGRAM_CHANNEL
            ),
            reply_markup=back_button(lang)
        )

    elif cmd == "settings":
        await message.answer(
            translator.t("settings_text", lang),
            reply_markup=lang_keyboard(lang)
        )

    elif cmd == "help":
        await message.answer(
            translator.t("help_text", lang),
            reply_markup=back_button(lang)
        )
