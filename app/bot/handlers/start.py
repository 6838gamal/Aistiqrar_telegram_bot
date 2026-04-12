from aiogram import Router, types
from app.database.storage import set_user
from app.keyboards.main_menu import home_menu

router = Router()

@router.message(lambda m: m.text and "start" in m.text.lower())
async def start_handler(message: types.Message):
    user_id = message.from_user.id

    # حفظ المستخدم
    set_user(user_id, "ar")

    await message.answer(
        "👋 أهلاً بك في منصة استقرار\n\n"
        "💼 سنساعدك في إيجاد فرص عمل حقيقية\n"
        "🚀 ابدأ الآن من القائمة بالأسفل",
        reply_markup=home_menu("ar")
    )
