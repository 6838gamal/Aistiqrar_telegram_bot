import os
import asyncio
from fastapi import FastAPI
import uvicorn

from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.bot.routers import main_router

app = FastAPI()

@app.on_event("startup")
async def startup():
    dp.include_router(main_router)
    asyncio.create_task(dp.start_polling(bot))

@app.get("/")
def root():
    return {"status": "running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "run:app",
        host="0.0.0.0",   # 🔥 مهم جدًا
        port=port,
        reload=False
    )
