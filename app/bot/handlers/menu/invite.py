from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.database.db import get_user
from app.keyboards.menu import back_button
from app.utils.translator import translator

router = Router()

@router.callback_query(F.data == "page_invite")
async def page_invite(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    me = await call.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start=ref_{call.from_user.id}"
    await call.message.edit_text(
        translator.t("invite_text", lang).format(link=ref_link),
        reply_markup=back_button(lang)
    )
    await call.answer()
