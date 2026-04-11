from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards.menu import home_menu

router = Router()


@router.callback_query(F.data == "back_home")
async def back_home(call: CallbackQuery):
    await call.message.edit_text(
        "🏠 القائمة الرئيسية:",
        reply_markup=home_menu()
    )
    await call.answer()
