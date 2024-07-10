from tortoise.functions import Lower

from aiogram import F, Dispatcher
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from db.models import User


class NameStates(StatesGroup):
    waiting_nick_or_id = State()


async def user_handler(message: Message, state: FSMContext) -> None:
    if message.text.startswith('@'):
        user = await User.annotate(name=Lower('username')).filter(name=message.text[1:].lower()).get_or_none()
    elif message.text.isnumeric():
        user = await User.get_or_none(telegram_id=int(message.text))
    else:
        user = await User.annotate(name=Lower('username')).filter(name=message.text.lower()).get_or_none()

    kb = [[
        KeyboardButton(text="Меню"),
        KeyboardButton(text="Поиск")
    ]]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Приветик :3"
    )

    if user:
        lb = await User.all().order_by('-clicks')
        for i in range(len(lb)):
            if lb[i].id == user.id:
                break
        if user.avatar:
            await message.answer_photo(
                photo=user.avatar,
                caption=f"Информация об игроке @{user.username}:\n"
                        f"Количество кликов: {user.clicks}\n"
                        f"Место в рейтинге: {i + 1}",
                reply_markup=keyboard
            )
        else:
            await message.answer(
                f"Информация об игроке @{user.username}:\n"
                f"Количество кликов: {user.clicks}\n"
                f"Место в рейтинге: {i + 1}",
                reply_markup=keyboard
            )
    else:
        await message.answer('Пользователь не найден', reply_markup=keyboard)

    await state.clear()


def register_handlers_user(dp: Dispatcher):
    dp.message.register(user_handler, NameStates.waiting_nick_or_id, F.text != 'Отмена')
