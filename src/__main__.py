import os
import uvicorn
import dotenv

from aiogram import Bot, Dispatcher, BaseMiddleware, F
from aiogram.types import Message, WebAppInfo, Update, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.bot import DefaultBotProperties
from aiogram.client.default import DefaultBotProperties

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

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
templates = Jinja2Templates(directory=os.getenv('DIR_TEMP'))
app.mount("/static", StaticFiles(directory=os.getenv('DIR_STAT')))


@dp.message(CommandStart())
async def start(message: Message):
    kb = [[
        KeyboardButton(text="Профиль"),
        KeyboardButton(text="Таблица лидеров"),
        KeyboardButton(text="Кликер"),
    ], ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Приветик :3")
    await message.answer(f"Добро пожаловать в Milkis Clicker!\n"
                         f"Кликай как чёрт, соревнуйся с другими игроками в колличестве кликов", reply_markup=keyboard)


@dp.message(F.text == "Профиль")
async def profile(message: Message, user: User):
    lb = await User.all().order_by('-clicks')
    for i in range(len(lb)):
        if lb[i].id == user.id:
            break
    await message.answer(f"Информация об игроке {user.username}:\n"
                         f"Колличество кликов: {user.clicks}\n"
                         f"Место в рейтинге: {i + 1}")


@dp.message(F.text == "Таблица лидеров")
async def leaderboard(message: Message):
    lb = await User.all().order_by('-clicks').limit(10)
    res = ['Никнейм - клики']
    for i in range(len(lb)):
        res.append(f'{i + 1}. @{lb[i].username} - {lb[i].clicks}')
    await message.answer('\n'.join(res))


@dp.message(F.text == "Кликер")
async def clicker(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Кликер",
        web_app=WebAppInfo(
            url=os.getenv("WEBAPP_URL")
        )
    )
    await message.answer(text="Кликай по кнопке ниже", reply_markup=builder.as_markup())


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/click")
async def click(request: Request, data: dict):
    user = await User.filter(id=data["id"]).first()
    user.clicks += 1
    await user.save()


@app.get("/get_clicks")
async def get_clicks(id: int):
    user = await User.filter(id=id).first()
    print(user.clicks)
    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)
    return JSONResponse({"clicks": user.clicks})


@app.post("/webhook")
async def webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)


if __name__ == "__main__":
    uvicorn.run(app)
