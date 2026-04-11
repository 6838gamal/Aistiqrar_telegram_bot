from aiogram import Router, types

router = Router()

@router.message()
async def menu(message: types.Message):

    if "📁" in message.text:
        await message.answer("👤 ملفك قيد التطوير")

    elif "🧭" in message.text:
        await message.answer("🎨 تصميم\n💻 برمجة\n✍️ كتابة")

    elif "💡" in message.text:
        await message.answer("اكتب اقتراحك")

    elif "👥" in message.text:
        await message.answer("رابط الدعوة قريبًا")

    elif "❓" in message.text:
        await message.answer("ابدأ بـ 🚀")
