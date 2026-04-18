from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.database.db import (
    get_user, get_selected_categories, get_favorites,
    is_profile_complete, get_profile
)
from app.utils.translator import translator
from app.keyboards.menu import back_button, home_menu, lang_keyboard
from app.keyboards.categories import categories_keyboard
from app.utils.commands import match_command
from app.utils.formatting import SEP, SEP2, format_project
from app.utils.matching import calc_match
from app.config import WHATSAPP_LINK, TELEGRAM_CHANNEL
from app.bot.handlers.menu.about import ABOUT_AR, ABOUT_EN
from app.bot.handlers.menu.contact import contact_keyboard
from app.bot.handlers.menu.subscribe import build_subscribe_text, subscribe_keyboard
from app.bot.handlers.profile_setup import start_profile_setup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


def _profile_incomplete_msg(lang: str) -> str:
    return (
        f"{SEP}\n⚠️ *أكمل ملفك الشخصي أولاً*\n{SEP}\n\n"
        f"✅ فرص مخصصة حسب مهاراتك\n"
        f"📊 نسبة توافق مع كل مشروع\n"
        f"💡 نصائح لرفع فرص القبول\n\n"
        f"اضغط أدناه لإكمال الملف (أقل من دقيقتين) ⏱️"
    ) if lang == "ar" else (
        f"{SEP}\n⚠️ *Complete Your Profile First*\n{SEP}\n\n"
        f"✅ Personalized opportunities by skill\n"
        f"📊 Match score for every project\n"
        f"💡 Tips to boost acceptance chances\n\n"
        f"Tap below to complete your profile (< 2 min) ⏱️"
    )


def _profile_incomplete_kb(lang: str) -> InlineKeyboardMarkup:
    label = "🚀 إكمال الملف الشخصي" if lang == "ar" else "🚀 Complete Profile"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, callback_data="profile_edit")]
    ])


