import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.bot.routers import main_router
from app.bot.handlers.menu import setup_menu_routers
from app.database.db import init_db, get_all_users, get_stats, init_favorites_table
from app.services.scraper import fetch_projects

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
    init_db()
    init_favorites_table()
    setup_menu_routers(dp)
    dp.include_router(main_router)
    asyncio.create_task(dp.start_polling(bot))


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    stats = get_stats()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats
    })


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    users = get_all_users()
    stats = get_stats()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "users": users,
        "stats": stats
    })


@app.get("/projects", response_class=HTMLResponse)
def projects(request: Request):
    data = fetch_projects()
    return templates.TemplateResponse("projects.html", {
        "request": request,
        "projects": data
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
