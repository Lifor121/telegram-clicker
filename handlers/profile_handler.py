from aiogram import F, Dispatcher
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from db.models import User


async def profile_handler(message: Message, user: User):
    kb = [[KeyboardButton(text="Меню")]]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb, 
        resize_keyboard=True, 
        input_field_placeholder="Вау магия"
    )

    lb = await User.all().order_by('-clicks')
    for i in range(len(lb)):
        if lb[i].id == user.id:
            break
    await message.answer_photo(
        photo=user.avatar, 
        caption=f"Информация об игроке @{user.username}:\n"
                f"Количество кликов: {user.clicks}\n"
                f"Место в рейтинге: {i + 1}",
        reply_markup=keyboard
    )


def register_handlers_profile(dp: Dispatcher):
    dp.message.register(profile_handler, F.text == "Профиль")