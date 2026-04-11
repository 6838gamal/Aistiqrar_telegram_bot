from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards.menu import back_button

router = Router()

@router.callback_query(F.data == "page_help")
async def page_help(call: CallbackQuery):
    await call.message.edit_text(
        "❓ المساعدة والدعم",
        reply_markup=back_button()
    )
    await call.answer()
