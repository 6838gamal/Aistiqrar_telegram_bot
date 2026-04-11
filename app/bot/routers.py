from aiogram import Router

from app.bot.handlers.start import router as start_router
from app.bot.handlers.work import router as work_router
from app.bot.handlers.job import router as job_router
from app.bot.handlers.menu import router as menu_router

main_router = Router()

main_router.include_router(start_router)
main_router.include_router(work_router)
main_router.include_router(job_router)
main_router.include_router(menu_router)
