SEP  = "━" * 26
SEP2 = "─" * 26
MAX_MSG_LEN = 4000


def _safe_len(text: str, limit: int = MAX_MSG_LEN) -> str:
    return text if len(text) <= limit else text[:limit - 3] + "..."


def format_project(p: dict, lang: str, match: dict = None) -> str:
    title     = p.get("title", "—")
    brief     = p.get("brief", "—")
    time_rel  = p.get("time", p.get("time_rel", "—")).strip()
    timestamp = p.get("timestamp", p.get("posted_at", ""))
    platform  = p.get("platform", "")

    PLATFORM_LABELS = {
        "mostaql":    "🟢 مستقل",
        "tafdhali":   "🔵 تفذلي",
        "kofeel":     "🟣 كفيل",
        "pph":        "🟠 PPH",
        "freelancer": "🔴 Freelancer",
    }
    platform_label = PLATFORM_LABELS.get(platform, "")

    if lang == "ar":
        platform_line = f"🌐 *المنصة:* {platform_label}\n" if platform_label else ""
        text = (
            f"{SEP}\n"
            f"🚀 *مشروع جديد*\n"
            f"{SEP}\n\n"
            f"{platform_line}"
            f"📌 *العنوان:*\n"
            f"{title}\n\n"
            f"{SEP2}\n\n"
            f"📝 *الوصف:*\n"
            f"{brief}\n\n"
            f"{SEP}\n"
            f"🕒 {time_rel}   |   📅 {timestamp}"
        )
    else:
        platform_line = f"🌐 *Platform:* {platform_label}\n" if platform_label else ""
        text = (
            f"{SEP}\n"
            f"🚀 *New Project*\n"
            f"{SEP}\n\n"
            f"{platform_line}"
            f"📌 *Title:*\n"
            f"{title}\n\n"
            f"{SEP2}\n\n"
            f"📝 *Description:*\n"
            f"{brief}\n\n"
            f"{SEP}\n"
            f"🕒 {time_rel}   |   📅 {timestamp}"
        )

    # Append match block if provided
    if match:
        from app.utils.matching import format_match_block
        text += format_match_block(match, lang)

    return _safe_len(text)
