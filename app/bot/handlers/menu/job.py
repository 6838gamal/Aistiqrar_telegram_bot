from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.database.db import get_user
from app.keyboards.menu import back_button
from app.services.job_service import get_job
from app.utils.translator import translator

router = Router()

@router.callback_query(F.data == "page_job")
async def page_job(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    job = get_job()
    await call.message.edit_text(
        f"{translator.t('job_title', lang)}\n\n"
        f"📌 {job['title']}\n"
        f"💰 {job['price']}\n"
        f"🌐 {job['platform']}\n\n"
        f"{translator.t('verified', lang)}",
        reply_markup=back_button(lang)
    )
    await call.answer()
