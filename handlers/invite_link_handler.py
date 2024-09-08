from aiogram import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from db.models import User, InviteLink
from filters.admin_filter import AdminFilter


async def cmd_invite(message: Message):
    user, _ = await User.get_or_create(id=message.from_user.id, defaults={"username": message.from_user.username})
    
    # Проверяем, есть ли у пользователя активная пригласительная ссылка
    existing_link = await InviteLink.filter(user=user, uses__lt=3).first()
    
    if existing_link:
        invite_code = existing_link.code
    else:
        invite_code = f"INVITE_{user.id}"
        await InviteLink.create(user=user, code=invite_code)
    
    await message.answer(f"Ваша пригласительная ссылка: https://t.me/milkisclickerbot?start={invite_code}\n"
                         f"Вы можете пригласить еще {3 - (existing_link.uses if existing_link else 0)} игроков.")


async def cmd_start_with_args(message: Message):
    args = message.get_args()
    if args.startswith("INVITE_"):
        await process_invite(message, args)
    else:
        # Если аргументы есть, но это не приглашение, передаем управление обычному обработчику start
        await message.answer("Добро пожаловать! Используйте /invite, чтобы получить пригласительную ссылку.")


async def process_invite(message: Message, invite_code: str):
    invite_link = await InviteLink.get_or_none(code=invite_code)

    if invite_link and invite_link.uses < invite_link.max_uses:
        inviter = await User.get(id=invite_link.user_id)
        inviter.clicks += 1
        await inviter.save()

        user, created = await User.get_or_create(id=message.from_user.id, defaults={"username": message.from_user.username})

        if created or not await InviteLink.filter(user=user).exists():
            invite_link.uses += 1
            await invite_link.save()
            await message.answer(f"Вы успешно перешли по ссылке! Пользователь {inviter.username} получил 1 клик.")
        else:
            await message.answer("Вы уже использовали пригласительную ссылку ранее.")
    elif invite_link and invite_link.uses >= invite_link.max_uses:
        await message.answer("Эта пригласительная ссылка уже достигла максимального количества использований.")
    else:
        await message.answer("Неверная пригласительная ссылка.")


def register_handlers_invite_link(dp: Dispatcher):
    dp.message.register(cmd_invite, Command('invite'))
    dp.message.register(cmd_start_with_args, CommandStart(deep_link=True))