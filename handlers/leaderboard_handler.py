from aiogram import F, Dispatcher
from aiogram.types import Message
from db.models import User


async def leaderboard_handler(message: Message):
    lb = await User.all().order_by('-clicks').limit(10)
    res = ['Никнейм - клики']
    for i in range(len(lb)):
        res.append(f'{i + 1}. @{lb[i].username} - {lb[i].clicks}')
    await message.answer('\n'.join(res))


def register_handlers_leaderboard(dp: Dispatcher):
    dp.message.register(leaderboard_handler, F.text == "Таблица лидеров")