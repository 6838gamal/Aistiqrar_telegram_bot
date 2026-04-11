import os
import asyncio
from fastapi import FastAPI
import uvicorn

from app.bot.bot import bot
from app.bot.dispatcher import dp

# 🔥 مهم: استيراد نظام المينيو الجديد
from app.bot.handlers.main_menu import setup_menu_routers

app = FastAPI()

# =========================
# 🚀 تشغيل البوت عند بدء السيرفر
# =========================
@app.on_event("startup")
async def startup():
    # 🔥 تسجيل جميع صفحات المينيو
    setup_menu_routers(dp)

    # 🚀 تشغيل البوت
    asyncio.create_task(dp.start_polling(bot))


# =========================
# 🌐 endpoint للتأكد أن السيرفر شغال
# =========================
@app.get("/")
def root():
    return {"status": "running"}


# =========================
# 🔥 تشغيل uvicorn
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
