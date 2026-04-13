from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.database.db import get_user
from app.utils.formatting import SEP, SEP2

router = Router()

HELP_AR = (
    f"{SEP}\n"
    f"❓ *دليل الاستخدام*\n"
    f"{SEP}\n\n"
    f"💼 *فرصة اليوم*\n"
    f"{SEP2}\n"
    f"اعرض أحدث المشاريع المتاحة الآن مع إمكانية فتحها أو كتابة عرض.\n\n"
    f"🧭 *الفئات*\n"
    f"{SEP2}\n"
    f"اختر مجالاتك المهنية وابدأ المراقبة المستمرة — سيصلك كل مشروع جديد فور نشره.\n\n"
    f"⭐ *المفضلة*\n"
    f"{SEP2}\n"
    f"استعرض المشاريع التي حفظتها سابقاً وافتحها في أي وقت.\n\n"
    f"👥 *دعوة الأصدقاء*\n"
    f"{SEP2}\n"
    f"شارك رابط إحالتك الشخصي واكسب مكافآت عند انضمامهم.\n\n"
    f"📞 *تواصل معنا*\n"
    f"{SEP2}\n"
    f"الدعم الفوري عبر واتساب، تيليجرام، إنستغرام، ماسنجر، أو إيميل.\n\n"
    f"💎 *الاشتراك*\n"
    f"{SEP2}\n"
    f"بعد انتهاء فترة التجربة، فعّل اشتراكك عبر Binance Pay أو صرافة كريمي.\n\n"
    f"📡 *قنواتنا*\n"
    f"{SEP2}\n"
    f"تابعنا على واتساب وتيليجرام لأحدث الفرص والتحديثات.\n\n"
    f"⚙️ *الإعدادات*\n"
    f"{SEP2}\n"
    f"تغيير لغة الواجهة بين العربية والإنجليزية.\n"
    f"{SEP}\n\n"
    f"📩 *للدعم المباشر:* استخدم زر تواصل معنا"
)

HELP_EN = (
    f"{SEP}\n"
    f"❓ *User Guide*\n"
    f"{SEP}\n\n"
    f"💼 *Today's Job*\n"
    f"{SEP2}\n"
    f"Browse the latest available projects with options to open them or write a proposal.\n\n"
    f"🧭 *Categories*\n"
    f"{SEP2}\n"
    f"Choose your professional fields and start continuous monitoring — every new project reaches you instantly.\n\n"
    f"⭐ *Favorites*\n"
    f"{SEP2}\n"
    f"Browse previously saved projects and open them anytime.\n\n"
    f"👥 *Invite Friends*\n"
    f"{SEP2}\n"
    f"Share your personal referral link and earn rewards when they join.\n\n"
    f"📞 *Contact Us*\n"
    f"{SEP2}\n"
    f"Instant support via WhatsApp, Telegram, Instagram, Messenger, or Email.\n\n"
    f"💎 *Subscription*\n"
    f"{SEP2}\n"
    f"After the trial period, activate your subscription via Binance Pay or Karimi Exchange.\n\n"
    f"📡 *Our Channels*\n"
    f"{SEP2}\n"
    f"Follow us on WhatsApp and Telegram for the latest opportunities and updates.\n\n"
    f"⚙️ *Settings*\n"
    f"{SEP2}\n"
    f"Switch the interface language between Arabic and English.\n"
    f"{SEP}\n\n"
    f"📩 *Direct Support:* Use the Contact Us button"
)


def help_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == "ar":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📞 تواصل معنا", callback_data="page_contact")],
            [InlineKeyboardButton(text="💎 الاشتراك",   callback_data="page_subscribe")],
            [InlineKeyboardButton(text="🔙 رجوع",       callback_data="back_home")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📞 Contact Us",  callback_data="page_contact")],
            [InlineKeyboardButton(text="💎 Subscribe",   callback_data="page_subscribe")],
            [InlineKeyboardButton(text="🔙 Back",        callback_data="back_home")],
        ])


@router.callback_query(F.data == "page_help")
async def page_help(call: CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ar")
    text = HELP_AR if lang == "ar" else HELP_EN
    await call.message.edit_text(text, reply_markup=help_keyboard(lang), parse_mode="Markdown")
    await call.answer()
