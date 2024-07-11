from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from db.models import User, Skin, Inventory
from filters.admin_filter import AdminFilter


async def admin_handler(message: Message):
    await message.answer('Вы админ')


async def add_item_handler(message: Message):
    command_parts = message.text.split()
    if len(command_parts) != 3:
        await message.answer("Неправильный формат команды. Используйте /hack skin_id кол")
        return
    item_id = command_parts[1]
    quantity = command_parts[2]
    if not item_id.isnumeric() or not quantity.isnumeric():
        await message.answer("Неправильный формат команды. Используйте /hack skin_id(число) кол(число)")
        return
    user = await User.get(id=message.from_user.id)
    skin = await Skin.get(item_id=int(item_id))
    inventory_item, created = await Inventory.get_or_create(
        user=user,
        skin=skin,
        defaults={'quantity': int(quantity)}
    )
    if not created:
        await inventory_item.update_quantity(inventory_item.quantity + int(quantity))
    await message.answer(f'Предмет с id {item_id} в количестве {quantity} добавлен в инвентарь')


def register_handlers_admin(dp: Dispatcher):
    dp.message.register(admin_handler, Command('admin'), AdminFilter())
    dp.message.register(add_item_handler, Command('hack'), AdminFilter())