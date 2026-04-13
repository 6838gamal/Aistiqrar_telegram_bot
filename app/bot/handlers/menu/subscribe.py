from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.database.db import get_user
from app.utils.translator import translator
from app.utils.formatting import SEP, SEP2
from app.config import (
    BINANCE_PAY_ID, KARIMI_ACCOUNT,
    SUBSCRIPTION_PRICE, SUBSCRIPTION_DAYS,
    WHATSAPP_LINK, TELEGRAM_CHANNEL
)

router = Router()


def subscribe_keyboard(lang: str) -> InlineKeyboardMarkup:
    back_label = translator.t("menu_back", lang)
    buttons = []
    if WHATSAPP_LINK:
        label = "📩 إرسال الإيصال — واتساب" if lang == "ar" else "📩 Send Receipt — WhatsApp"
        buttons.append([InlineKeyboardButton(text=label, url=WHATSAPP_LINK)])
    if TELEGRAM_CHANNEL:
        label = "📩 إرسال الإيصال — تيليجرام" if lang == "ar" else "📩 Send Receipt — Telegram"
        buttons.append([InlineKeyboardButton(text=label, url=TELEGRAM_CHANNEL)])
    buttons.append([InlineKeyboardButton(text=back_label, callback_data="back_home")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_subscribe_text(lang: str) -> str:
    price = SUBSCRIPTION_PRICE
    days  = SUBSCRIPTION_DAYS

    binance_section = ""
    if BINANCE_PAY_ID:
        if lang == "ar":
            binance_section = (
                f"\n【 1 】🟡 *Binance Pay*\n"
                f"{SEP2}\n"
                f"🔑 معرّف الدفع: `{BINANCE_PAY_ID}`\n\n"
                f"الخطوات:\n"
                f"① افتح تطبيق Binance\n"
                f"② اضغط *Pay* ← *Send*\n"
                f"③ أدخل معرّف الدفع أعلاه\n"
                f"④ أرسل المبلغ المحدد\n"
                f"⑤ احتفظ بصورة الإيصال\n"
            )
        else:
            binance_section = (
                f"\n【 1 】🟡 *Binance Pay*\n"
                f"{SEP2}\n"
                f"🔑 Pay ID: `{BINANCE_PAY_ID}`\n\n"
                f"Steps:\n"
                f"① Open Binance app\n"
                f"② Tap *Pay* → *Send*\n"
                f"③ Enter the Pay ID above\n"
                f"④ Send the exact amount\n"
                f"⑤ Keep the receipt screenshot\n"
            )

    karimi_section = ""
    if KARIMI_ACCOUNT:
        if lang == "ar":
            karimi_section = (
                f"\n【 2 】💵 *صرافة كريمي*\n"
                f"{SEP2}\n"
                f"📱 رقم الحساب: `{KARIMI_ACCOUNT}`\n\n"
                f"الخطوات:\n"
                f"① تواصل مع صرافة كريمي\n"
                f"② اذكر اسم المنصة: *استقرار*\n"
                f"③ أرسل المبلغ المحدد\n"
                f"④ احتفظ بصورة الإيصال\n"
            )
        else:
            karimi_section = (
                f"\n【 2 】💵 *Karimi Exchange*\n"
                f"{SEP2}\n"
                f"📱 Account: `{KARIMI_ACCOUNT}`\n\n"
                f"Steps:\n"
                f"① Contact Karimi Exchange\n"
                f"② Mention platform: *Aistiqrar*\n"
                f"③ Send the exact amount\n"
                f"④ Keep the receipt screenshot\n"
            )

    num = 3 if (BINANCE_PAY_ID and KARIMI_ACCOUNT) else (2 if (BINANCE_PAY_ID or KARIMI_ACCOUNT) else 1)
    if lang == "ar":
        other_section = (
            f"\n【 {num} 】📱 *تطبيقات الصرافة الأخرى*\n"
            f"{SEP2}\n"
            f"تواصل معنا للحصول على تفاصيل الإرسال عبر تطبيقات مثل:\n"
            f"STC Pay • Vodafone Cash • ويسترن يونيون وغيرها\n"
        )
        text = (
            f"{SEP}\n"
            f"💎 *الاشتراك في منصة استقرار*\n"
            f"{SEP}\n\n"
            f"📦 *خطة الاشتراك:*\n"
            f"• المدة: {days} يوم\n"
            f"• السعر: *{price}$*\n"
            f"\n{SEP}\n"
            f"💳 *طرق الدفع المتاحة:*\n"
            f"{binance_section}"
            f"{karimi_section}"
            f"{other_section}"
            f"\n{SEP}\n"
            f"📩 *بعد الدفع:*\n"
            f"أرسل صورة الإيصال عبر الأزرار أدناه\n"
            f"وسيتم تفعيل اشتراكك خلال ساعة ✅\n"
            f"{SEP}"
        )
    else:
        other_section = (
            f"\n【 {num} 】📱 *Other Exchange Apps*\n"
            f"{SEP2}\n"
            f"Contact us for transfer details via:\n"
            f"STC Pay • Vodafone Cash • Western Union & more\n"
        )
        text = (
            f"{SEP}\n"
            f"💎 *Subscribe to Aistiqrar Platform*\n"
            f"{SEP}\n\n"
            f"📦 *Subscription Plan:*\n"
            f"• Duration: {days} days\n"
            f"• Price: *${price}*\n"
            f"\n{SEP}\n"
            f"💳 *Available Payment Methods:*\n"
            f"{binance_section}"
            f"{karimi_section}"
            f"{other_section}"
            f"\n{SEP}\n"
            f"📩 *After Payment:*\n"
            f"Send your receipt screenshot using the buttons below\n"
            f"Your subscription will be activated within 1 hour ✅\n"
            f"{SEP}"
        )

    return text


@router.callback_query(F.data == "page_subscribe")
async def page_subscribe(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    text = build_subscribe_text(lang)
    await call.message.answer(
        text,
        reply_markup=subscribe_keyboard(lang),
        parse_mode="Markdown"
    )
    await call.answer()
