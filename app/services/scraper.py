import re
import requests
from bs4 import BeautifulSoup

SCRAPER_URL = "https://scraper-live-tracker.onrender.com/"

CATEGORY_KEYWORDS = {
    0: [
        "برمج", "تطوير", "كود", "موقع", "تطبيق", "بوت", "سيرفر", "قاعدة بيانات",
        "software", "dev", "web", "app", "flutter", "react", "python", "php",
        "javascript", "typescript", "backend", "frontend", "api", "bot", "wordpress",
        "laravel", "django", "node", "vps", "linux", "docker", "database"
    ],
    1: [
        "تصميم", "شعار", "هوية", "بنر", "واجهة", "جرافيك", "فوتوشوب",
        "design", "logo", "ui", "ux", "graphic", "photoshop", "illustrator",
        "figma", "banner", "brand", "creative"
    ],
    2: [
        "كتاب", "ترجم", "محتوى", "مقال", "نص", "تأليف", "كتابة", "مراجعة",
        "writing", "translation", "content", "blog", "article", "copywriting",
        "proofreading", "script", "translate"
    ],
    3: [
        "تسويق", "إعلان", "سوشيال", "ميديا", "متابعين", "مبيعات", "حملة",
        "marketing", "ads", "social", "media", "seo", "sales", "campaign",
        "facebook", "instagram", "tiktok", "google ads"
    ],
    4: [
        "فيديو", "مونتاج", "صوت", "تسجيل", "مقطع", "انيميشن", "موشن",
        "video", "audio", "editing", "animation", "motion", "voice", "podcast",
        "youtube", "reel"
    ],
    5: [
        "أعمال", "استشار", "خطة", "إدارة", "مشروع", "دراسة جدوى",
        "business", "consulting", "management", "plan", "strategy", "feasibility"
    ],
    6: [
        "دعم", "خدمة", "إدخال بيانات", "بحث", "رفع", "أرشفة",
        "support", "service", "data entry", "research", "virtual assistant", "admin"
    ],
    7: [
        "ذكاء اصطناعي", "تعلم آلي", "نموذج", "بيانات", "تحليل", "llm", "nlp",
        "ai", "machine learning", "deep learning", "data", "model", "gpt",
        "chatbot", "rag", "vector", "automation", "scraping"
    ],
    8: [
        "منزل", "إنتاجية", "تنظيم", "حياة", "صحة", "تعليم",
        "productivity", "lifestyle", "home", "education", "health", "personal"
    ],
}


def fetch_projects() -> list[dict]:
    try:
        r = requests.get(SCRAPER_URL, timeout=15)
        r.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(r.text, "lxml")
    cards = soup.select("div.card[data-title]")

    projects = []
    for card in cards:
        title = card.get("data-title", "").strip()
        brief = card.get("data-brief", "").strip()
        time_rel = card.get("data-time", "").strip()
        timestamp = card.get("data-timestamp", "").strip()
        link = card.get("data-link", "").strip()

        if title and link:
            match = re.search(r'/project/(\d+)', link)
            project_id = match.group(1) if match else ""
            projects.append({
                "id": project_id,
                "title": title,
                "brief": brief,
                "time": time_rel,
                "timestamp": timestamp,
                "link": link,
            })

    return projects


def filter_by_categories(projects: list[dict], category_indices: list[int]) -> list[dict]:
    if not category_indices or not projects:
        return projects

    matched = []
    seen_links = set()

    for project in projects:
        text = (project.get("title", "") + " " + project.get("brief", "")).lower()
        for cat_idx in category_indices:
            keywords = CATEGORY_KEYWORDS.get(cat_idx, [])
            if any(kw.lower() in text for kw in keywords):
                if project["link"] not in seen_links:
                    seen_links.add(project["link"])
                    matched.append(project)
                break

    return matched
