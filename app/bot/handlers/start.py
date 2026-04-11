from aiogram import Router, types
from app.database.storage import set_user
from app.keyboards.main_menu import main_menu

router = Router()

@router.message(lambda m: m.text == "/start")
async def start(message: types.Message):
    await message.answer("🇸🇦 عربي / 🇺🇸 English")

@router.message(lambda m: m.text in ["🇸🇦 عربي", "🇺🇸 English"])
async def set_lang(message: types.Message):
    lang = "ar" if "عربي" in message.text else "en"
    set_user(message.from_user.id, lang)

    await message.answer(
        "✅ Done",
        reply_markup=main_menu(lang)
    )
