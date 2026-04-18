def normalize(text: str):
    return text.strip().lower()

COMMANDS = {
    "job":        ["job", "فرصة", "وظيفة", "💼"],
    "profile":    ["profile", "ملفي", "📁"],
    "categories": ["categories", "فئات", "🧭"],
    "suggest":    ["suggest", "suggestion", "اقتراح", "💡"],
    "invite":     ["invite", "دعوة", "👥"],
    "help":       ["help", "مساعدة", "❓"],
    "channels":   ["channels", "قنواتنا", "📡"],
    "settings":   ["settings", "إعدادات", "⚙️"],
    "back":       ["back", "رجوع", "🔙"],
    "favorites":  ["favorites", "المفضلة", "مفضلة", "⭐"],
    "about":      ["about", "عن المطور", "عنا", "👤"],
    "contact":    ["contact", "تواصل", "تواصل معنا", "📞"],
    "subscribe":  ["subscribe", "اشترك", "اشتراك", "💎"],
}

def match_command(text: str):
    if not text:
        return None
    text = normalize(text)
    for key, values in COMMANDS.items():
        for value in values:
            if value in text:
                return key
    return None
