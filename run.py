import os
import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.bot.routers import main_router
from app.bot.handlers.menu import setup_menu_routers
from app.database.db import init_db, get_all_users, get_stats, init_favorites_table
from app.database.projects_db import init_projects_table, get_latest_projects, get_stats_per_platform
from app.services.scraper import fetch_projects
from app.services.scraper_manager import scraper_loop

logging.basicConfig(level=logging.INFO)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup():
    init_db()
    init_favorites_table()
    init_projects_table()
    setup_menu_routers(dp)
    dp.include_router(main_router)
    asyncio.create_task(dp.start_polling(bot))
    asyncio.create_task(scraper_loop())


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    stats = get_stats()
    platform_stats = get_stats_per_platform()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats,
        "platform_stats": platform_stats,
    })


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    users = get_all_users()
    stats = get_stats()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "users": users,
        "stats": stats,
    })


@app.get("/projects", response_class=HTMLResponse)
def projects_page(request: Request):
    platform = request.query_params.get("platform")
    data = get_latest_projects(platform=platform, limit=50)
    platform_stats = get_stats_per_platform()
    return templates.TemplateResponse("projects.html", {
        "request": request,
        "projects": data,
        "platform_stats": platform_stats,
        "selected_platform": platform or "all",
    })


@app.get("/api/scrape")
async def trigger_scrape():
    """Manual trigger — runs all scrapers once and returns summary."""
    from app.services.scraper_manager import run_all_scrapers
    loop = asyncio.get_event_loop()
    summary = await loop.run_in_executor(None, run_all_scrapers)
    return {"status": "ok", "summary": summary}


@app.get("/api/projects")
def api_projects(platform: str = None, limit: int = 30):
    data = get_latest_projects(platform=platform, limit=limit)
    for row in data:
        if row.get("scraped_at"):
            row["scraped_at"] = str(row["scraped_at"])
    return {"projects": data, "count": len(data)}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("run:app", host="0.0.0.0", port=port, reload=False)
