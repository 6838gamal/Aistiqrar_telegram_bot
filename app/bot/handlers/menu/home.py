from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.database.db import get_user
from app.keyboards.menu import home_menu
from app.utils.translator import translator

router = Router()


@router.callback_query(F.data == "back_home")
async def back_home(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    await call.message.edit_text(
        translator.t("home_text", lang),
        reply_markup=home_menu(lang)
    )
    await call.answer()
