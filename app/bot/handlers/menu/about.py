from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.database.db import get_user
from app.keyboards.menu import back_button
from app.utils.formatting import SEP, SEP2

router = Router()

ABOUT_AR = (
    f"{SEP}\n"
    "⚡ *منصة استقرار*\n"
    f"{SEP}\n\n"
    "👤 *عن المطور:*\n"
    f"{SEP2}\n"
    "مطور متخصص في بناء أدوات ذكية تخدم المستقلين العرب وتوفر لهم الوقت والجهد.\n\n"
    f"{SEP}\n\n"
    "🎯 *الهدف:*\n"
    f"{SEP2}\n"
    "مساعدة المستقلين العرب في إيجاد فرص عمل حقيقية، بشكل تلقائي ومباشر على هواتفهم — دون عناء البحث اليدوي.\n\n"
    f"{SEP}\n\n"
    "🛠️ *التقنيات المستخدمة:*\n"
    f"{SEP2}\n"
    "• Python & Aiogram v3\n"
    "• FastAPI & SQLite\n"
    "• Web Scraping & Real-time Monitoring\n"
    "• Async Task Management\n\n"
    f"{SEP}\n\n"
    "💡 *الرؤية:*\n"
    f"{SEP2}\n"
    "بناء منظومة ذكية متكاملة تجمع فرص العمل الحر من مختلف المنصات وتوصلها للمستقل لحظة بلحظة.\n\n"
    f"{SEP}\n\n"
    "📌 *الإصدار:* 1.0.0\n"
    "📬 *للتواصل:* استخدم قسم تواصل معنا\n"
    f"{SEP}"
)

ABOUT_EN = (
    f"{SEP}\n"
    "⚡ *Aistiqrar Platform*\n"
    f"{SEP}\n\n"
    "👤 *About the Developer:*\n"
    f"{SEP2}\n"
    "A developer specialized in building smart tools that serve Arab freelancers, saving them time and effort.\n\n"
    f"{SEP}\n\n"
    "🎯 *Mission:*\n"
    f"{SEP2}\n"
    "Helping Arab freelancers find real job opportunities automatically and directly on their phones — no manual searching needed.\n\n"
    f"{SEP}\n\n"
    "🛠️ *Tech Stack:*\n"
    f"{SEP2}\n"
    "• Python & Aiogram v3\n"
    "• FastAPI & SQLite\n"
    "• Web Scraping & Real-time Monitoring\n"
    "• Async Task Management\n\n"
    f"{SEP}\n\n"
    "💡 *Vision:*\n"
    f"{SEP2}\n"
    "Build an integrated smart system that aggregates freelance opportunities from various platforms and delivers them in real-time.\n\n"
    f"{SEP}\n\n"
    "📌 *Version:* 1.0.0\n"
    "📬 *Contact:* Use the Contact Us section\n"
    f"{SEP}"
)


@router.callback_query(F.data == "page_about")
async def page_about(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    text = ABOUT_AR if lang == "ar" else ABOUT_EN
    await call.message.edit_text(text, reply_markup=back_button(lang), parse_mode="Markdown")
    await call.answer()
