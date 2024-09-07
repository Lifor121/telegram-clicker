from aiogram import Dispatcher, F
from aiogram.types import Message

async def support_handler(message: Message):
    await message.answer(f"Служба поддержки @Lifor121")


def register_handlers_support(dp: Dispatcher):
    dp.message.register(support_handler, F.text == "Support")

