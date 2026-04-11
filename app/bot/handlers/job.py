from aiogram import Router, types
from app.database.storage import get_user
from app.services.job_service import get_job
from app.utils.translator import translator

router = Router()

@router.message()
async def job(message: types.Message):
    user = get_user(message.from_user.id)
    lang = user["lang"]

    if "💼" in message.text:
        job = get_job()

        await message.answer(f"""
{translator.t("job_title", lang)}

{job['title']}
💰 {job['price']}
🌐 {job['platform']}

{translator.t("verified", lang)}
""")
