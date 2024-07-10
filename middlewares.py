from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Any

from db.models import User


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any]
    ) -> Any:
        if not event.from_user.username:
            return await event.answer(
                "Your username is not set. Please set it in your Telegram settings."
            )
        photos = await event.from_user.get_profile_photos()
        user, created = await User.get_or_create(
            id=event.from_user.id, 
            username=event.from_user.username,
            defaults={"avatar": photos.photos[0][0].file_id} 
        )
        if not created:
            user = await User.get(id=event.from_user.id)
        data["user"] = user
        return await handler(event, data)