from aiogram import Router, types
from app.utils.commands import match_command

router = Router()

@router.message()
async def menu(message: types.Message):
    cmd = match_command(message.text)

    if not cmd:
        return

    if cmd == "profile":
        await message.answer("👤 ملفك قيد التطوير")

    elif cmd == "categories":
        await message.answer("🎨 تصميم\n💻 برمجة\n✍️ كتابة")

    elif cmd == "suggest":
        await message.answer("💡 اكتب اقتراحك")

    elif cmd == "invite":
        await message.answer("👥 شارك البوت مع أصدقائك")

    elif cmd == "help":
        await message.answer("❓ اكتب job أو اختر من القائمة")
