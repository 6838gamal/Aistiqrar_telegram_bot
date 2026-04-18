import re
from bs4 import BeautifulSoup
from .base import BaseScraper

BASE_URL = "https://www.peopleperhour.com"
JOBS_URL = "https://www.peopleperhour.com/freelance-jobs"


class PPHScraper(BaseScraper):
    platform = "pph"

    def scrape(self) -> list[dict]:
        html = self.fetch_html(JOBS_URL)
        if not html:
            html = self.fetch_html(BASE_URL + "/jobs")
        if not html:
            return []
        return self._parse(html)

    def _parse(self, html: str) -> list[dict]:
        soup    = BeautifulSoup(html, "lxml")
        results = []

        selectors = [
            "li.jobcard",
            "div.jobcard",
            "div[class*='JobCard']",
            "article[class*='job']",
            "div[class*='listing']",
            "li[class*='job']",
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
                card.select_one("a[href*='/job/']") or
                card.select_one("a[href*='/hourlies/']")
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
            for sel in ["p.text", ".job-description", "p[class*='desc']", "p"]:
                el = card.select_one(sel)
                if el:
                    brief = el.get_text(strip=True)
                    break

            budget = ""
            for sel in [".budget", ".price", "span[class*='budget']", "span[class*='price']",
                        "div[class*='Budget']"]:
                el = card.select_one(sel)
                if el:
                    budget = el.get_text(strip=True)
                    break

            time_rel = ""
            for sel in ["time", ".posted-time", "span[class*='time']", "span[class*='ago']"]:
                el = card.select_one(sel)
                if el:
                    time_rel = el.get("datetime", "") or el.get_text(strip=True)
                    break

            m   = re.search(r'/job/(\d+)', link)
            pid = m.group(1) if m else re.sub(r'[^a-z0-9]', '', link.split("/")[-1])[:30]

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