@router.message(F.text)
async def text_handler(message: types.Message, state: FSMContext):
    text = message.text or ""
    user_data = get_user(message.from_user.id)
    lang = user_data.get("lang", "ar")

    # Start working session
    if ("🚀" in text and "ابدأ" in text) or ("🚀" in text and "Start" in text):
        await message.answer(
            translator.t("start_work", lang),
            reply_markup=back_button(lang)
        )
        return

    cmd = match_command(text)
    if not cmd:
        return

    # ── Back ──────────────────────────────────────────────────────────
    if cmd == "back":
        await message.answer(
            translator.t("home_text", lang),
            reply_markup=home_menu(lang)
        )

    # ── Today's Job ───────────────────────────────────────────────────
    elif cmd == "job":
        if not is_profile_complete(message.from_user.id):
            await message.answer(
                _profile_incomplete_msg(lang),
                reply_markup=_profile_incomplete_kb(lang),
                parse_mode="Markdown"
            )
            return

        from app.services.scraper import fetch_projects
        from app.bot.handlers.menu.job import _project_keyboard
        projects = fetch_projects()
        if not projects:
            await message.answer(
                "⚠️ لا توجد مشاريع متاحة حالياً." if lang == "ar"
                else "⚠️ No projects available right now.",
                reply_markup=back_button(lang)
            )
            return
        profile = get_profile(message.from_user.id)
        for p in projects:
            match = calc_match(profile, p)
            await message.answer(
                format_project(p, lang, match=match),
                reply_markup=_project_keyboard(p, lang),
                parse_mode="Markdown"
            )

    # ── Profile ───────────────────────────────────────────────────────
    elif cmd == "profile":
        from app.bot.handlers.menu.profile import _profile_display, _profile_keyboard
        user_full = get_user(message.from_user.id)
        completed = bool(user_full.get("profile_completed"))
        await message.answer(
            _profile_display(user_full, lang),
            reply_markup=_profile_keyboard(lang, completed),
            parse_mode="Markdown"
        )

    # ── Categories ────────────────────────────────────────────────────
    elif cmd == "categories":
        if not is_profile_complete(message.from_user.id):
            await message.answer(
                _profile_incomplete_msg(lang),
                reply_markup=_profile_incomplete_kb(lang),
                parse_mode="Markdown"
            )
            return
        selected = get_selected_categories(message.from_user.id)
        await message.answer(
            translator.t("categories_text", lang),
            reply_markup=categories_keyboard(lang, selected)
        )

    # ── Suggest ───────────────────────────────────────────────────────
    elif cmd == "suggest":
        await message.answer(
            translator.t("suggest_text", lang),
            reply_markup=back_button(lang)
        )

    # ── Invite ────────────────────────────────────────────────────────
    elif cmd == "invite":
        me = await message.bot.get_me()
        ref_link = f"https://t.me/{me.username}?start=ref_{message.from_user.id}"
        await message.answer(
            translator.t("invite_text", lang).format(link=ref_link),
            reply_markup=back_button(lang)
        )

    # ── Channels ──────────────────────────────────────────────────────
    elif cmd == "channels":
        await message.answer(
            translator.t("channels_text", lang).format(
                whatsapp=WHATSAPP_LINK,
                telegram=TELEGRAM_CHANNEL
            ),
            reply_markup=back_button(lang)
        )

    # ── Settings ──────────────────────────────────────────────────────
    elif cmd == "settings":
        await message.answer(
            translator.t("settings_text", lang),
            reply_markup=lang_keyboard(lang)
        )

    # ── Help ──────────────────────────────────────────────────────────
    elif cmd == "help":
        from app.bot.handlers.menu.help import HELP_AR, HELP_EN, help_keyboard
        txt = HELP_AR if lang == "ar" else HELP_EN
        await message.answer(txt, reply_markup=help_keyboard(lang), parse_mode="Markdown")

    # ── Favorites ─────────────────────────────────────────────────────
    elif cmd == "favorites":
        favs = get_favorites(message.from_user.id)
        back_label = translator.t("menu_back", lang)
        if not favs:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            empty_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=back_label, callback_data="back_home")]
            ])
            text_out = (
                f"{SEP}\n⭐ *مفضلتك*\n{SEP}\n\n"
                f"لم تقم بإضافة أي مشروع بعد.\n\n"
                f"اضغط ⭐ على أي مشروع لحفظه هنا."
            ) if lang == "ar" else (
                f"{SEP}\n⭐ *Favorites*\n{SEP}\n\n"
                f"No saved projects yet.\n\n"
                f"Tap ⭐ on any project to save it here."
            )
            await message.answer(text_out, reply_markup=empty_kb, parse_mode="Markdown")
        else:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            header = (
                f"{SEP}\n⭐ *مفضلتك* — {len(favs)} مشروع\n{SEP}\n\n"
                f"اضغط على أي مشروع لفتحه:\n{SEP2}\n"
            ) if lang == "ar" else (
                f"{SEP}\n⭐ *Favorites* — {len(favs)} projects\n{SEP}\n\n"
                f"Tap any project to open it:\n{SEP2}\n"
            )
            buttons = [
                [InlineKeyboardButton(
                    text=f"📌 {i}. {fav['title'][:40]}",
                    url=fav["link"]
                )]
                for i, fav in enumerate(favs[:20], 1)
            ]
            buttons.append([InlineKeyboardButton(text=back_label, callback_data="back_home")])
            await message.answer(
                header,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
                parse_mode="Markdown"
            )

    # ── About ─────────────────────────────────────────────────────────
    elif cmd == "about":
        text_out = ABOUT_AR if lang == "ar" else ABOUT_EN
        await message.answer(text_out, reply_markup=back_button(lang), parse_mode="Markdown")

    # ── Contact ───────────────────────────────────────────────────────
    elif cmd == "contact":
        text_out = (
            f"{SEP}\n📞 *تواصل معنا*\n{SEP}\n\nاختر وسيلة التواصل المناسبة:"
        ) if lang == "ar" else (
            f"{SEP}\n📞 *Contact Us*\n{SEP}\n\nChoose your preferred contact method:"
        )
        await message.answer(text_out, reply_markup=contact_keyboard(lang), parse_mode="Markdown")

    # ── Subscribe ─────────────────────────────────────────────────────
    elif cmd == "subscribe":
        await message.answer(
            build_subscribe_text(lang),
            reply_markup=subscribe_keyboard(lang),
            parse_mode="Markdown"
        )
