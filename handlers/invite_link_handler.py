from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from db.models import User, InviteLink
from filters.admin_filter import AdminFilter


async def cmd_invite(message: Message):
    user = await User.get_or_none(message.from_user.id, message.from_user.username)
    invite_code = "INVITE_" + str(user.id)
    await InviteLink.create(user=user, code=invite_code)
    await message.answer(f"Ваша пригласительная ссылка: https://t.me/milkisclickerbot?start={invite_code}")


async def cmd_click(message: Message):
    if message.get_args():
        invite_code = message.get_args()
        invite_link = await InviteLink.get_or_none(code=invite_code)

        if invite_link:
            inviter = await User.get(id=invite_link.user.id)
            inviter.clicks += 1
            await inviter.save()

            user = await User.get_or_create(message.from_user.id, message.from_user.username)

            await message.answer(f"Вы успешно перешли по ссылке! Пользователь {inviter.username} получил 1 клик.")
        else:
            await message.answer("Неверная пригласительная ссылка.")
    else:
        await message.answer("Используйте команду с кодом ссылки.")


def register_handlers_invite_link(dp: Dispatcher):
    dp.message.register(cmd_invite, Command('invite'), AdminFilter())
    dp.message.register(cmd_click, Command('click'), AdminFilter())