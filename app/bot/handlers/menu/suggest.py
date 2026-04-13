from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.database.db import get_user
from app.keyboards.menu import back_button
from app.utils.translator import translator

router = Router()

@router.callback_query(F.data == "page_suggest")
async def page_suggest(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    await call.message.edit_text(
        translator.t("suggest_text", lang),
        reply_markup=back_button(lang)
    )
    await call.answer()
