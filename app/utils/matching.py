"""
Match score calculator:
Compares user profile skills/specialization against a project's title+brief.
Returns a dict with score, matched/missing skills, and acceptance advice.
"""
from __future__ import annotations


def _progress_bar(pct: int) -> str:
    filled = round(pct / 10)
    return "█" * filled + "░" * (10 - filled)


def _parse_skills(skills_str: str) -> list[str]:
    if not skills_str:
        return []
    return [s.strip().lower() for s in skills_str.replace("،", ",").split(",") if s.strip()]


def calc_match(profile: dict, project: dict) -> dict:
    """
    Returns:
    {
        score:          int   (0-100),
        matched:        list[str],
        missing:        list[str],
        advice:         list[str],   (tips for this specific project)
        acceptance:     str,
        bar:            str,
        profile_score:  int   (profile completeness bonus),
    }
    """
    title  = (project.get("title", "") or "").lower()
    brief  = (project.get("brief",  "") or "").lower()
    text   = title + " " + brief

    # ── 1. Skills match ──────────────────────────────────────────────
    specialization = (profile.get("specialization", "") or "").lower()
    skills_str     = profile.get("skills", "") or ""
    user_skills    = _parse_skills(skills_str)
    if specialization:
        user_skills = list({specialization} | set(user_skills))

    matched = [s for s in user_skills if s in text]
    missing = [s for s in user_skills if s not in text]

    skill_score = int(len(matched) / len(user_skills) * 70) if user_skills else 35

    # ── 2. Profile completeness bonus ────────────────────────────────
    profile_bonus = 0
    advice = []

    has_portfolio = bool(profile.get("portfolio_link", "").strip())
    has_rate      = bool(profile.get("hourly_rate",    "").strip())
    has_exp       = bool(profile.get("experience_years", "").strip())

    if has_portfolio:
        profile_bonus += 15
    else:
        advice.append("أضف رابط محفظة أعمالك لرفع فرص القبول" if True else "Add portfolio link")

    if has_rate:
        profile_bonus += 10
    else:
        advice.append("حدد سعرك لتبدو أكثر احترافية")

    if has_exp:
        profile_bonus += 5

    score = min(100, skill_score + profile_bonus)

    # ── 3. Project-specific advice ───────────────────────────────────
    if missing:
        short_missing = [m.title() for m in missing[:3]]
        advice.insert(0, f"لا تملك: {', '.join(short_missing)} — قد تحتاجها")

    # ── 4. Acceptance label ──────────────────────────────────────────
    if score >= 75:
        acceptance = "عالية جداً ✅"
    elif score >= 50:
        acceptance = "متوسطة ⚡"
    elif score >= 30:
        acceptance = "منخفضة ⚠️"
    else:
        acceptance = "بعيدة عن التخصص ❌"

    return {
        "score":         score,
        "matched":       [m.title() for m in matched[:5]],
        "missing":       [m.title() for m in missing[:3]],
        "advice":        advice[:2],
        "acceptance":    acceptance,
        "bar":           _progress_bar(score),
        "profile_bonus": profile_bonus,
    }


def format_match_block(match: dict, lang: str) -> str:
    SEP2 = "─" * 26
    score = match["score"]
    bar   = match["bar"]

    if lang == "ar":
        lines = [
            f"\n{SEP2}\n",
            f"📊 *تحليل التوافق مع ملفك:*\n",
            f"🎯 نسبة التوافق: *{score}%*  {bar}\n",
        ]
        if match["matched"]:
            lines.append(f"✅ مهارات مطابقة: {', '.join(match['matched'])}\n")
        if match["missing"]:
            lines.append(f"⚠️ مهارات ناقصة: {', '.join(match['missing'])}\n")
        lines.append(f"💡 فرصة القبول: *{match['acceptance']}*\n")
        for tip in match["advice"][:1]:
            lines.append(f"📌 {tip}\n")
    else:
        lines = [
            f"\n{SEP2}\n",
            f"📊 *Profile Match Analysis:*\n",
            f"🎯 Match Score: *{score}%*  {bar}\n",
        ]
        if match["matched"]:
            lines.append(f"✅ Matched Skills: {', '.join(match['matched'])}\n")
        if match["missing"]:
            lines.append(f"⚠️ Missing Skills: {', '.join(match['missing'])}\n")
        lines.append(f"💡 Acceptance Chance: *{match['acceptance']}*\n")
        for tip in match["advice"][:1]:
            lines.append(f"📌 {tip}\n")

    return "".join(lines)
