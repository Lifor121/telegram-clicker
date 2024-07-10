from aiogram import Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from .profile_handler import profile_handler


class NameStates(StatesGroup):
    waiting_nick_or_id = State()


async def cancel_user_search(message: Message, state: FSMContext):
    await state.clear()
    await profile_handler(message)


def register_handlers_cancel_user_search(dp: Dispatcher):
    dp.message.register(cancel_user_search, NameStates.waiting_nick_or_id, F.text == 'Отмена')