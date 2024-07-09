from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup


async def start_handler(message: Message):
    kb = [[
        KeyboardButton(text="Профиль"),
        KeyboardButton(text="Таблица лидеров"),
        KeyboardButton(text="Кликер"),
    ], ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Приветик :3")
    await message.answer(f"Добро пожаловать в Milkis Clicker!\n"
                         f"Кликай как чёрт, соревнуйся с другими игроками в количестве кликов", reply_markup=keyboard)


def register_handlers_start(dp: Dispatcher):
    dp.message.register(start_handler, CommandStart())