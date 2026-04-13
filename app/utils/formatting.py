SEP  = "━" * 26
SEP2 = "─" * 26
MAX_MSG_LEN = 4000


def _safe_len(text: str, limit: int = MAX_MSG_LEN) -> str:
    return text if len(text) <= limit else text[:limit - 3] + "..."


def format_project(p: dict, lang: str) -> str:
    title     = p.get("title", "—")
    brief     = p.get("brief", "—")
    time_rel  = p.get("time", "—").strip()
    timestamp = p.get("timestamp", "")

    if lang == "ar":
        text = (
            f"{SEP}\n"
            f"🚀 *مشروع جديد*\n"
            f"{SEP}\n\n"
            f"📌 *العنوان:*\n"
            f"{title}\n\n"
            f"{SEP}\n\n"
            f"📝 *الوصف:*\n"
            f"{brief}\n\n"
            f"{SEP}\n"
            f"🕒 {time_rel}   |   📅 {timestamp}"
        )
    else:
        text = (
            f"{SEP}\n"
            f"🚀 *New Project*\n"
            f"{SEP}\n\n"
            f"📌 *Title:*\n"
            f"{title}\n\n"
            f"{SEP}\n\n"
            f"📝 *Description:*\n"
            f"{brief}\n\n"
            f"{SEP}\n"
            f"🕒 {time_rel}   |   📅 {timestamp}"
        )

    return _safe_len(text)
