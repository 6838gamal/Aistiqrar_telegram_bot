from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.database.db import get_user
from app.keyboards.menu import back_button
from app.utils.translator import translator

router = Router()

@router.callback_query(F.data == "page_profile")
async def page_profile(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    referral_count = user.get("referral_count", 0)
    join_type = user.get("join_type", "direct")
    join_label = translator.t("join_referral", lang) if join_type == "referral" else translator.t("join_direct", lang)
    await call.message.edit_text(
        translator.t("profile_text", lang).format(
            id=call.from_user.id,
            name=call.from_user.full_name,
            join_type=join_label,
            referrals=referral_count
        ),
        reply_markup=back_button(lang)
    )
    await call.answer()
