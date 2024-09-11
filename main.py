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
from handlers import register_handlers, invite_link_handler, start_handler

dotenv.load_dotenv()


async def lifespan(app: FastAPI):
    await init_db()
    await bot.set_webhook(
        url=f"{os.getenv('WEBAPP_URL')}/webhook",
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )
    yield
    await Tortoise.close_connections()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(os.getenv('BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.message.middleware(UserMiddleware())
register_handlers(dp)
invite_link_handler.register_handlers_invite_link(dp)
start_handler.register_handlers_start(dp)
app = FastAPI(lifespan=lifespan)
setup_routes(app, bot, dp)


if __name__ == "__main__":
    logger.info("Starting the bot...")
    uvicorn.run(app)