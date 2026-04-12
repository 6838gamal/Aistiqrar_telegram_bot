from aiogram import Router, types
from aiogram.filters import CommandStart

from app.database.storage import set_user
from app.keyboards.main_menu import home_menu

router = Router()

# 🔥 هذا هو الحل الصحيح بدل lambda
@router.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id

    set_user(user_id, "ar")

    await message.answer(
        "👋 أهلاً بك في منصة استقرار\n\n"
        "💼 سنساعدك في إيجاد فرص عمل حقيقية\n"
        "🚀 استخدم القائمة بالأسفل",
        reply_markup=home_menu("ar")
    )
