from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards.menu import back_button

router = Router()

@router.callback_query(F.data == "page_profile")
async def page_profile(call: CallbackQuery):
    await call.message.edit_text(
        "👤 الملف الشخصي",
        reply_markup=back_button()
    )
    await call.answer()
