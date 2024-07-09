from aiogram import F, Dispatcher
from aiogram.types import Message
from db.models import User


async def profile_handler(message: Message, user: User):
    lb = await User.all().order_by('-clicks')
    for i in range(len(lb)):
        if lb[i].id == user.id:
            break
    await message.answer(f"Информация об игроке {user.username}:\n"
                         f"Количество кликов: {user.clicks}\n"
                         f"Место в рейтинге: {i + 1}")


def register_handlers_profile(dp: Dispatcher):
    dp.message.register(profile_handler, F.text == "Профиль")
