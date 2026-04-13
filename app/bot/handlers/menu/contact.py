from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.database.db import get_user
from app.utils.translator import translator
from app.utils.formatting import SEP, SEP2
from app.config import (
    WHATSAPP_LINK, TELEGRAM_CHANNEL,
    CONTACT_EMAIL, INSTAGRAM_LINK, MESSENGER_LINK
)

router = Router()


def contact_keyboard(lang: str) -> InlineKeyboardMarkup:
    back_label = translator.t("menu_back", lang)
    buttons = []
    if WHATSAPP_LINK:
        buttons.append([InlineKeyboardButton(text="💬 واتساب — دعم فوري", url=WHATSAPP_LINK)])
    if TELEGRAM_CHANNEL:
        buttons.append([InlineKeyboardButton(text="✈️ تيليجرام — استفسارات", url=TELEGRAM_CHANNEL)])
    if INSTAGRAM_LINK:
        buttons.append([InlineKeyboardButton(text="📸 إنستغرام — أخبار ومستجدات", url=INSTAGRAM_LINK)])
    if MESSENGER_LINK:
        buttons.append([InlineKeyboardButton(text="💬 ماسنجر — محادثات", url=MESSENGER_LINK)])
    if CONTACT_EMAIL:
        buttons.append([InlineKeyboardButton(text="📧 إيميل — مراسلات رسمية", url=f"mailto:{CONTACT_EMAIL}")])
    buttons.append([InlineKeyboardButton(text=back_label, callback_data="back_home")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "page_contact")
async def page_contact(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")

    if lang == "ar":
        text = (
            f"{SEP}\n"
            f"📞 *تواصل معنا*\n"
            f"{SEP}\n\n"
            f"نحن هنا لمساعدتك على مدار الساعة ✅\n\n"
            f"{SEP2}\n"
            f"💬 *واتساب* — للدعم الفوري والاستجابة السريعة\n"
            f"✈️ *تيليجرام* — للاستفسارات والاشتراك\n"
            f"📸 *إنستغرام* — لمتابعة الأخبار والمستجدات\n"
            f"💬 *ماسنجر* — للمحادثات العامة\n"
            f"📧 *إيميل* — للمراسلات الرسمية\n"
            f"{SEP2}\n\n"
            f"⏱️ *وقت الرد:* خلال ساعة في أغلب الأوقات\n"
            f"{SEP}"
        )
    else:
        text = (
            f"{SEP}\n"
            f"📞 *Contact Us*\n"
            f"{SEP}\n\n"
            f"We're here to help you 24/7 ✅\n\n"
            f"{SEP2}\n"
            f"💬 *WhatsApp* — Instant support & fast replies\n"
            f"✈️ *Telegram* — Inquiries & subscriptions\n"
            f"📸 *Instagram* — News & updates\n"
            f"💬 *Messenger* — General chat\n"
            f"📧 *Email* — Official correspondence\n"
            f"{SEP2}\n\n"
            f"⏱️ *Response time:* Usually within 1 hour\n"
            f"{SEP}"
        )

    await call.message.edit_text(text, reply_markup=contact_keyboard(lang), parse_mode="Markdown")
    await call.answer()
