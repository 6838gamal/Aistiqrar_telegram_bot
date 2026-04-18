import re
from .base import BaseScraper

API_URL = (
    "https://www.freelancer.com/api/projects/0.1/projects/active/"
    "?limit=20&sort_field=time_updated&full_description=true"
    "&job_details=true&compact=false"
)

WEB_URL = "https://www.freelancer.com/jobs/"


class FreelancerScraper(BaseScraper):
    platform = "freelancer"

    def scrape(self) -> list[dict]:
        projects = self._scrape_api()
        if projects:
            return projects
        return self._scrape_web()

    def _scrape_api(self) -> list[dict]:
        data = self.fetch_json(API_URL)
        if not data:
            return []

        result_list = []

        try:
            projects = data.get("result", {}).get("projects", [])
        except Exception:
            return []

        for p in projects:
            try:
                pid       = str(p.get("id", ""))
                title     = p.get("title", "").strip()
                brief     = p.get("preview_description", "") or p.get("description", "") or ""
                brief     = brief.strip()[:2000]
                link      = f"https://www.freelancer.com/projects/{p.get('seo_url', pid)}"
                budget    = ""
                b         = p.get("budget", {})
                if b:
                    min_b  = b.get("minimum", "")
                    max_b  = b.get("maximum", "")
                    curr   = p.get("currency", {}).get("sign", "$")
                    if min_b and max_b:
                        budget = f"{curr}{min_b} – {curr}{max_b}"
                    elif min_b:
                        budget = f"{curr}{min_b}+"
                time_updated = p.get("time_updated", 0) or p.get("time_submitted", 0)
                time_rel = ""
                if time_updated:
                    import datetime
                    dt = datetime.datetime.fromtimestamp(time_updated)
                    time_rel = dt.strftime("%Y-%m-%d %H:%M")
                if title and link:
                    result_list.append(self._make_project(
                        project_id=pid,
                        title=title,
                        brief=brief,
                        budget=budget,
                        link=link,
                        time_rel=time_rel,
                    ))
            except Exception:
                continue

        return result_list

    def _scrape_web(self) -> list[dict]:
        from bs4 import BeautifulSoup
        html = self.fetch_html(WEB_URL)
        if not html:
            return []

        soup    = BeautifulSoup(html, "lxml")
        results = []

        selectors = [
            "div.JobSearchCard-item",
            "div[class*='JobSearchCard']",
            "article[class*='project']",
            "li.project-item",
        ]

        cards = []
        for sel in selectors:
            cards = soup.select(sel)
            if cards:
                break

        for card in cards:
            a = (
                card.select_one("a[href*='/projects/']") or
                card.select_one("h2 a") or
                card.select_one("h3 a")
            )
            if not a:
                continue
            title = a.get_text(strip=True)
            link  = a.get("href", "")
            if not link:
                continue
            if not link.startswith("http"):
                link = "https://www.freelancer.com" + link

            brief = ""
            for sel in ["p.JobSearchCard-primary-description", "p[class*='description']", "p"]:
                el = card.select_one(sel)
                if el:
                    brief = el.get_text(strip=True)
                    break

            budget = ""
            for sel in ["span[class*='Budget']", "span[class*='budget']", ".budget"]:
                el = card.select_one(sel)
                if el:
                    budget = el.get_text(strip=True)
                    break

            time_rel = ""
            for sel in ["span[class*='Time']", "time", ".posted-time"]:
                el = card.select_one(sel)
                if el:
                    time_rel = el.get_text(strip=True)
                    break

            m   = re.search(r'/projects/[^/]+/(\d+)', link)
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
