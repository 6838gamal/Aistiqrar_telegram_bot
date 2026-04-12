def normalize(text: str):
    return text.strip().lower()

COMMANDS = {
    "job": ["job", "فرصة", "وظيفة", "💼"],
    "profile": ["profile", "ملفي", "📁"],
    "categories": ["categories", "فئات", "🧭"],
    "suggest": ["suggest", "اقتراح", "💡"],
    "invite": ["invite", "دعوة", "👥"],
    "help": ["help", "مساعدة", "❓"],
}

def match_command(text: str):
    text = normalize(text)

    for key, values in COMMANDS.items():
        for value in values:
            if value in text:
                return key

    return None
