import re
from bs4 import BeautifulSoup
from .base import BaseScraper

LIVE_TRACKER_URL = "https://scraper-live-tracker.onrender.com/"
DIRECT_URL       = "https://mostaql.com/projects"


class MostaqlScraper(BaseScraper):
    platform = "mostaql"

    def scrape(self) -> list[dict]:
        projects = self._scrape_live_tracker()
        if projects:
            return projects
        return self._scrape_direct()

    def _scrape_live_tracker(self) -> list[dict]:
        html = self.fetch_html(LIVE_TRACKER_URL)
        if not html:
            return []
        soup = BeautifulSoup(html, "lxml")
        cards = soup.select("div.card[data-title]")
        results = []
        for card in cards:
            title     = card.get("data-title", "").strip()
            brief     = card.get("data-brief", "").strip()
            time_rel  = card.get("data-time", "").strip()
            timestamp = card.get("data-timestamp", "").strip()
            link      = card.get("data-link", "").strip()
            if not title or not link:
                continue
            m = re.search(r'/project/(\d+)', link)
            pid = m.group(1) if m else ""
            results.append(self._make_project(
                project_id=pid,
                title=title,
                brief=brief,
                budget="",
                link=link,
                time_rel=time_rel,
                posted_at=timestamp,
            ))
        return results

    def _scrape_direct(self) -> list[dict]:
        html = self.fetch_html(DIRECT_URL)
        if not html:
            return []
        soup     = BeautifulSoup(html, "lxml")
        results  = []

        for row in soup.select("tr.project_row"):
            a = row.select_one("h3.project-title a") or row.select_one("a.project-title")
            if not a:
                continue
            title  = a.get_text(strip=True)
            link   = a.get("href", "")
            if not link.startswith("http"):
                link = "https://mostaql.com" + link
            brief  = ""
            bd = row.select_one(".project-brief, .project-description, p")
            if bd:
                brief = bd.get_text(strip=True)
            budget = ""
            bud_el = row.select_one(".budget, .project-budget")
            if bud_el:
                budget = bud_el.get_text(strip=True)
            time_el = row.select_one("time, .time-since, .project-time")
            time_rel = time_el.get_text(strip=True) if time_el else ""
            m = re.search(r'/project/(\d+)', link)
            pid = m.group(1) if m else ""
            results.append(self._make_project(
                project_id=pid,
                title=title,
                brief=brief,
                budget=budget,
                link=link,
                time_rel=time_rel,
            ))

        return results
