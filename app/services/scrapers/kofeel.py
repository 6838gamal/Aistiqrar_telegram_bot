import re
from bs4 import BeautifulSoup
from .base import BaseScraper

BASE_URL     = "https://kofeel.com"
PROJECTS_URL = "https://kofeel.com/projects"


class KofeelScraper(BaseScraper):
    platform = "kofeel"

    def scrape(self) -> list[dict]:
        for url in [PROJECTS_URL, BASE_URL + "/jobs", BASE_URL]:
            html = self.fetch_html(url)
            if html:
                results = self._parse(html)
                if results:
                    return results
        return []

    def _parse(self, html: str) -> list[dict]:
        soup    = BeautifulSoup(html, "lxml")
        results = []

        selectors = [
            "div.project-item",
            "div.project-card",
            "article.project",
            "li.project",
            "div.card",
            "div[class*='project']",
        ]

        cards = []
        for sel in selectors:
            cards = soup.select(sel)
            if cards:
                break

        for card in cards:
            a = (
                card.select_one("h2 a") or
                card.select_one("h3 a") or
                card.select_one("a.project-title") or
                card.select_one("a[href*='/project']")
            )
            if not a:
                continue
            title = a.get_text(strip=True)
            link  = a.get("href", "")
            if not link:
                continue
            if not link.startswith("http"):
                link = BASE_URL + link

            brief = ""
            for sel in ["p.description", ".brief", "p.project-desc", "p"]:
                el = card.select_one(sel)
                if el:
                    brief = el.get_text(strip=True)
                    break

            budget = ""
            for sel in [".budget", ".price", "span[class*='budget']"]:
                el = card.select_one(sel)
                if el:
                    budget = el.get_text(strip=True)
                    break

            time_rel = ""
            for sel in ["time", ".time", "span[class*='time']"]:
                el = card.select_one(sel)
                if el:
                    time_rel = el.get_text(strip=True)
                    break

            m   = re.search(r'/(?:project|job)[s]?/(\d+)', link)
            pid = m.group(1) if m else ""

            if title and link:
                results.append(self._make_project(
                    project_id=pid,
                    title=title,
                    brief=brief,
                    budget=budget,
                    link=link,
                    time_rel=time_rel,
                ))

        return results
