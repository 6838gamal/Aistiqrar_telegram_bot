import asyncio
from fastapi import FastAPI
import uvicorn

from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.bot.routers import main_router

app = FastAPI()

dp.include_router(main_router)

@app.on_event("startup")
async def startup():
    asyncio.create_task(dp.start_polling(bot))

@app.get("/")
def root():
    return {"status": "running"}

if __name__ == "__main__":
    uvicorn.run("run:app", port=8000, reload=False)
