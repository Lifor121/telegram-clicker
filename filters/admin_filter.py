from aiogram.types import Message
from aiogram.filters import BaseFilter
from db.models import User


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = await User.filter(id=message.from_user.id).first()
        if user and user.role == 'admin':
            return True
        else:
            return False
