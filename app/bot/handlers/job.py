from aiogram import Router, types
from app.database.storage import get_user
from app.services.job_service import get_job
from app.utils.translator import translator
from app.utils.commands import match_command
from app.keyboards.menu import back_button

router = Router()

@router.message()
async def job_handler(message: types.Message):
    if not message.text:
        return

    cmd = match_command(message.text)

    if cmd != "job":
        return

    user = get_user(message.from_user.id)
    lang = user["lang"]

    job_data = get_job()

    await message.answer(
        f"{translator.t('job_title', lang)}\n\n"
        f"📌 {job_data['title']}\n"
        f"💰 {job_data['price']}\n"
        f"🌐 {job_data['platform']}\n\n"
        f"{translator.t('verified', lang)}",
        reply_markup=back_button(lang)
    )
