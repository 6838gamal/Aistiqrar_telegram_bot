from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.database.db import get_user
from app.keyboards.menu import back_button
from app.utils.translator import translator

router = Router()

ABOUT_AR = (
    "👤 *عن المطور*\n\n"
    "مرحباً! أنا المطور خلف منصة *استقرار* 👋\n\n"
    "🎯 *الهدف:*\n"
    "مساعدة المستقلين العرب في إيجاد فرص عمل حقيقية وبشكل تلقائي ومباشر.\n\n"
    "🛠️ *التقنيات المستخدمة:*\n"
    "• Python & Aiogram v3\n"
    "• FastAPI & SQLite\n"
    "• Web Scraping & Real-time Monitoring\n\n"
    "💡 *الرؤية:*\n"
    "بناء أداة ذكية تجمع فرص العمل الحر وتوصلها للمستقل مباشرة على هاتفه.\n\n"
    "📬 للتواصل أو الاستفسار، استخدم قسم *تواصل معنا*."
)

ABOUT_EN = (
    "👤 *About the Developer*\n\n"
    "Hello! I'm the developer behind *Aistiqrar* platform 👋\n\n"
    "🎯 *Mission:*\n"
    "Helping Arab freelancers find real job opportunities automatically and directly.\n\n"
    "🛠️ *Tech Stack:*\n"
    "• Python & Aiogram v3\n"
    "• FastAPI & SQLite\n"
    "• Web Scraping & Real-time Monitoring\n\n"
    "💡 *Vision:*\n"
    "Build a smart tool that aggregates freelance opportunities and delivers them directly to your phone.\n\n"
    "📬 For inquiries, use the *Contact Us* section."
)


@router.callback_query(F.data == "page_about")
async def page_about(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    text = ABOUT_AR if lang == "ar" else ABOUT_EN
    await call.message.edit_text(text, reply_markup=back_button(lang), parse_mode="Markdown")
    await call.answer()
