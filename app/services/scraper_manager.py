"""
Scraper Manager — runs all platform scrapers on a schedule,
stores results in PostgreSQL, and keeps per-platform stats.
"""
import asyncio
import logging
from datetime import datetime
from app.services.scrapers import ALL_SCRAPERS
from app.database.projects_db import upsert_projects, get_stats_per_platform

logger = logging.getLogger(__name__)

INTERVAL_SECONDS = 120   # run all scrapers every 2 minutes

_running = False


def run_all_scrapers() -> dict:
    """
    Run every scraper synchronously, store results in PostgreSQL.
    Returns a summary: {platform: {"fetched": n, "new": m}}
    """
    summary = {}
    for scraper in ALL_SCRAPERS:
        platform = scraper.platform
        try:
            projects = scraper.scrape()
            new_count = upsert_projects(projects)
            summary[platform] = {"fetched": len(projects), "new": new_count}
            if projects:
                logger.info(
                    "[%s] fetched=%d  new=%d",
                    platform, len(projects), new_count
                )
            else:
                logger.warning("[%s] returned 0 projects", platform)
        except Exception as exc:
            logger.error("[%s] scraper error: %s", platform, exc)
            summary[platform] = {"fetched": 0, "new": 0, "error": str(exc)}
    return summary


async def scraper_loop():
    """Async background loop — runs forever, calling run_all_scrapers() each cycle."""
    global _running
    if _running:
        return
    _running = True
    logger.info("Scraper manager started — interval=%ds", INTERVAL_SECONDS)

    while True:
        try:
            loop = asyncio.get_event_loop()
            summary = await loop.run_in_executor(None, run_all_scrapers)
            total_new = sum(v.get("new", 0) for v in summary.values())
            logger.info("Scrape cycle complete — total_new=%d | %s",
                        total_new, summary)
        except Exception as exc:
            logger.error("Scraper loop error: %s", exc)

        await asyncio.sleep(INTERVAL_SECONDS)
