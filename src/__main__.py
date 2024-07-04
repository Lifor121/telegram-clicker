import os
import uvicorn
import dotenv

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.types import Message, WebAppInfo, Update
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.bot import DefaultBotProperties
from aiogram.client.default import DefaultBotProperties

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from typing import Callable, Awaitable, Any
from tortoise import Tortoise
from models import User

dotenv.load_dotenv()

class UserMiddleware(BaseMiddleware):
    async def __call__(
        self, 
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]], 
        event: Message, 
        data: dict[str, Any]
    ) -> Any:
        if not event.from_user.username: 
            return await event.answer(
                "Your username is not set. Please set it in your Telegram settings."
            ) 
        user = await User.get_or_create(id=event.from_user.id, username=event.from_user.username)
        data["user"] = user[0]
        return await handler(event, data)

async def lifespan(app: FastAPI):
    await bot.set_webhook(
        url=f"{os.getenv('WEBAPP_URL')}/webhook",
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
        )
    
    await Tortoise.init(
        db_url=os.getenv("DB_URL"),
        modules={"models": ["models"]}
    )

    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

bot = Bot(os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.message.middleware(UserMiddleware())

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory=r".\src\web\templates")
app.mount("/static", StaticFiles(directory=r".\src\web\static"), name="static")

def webapp_builder() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Click It!",
        web_app=WebAppInfo(
            url=os.getenv("WEBAPP_URL")
        )
    )
    return builder.as_markup()

@dp.message(CommandStart())
async def start(message: Message, user: User):
    clicks_stats = f"Колличество Ваших кликов: {user.clicks}" if user.clicks else None

    markup = None
    if not clicks_stats:
        markup = (
            InlineKeyboardBuilder()
            .button(
                text="Click It!",
                web_app=WebAppInfo(
                    url=os.getenv("WEBAPP_URL")
                )
            )
        ).as_markup()
    
    await message.answer(
        text=f"Привет, {message.from_user.first_name}!{clicks_stats}",
        reply_markup=markup
    )

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/click")
async def click(request: Request, data: dict):
    print(data)
    user = await User.filter(id=data["id"]).first()
    user.clicks += 1
    await user.save()

@app.post("/webhook")
async def webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)

if __name__ == "__main__":
    uvicorn.run(app)