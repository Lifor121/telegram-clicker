from aiogram import Dispatcher, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


class NameStates(StatesGroup):
    waiting_nick_or_id = State()


async def user_search_handler(message: Message, state: FSMContext) -> None:
    kb = [[KeyboardButton(text="Отмена")]]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb, 
        resize_keyboard=True,
        input_field_placeholder="Username или telegram id"
    )
    await message.answer('Введите имя или id', reply_markup=keyboard)
    await state.set_state(NameStates.waiting_nick_or_id)


def register_handlers_user_search(dp: Dispatcher):
    dp.message.register(user_search_handler, F.text == 'Поиск')