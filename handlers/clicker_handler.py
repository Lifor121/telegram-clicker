from aiogram import F, Dispatcher
from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os


async def clicker_handler(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Кликер",
        web_app=WebAppInfo(
            url=os.getenv("WEBAPP_URL")
        )
    )
    await message.answer(text="Кликай по кнопке ниже", reply_markup=builder.as_markup())


def register_handlers_click(dp: Dispatcher):
    dp.message.register(clicker_handler, F.text == "Кликер")