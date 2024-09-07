from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from db.models import User, Skin
from filters.admin_filter import AdminFilter
from utils.inventory import add_skin_to_inventory, get_user_inventory


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
    
    for _ in range(int(quantity)):
        await add_skin_to_inventory(user, skin)
    
    await message.answer(f'Предмет с id {item_id} добавлен в инвентарь в количестве {quantity}')

    # Показать обновленный инвентарь
    inventory = await get_user_inventory(user.id)
    inventory_text = f"Обновленный инвентарь пользователя {inventory['username']}:\n"
    for item in inventory['inventory']:
        inventory_text += f"{item['skin_name']} из коллекции {item['collection_name']} - {item['count']} шт.\n"
    
    await message.answer(inventory_text)


def register_handlers_admin(dp: Dispatcher):
    dp.message.register(admin_handler, Command('admin'), AdminFilter())
    dp.message.register(add_item_handler, Command('hack'), AdminFilter())