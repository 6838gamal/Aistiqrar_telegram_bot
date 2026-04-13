from aiogram import Router

from app.bot.handlers.start import router as start_router
from app.bot.handlers.menu_text import router as menu_router

main_router = Router()

main_router.include_router(start_router)
main_router.include_router(menu_router)
