from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.database.db import get_user
from app.utils.translator import translator
from app.config import (
    WHATSAPP_LINK, TELEGRAM_CHANNEL,
    CONTACT_EMAIL, INSTAGRAM_LINK, MESSENGER_LINK
)

router = Router()


def contact_keyboard(lang: str) -> InlineKeyboardMarkup:
    back_label = translator.t("menu_back", lang)
    buttons = []

    if WHATSAPP_LINK:
        buttons.append([InlineKeyboardButton(text="💬 واتساب | WhatsApp", url=WHATSAPP_LINK)])
    if TELEGRAM_CHANNEL:
        buttons.append([InlineKeyboardButton(text="✈️ تيليجرام | Telegram", url=TELEGRAM_CHANNEL)])
    if INSTAGRAM_LINK:
        buttons.append([InlineKeyboardButton(text="📸 إنستغرام | Instagram", url=INSTAGRAM_LINK)])
    if MESSENGER_LINK:
        buttons.append([InlineKeyboardButton(text="💬 ماسنجر | Messenger", url=MESSENGER_LINK)])
    if CONTACT_EMAIL:
        buttons.append([InlineKeyboardButton(text="📧 إيميل | Email", url=f"mailto:{CONTACT_EMAIL}")])

    buttons.append([InlineKeyboardButton(text=back_label, callback_data="back_home")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "page_contact")
async def page_contact(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")

    if lang == "ar":
        text = (
            "📞 *تواصل معنا*\n\n"
            "نحن هنا للمساعدة! اختر وسيلة التواصل المناسبة:"
        )
    else:
        text = (
            "📞 *Contact Us*\n\n"
            "We're here to help! Choose your preferred contact method:"
        )

    await call.message.edit_text(
        text,
        reply_markup=contact_keyboard(lang),
        parse_mode="Markdown"
    )
    await call.answer()
