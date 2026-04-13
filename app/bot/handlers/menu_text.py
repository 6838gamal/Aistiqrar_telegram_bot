from aiogram import Router, types, F
from app.database.storage import get_user
from app.database.db import get_user as db_get_user, get_selected_categories, get_favorites
from app.utils.translator import translator
from app.keyboards.menu import back_button, home_menu, lang_keyboard
from app.keyboards.categories import categories_keyboard
from app.utils.commands import match_command
from app.config import WHATSAPP_LINK, TELEGRAM_CHANNEL, INSTAGRAM_LINK, MESSENGER_LINK, CONTACT_EMAIL
from app.bot.handlers.menu.about import ABOUT_AR, ABOUT_EN
from app.bot.handlers.menu.contact import contact_keyboard

router = Router()

@router.message(F.text)
async def text_handler(message: types.Message):
    text = message.text
    user_data = get_user(message.from_user.id)
    lang = user_data.get("lang", "ar")

    if "🚀" in text and "ابدأ" in text or "🚀" in text and "Start" in text:
        await message.answer(
            translator.t("start_work", lang),
            reply_markup=back_button(lang)
        )
        return

    cmd = match_command(text)
    if not cmd:
        return

    if cmd == "back":
        await message.answer(
            translator.t("home_text", lang),
            reply_markup=home_menu(lang)
        )

    elif cmd == "job":
        from app.services.scraper import fetch_projects
        from app.bot.handlers.menu.job import _format_project, _project_keyboard
        projects = fetch_projects()
        if not projects:
            await message.answer(
                "⚠️ لا توجد مشاريع متاحة حالياً." if lang == "ar"
                else "⚠️ No projects available right now.",
                reply_markup=back_button(lang)
            )
            return
        for p in projects:
            await message.answer(
                _format_project(p, lang),
                reply_markup=_project_keyboard(p, lang),
                parse_mode="Markdown"
            )

    elif cmd == "profile":
        full = db_get_user(message.from_user.id)
        referral_count = full.get("referral_count", 0) if full else 0
        join_type = full.get("join_type", "direct") if full else "direct"
        join_label = translator.t("join_referral", lang) if join_type == "referral" else translator.t("join_direct", lang)
        await message.answer(
            translator.t("profile_text", lang).format(
                id=message.from_user.id,
                name=message.from_user.full_name,
                join_type=join_label,
                referrals=referral_count
            ),
            reply_markup=back_button(lang)
        )

    elif cmd == "categories":
        selected = get_selected_categories(message.from_user.id)
        await message.answer(
            translator.t("categories_text", lang),
            reply_markup=categories_keyboard(lang, selected)
        )

    elif cmd == "suggest":
        await message.answer(
            translator.t("suggest_text", lang),
            reply_markup=back_button(lang)
        )

    elif cmd == "invite":
        me = await message.bot.get_me()
        ref_link = f"https://t.me/{me.username}?start=ref_{message.from_user.id}"
        await message.answer(
            translator.t("invite_text", lang).format(link=ref_link),
            reply_markup=back_button(lang)
        )

    elif cmd == "channels":
        await message.answer(
            translator.t("channels_text", lang).format(
                whatsapp=WHATSAPP_LINK,
                telegram=TELEGRAM_CHANNEL
            ),
            reply_markup=back_button(lang)
        )

    elif cmd == "settings":
        await message.answer(
            translator.t("settings_text", lang),
            reply_markup=lang_keyboard(lang)
        )

    elif cmd == "help":
        await message.answer(
            translator.t("help_text", lang),
            reply_markup=back_button(lang)
        )

    elif cmd == "favorites":
        favs = get_favorites(message.from_user.id)
        if not favs:
            text_out = "⭐ *مفضلتك فارغة*\n\nلم تقم بإضافة أي مشروع بعد." if lang == "ar" \
                       else "⭐ *Your favorites list is empty*\n\nYou haven't saved any projects yet."
            await message.answer(text_out, reply_markup=back_button(lang), parse_mode="Markdown")
        else:
            header = f"⭐ *مفضلتك* — {len(favs)} مشروع\n\n" if lang == "ar" \
                     else f"⭐ *Your Favorites* — {len(favs)} projects\n\n"
            lines = []
            for i, fav in enumerate(favs[:20], 1):
                title = fav['title'][:35] + ("..." if len(fav['title']) > 35 else "")
                lines.append(f"{i}. [{title}]({fav['link']})")
            await message.answer(
                header + "\n".join(lines),
                reply_markup=back_button(lang),
                parse_mode="Markdown",
                disable_web_page_preview=True
            )

    elif cmd == "about":
        text_out = ABOUT_AR if lang == "ar" else ABOUT_EN
        await message.answer(text_out, reply_markup=back_button(lang), parse_mode="Markdown")

    elif cmd == "contact":
        text_out = (
            "📞 *تواصل معنا*\n\nنحن هنا للمساعدة! اختر وسيلة التواصل المناسبة:"
            if lang == "ar" else
            "📞 *Contact Us*\n\nWe're here to help! Choose your preferred contact method:"
        )
        await message.answer(text_out, reply_markup=contact_keyboard(lang), parse_mode="Markdown")
