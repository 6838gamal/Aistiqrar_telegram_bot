from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject

from app.database.db import get_user as db_get_user
from app.database.storage import set_user
from app.keyboards.menu import home_menu
from app.utils.translator import translator

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message, command: CommandObject):
    user = message.from_user
    user_id = user.id
    name = user.full_name or ""
    username = user.username or ""

    referred_by = None
    args = command.args
    if args and args.startswith("ref_"):
        try:
            ref_id = int(args[4:])
            if ref_id != user_id:
                referred_by = ref_id
        except ValueError:
            pass

    existing = db_get_user(user_id)
    lang = existing.get("lang", "ar") if existing else "ar"

    set_user(user_id, lang=lang, name=name, username=username, referred_by=referred_by)

    welcome = translator.t("welcome", lang)
    if referred_by:
        welcome += translator.t("welcome_referral", lang)

    await message.answer(welcome, reply_markup=home_menu(lang))
