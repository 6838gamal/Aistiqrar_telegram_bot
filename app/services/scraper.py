import requests
from bs4 import BeautifulSoup

SCRAPER_URL = "https://scraper-live-tracker.onrender.com/"


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
            projects.append({
                "title": title,
                "brief": brief,
                "time": time_rel,
                "timestamp": timestamp,
                "link": link,
            })

    return projects
