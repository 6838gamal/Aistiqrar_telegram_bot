import requests
from abc import ABC, abstractmethod

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ar,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TIMEOUT = 20


class BaseScraper(ABC):
    platform: str = ""

    def fetch_html(self, url: str, **kwargs) -> str | None:
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, **kwargs)
            r.raise_for_status()
            return r.text
        except Exception:
            return None

    def fetch_json(self, url: str, **kwargs) -> dict | list | None:
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, **kwargs)
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    @abstractmethod
    def scrape(self) -> list[dict]:
        """Returns list of project dicts with keys:
        platform, project_id, title, brief, budget, link, time_rel, posted_at
        """
        ...

    def _make_project(self, *, project_id="", title="", brief="",
                      budget="", link="", time_rel="", posted_at="") -> dict:
        return {
            "platform":   self.platform,
            "project_id": str(project_id),
            "title":      title.strip()[:500],
            "brief":      brief.strip()[:2000],
            "budget":     budget.strip()[:200],
            "link":       link.strip(),
            "time_rel":   time_rel.strip()[:200],
            "posted_at":  posted_at.strip()[:200],
        }
