from aiogram import Router, types
from app.database.storage import get_user
from app.services.job_service import get_job
from app.utils.translator import translator
from app.utils.commands import match_command

router = Router()

@router.message()
async def job(message: types.Message):
    cmd = match_command(message.text)

    if cmd != "job":
        return

    user = get_user(message.from_user.id)
    lang = user["lang"]

    job = get_job()

    await message.answer(f"""
{translator.t("job_title", lang)}

{job['title']}
💰 {job['price']}
🌐 {job['platform']}

{translator.t("verified", lang)}
""")
