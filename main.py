import logging
import os
import uvicorn
import dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from fastapi import FastAPI
from tortoise import Tortoise

from middlewares import UserMiddleware
from db.init_db import init_db
from web.routes import setup_routes
from handlers import register_handlers

dotenv.load_dotenv()


async def lifespan(app: FastAPI):
    await bot.set_webhook(
        url=f"{os.getenv('WEBAPP_URL')}/webhook",
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )
    await init_db()
    yield
    await Tortoise.close_connections()

logging.basicConfig(level=logging.INFO)

bot = Bot(os.getenv('BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.message.middleware(UserMiddleware())
register_handlers(dp)
app = FastAPI(lifespan=lifespan)
setup_routes(app, bot, dp)


if __name__ == "__main__":
    uvicorn.run(app)