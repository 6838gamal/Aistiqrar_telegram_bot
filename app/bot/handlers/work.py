from aiogram import Router, types
from app.database.storage import get_user
from app.utils.translator import translator
from app.keyboards.menu import back_button

router = Router()

@router.message()
async def work(message: types.Message):
    if not message.text:
        return

    user = get_user(message.from_user.id)
    lang = user["lang"]

    if "🚀" in message.text:
        await message.answer(
            translator.t("start_work", lang),
            reply_markup=back_button(lang)
        )
