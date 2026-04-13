from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.database.db import update_user_lang, get_user
from app.keyboards.menu import home_menu
from app.utils.translator import translator

router = Router()

@router.callback_query(F.data.startswith("set_lang:"))
async def set_language(call: CallbackQuery):
    data = call.data.split(":")[1]

    if data == "back":
        user = get_user(call.from_user.id)
        lang = user.get("lang", "ar")
        await call.message.answer(
            translator.t("home_text", lang),
            reply_markup=home_menu(lang)
        )
        await call.answer()
        return

    lang = data
    update_user_lang(call.from_user.id, lang)

    if lang == "ar":
        confirm = translator.t("lang_changed_ar", "ar")
    else:
        confirm = translator.t("lang_changed_en", "en")

    await call.message.answer(confirm, reply_markup=home_menu(lang))
    await call.answer()
