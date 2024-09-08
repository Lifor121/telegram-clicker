from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.models import User, Skin, Collection
from filters.admin_filter import AdminFilter
from utils.inventory import add_skin_to_inventory, get_user_inventory

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminStates(StatesGroup):
    choosing_action = State()
    adding_collection = State()
    adding_collection_type = State()
    adding_collection_description = State()
    adding_collection_price = State()
    adding_collection_folder = State()
    choosing_collection = State()
    adding_skin_name = State()
    adding_skin_description = State()
    adding_skin_photo = State()
    adding_skin_chance = State()
    editing_collection = State()
    editing_collection_name = State()
    editing_collection_type = State()
    editing_collection_description = State()
    editing_collection_price = State()
    editing_skin = State()
    editing_skin_name = State()
    editing_skin_description = State()
    editing_skin_photo = State()
    editing_skin_chance = State()

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

async def admin_menu(message: types.Message, state: FSMContext):
    logger.info("Вызвана функция admin_menu")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить коллекцию", callback_data="add_collection")],
        [InlineKeyboardButton(text="Добавить скин", callback_data="add_skin")],
        [InlineKeyboardButton(text="Редактировать коллекцию", callback_data="edit_collection")],
        [InlineKeyboardButton(text="Редактировать скин", callback_data="edit_skin")],
        [InlineKeyboardButton(text="Просмотреть все коллекции", callback_data="view_collections")]
    ])
    await message.answer("Выберите действие:", reply_markup=keyboard)
    await state.set_state(AdminStates.choosing_action)

async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"Вызвана функция process_callback с данными: {callback_query.data}")
    action = callback_query.data
    if action == "add_collection":
        await callback_query.message.answer("Введите название новой коллекции:")
        await state.set_state(AdminStates.adding_collection)
    elif action == "add_skin":
        collections = await Collection.all()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=c.name, callback_data=f"collection_{c.id}")] for c in collections
        ])
        await callback_query.message.answer("Выберите коллекцию для нового скина:", reply_markup=keyboard)
        await state.set_state(AdminStates.choosing_collection)
    elif action == "edit_collection":
        await show_collections_for_edit(callback_query, state)
    elif action == "edit_skin":
        await show_collections_for_skin_edit(callback_query, state)
    elif action == "view_collections":
        collections = await Collection.all().prefetch_related('skins')
        for collection in collections:
            skins = [f"- {skin.name}" for skin in collection.skins]
            skins_text = "\n".join(skins) if skins else "Нет скинов"
            await callback_query.message.answer(
                f"Коллекция: {collection.name}\n"
                f"Тип: {collection.type}\n"
                f"Описание: {collection.description}\n"
                f"Цена крафта: {collection.price_craft}\n"
                f"Скины:\n{skins_text}"
            )
    await callback_query.answer()

async def show_collections_for_edit(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info("show_collections_for_edit вызван")
    collections = await Collection.all()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=c.name, callback_data=f"edit_collection_{c.id}")] for c in collections
    ])
    await callback_query.message.answer("Выберите коллекцию для редактирования:", reply_markup=keyboard)

async def edit_collection(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"edit_collection вызван с данными: {callback_query.data}")
    collection_id = int(callback_query.data.split('_')[2])
    collection = await Collection.get(id=collection_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить название", callback_data=f"edit_collection_name_{collection_id}")],
        [InlineKeyboardButton(text="Изменить тип", callback_data=f"edit_collection_type_{collection_id}")],
        [InlineKeyboardButton(text="Изменить описание", callback_data=f"edit_collection_description_{collection_id}")],
        [InlineKeyboardButton(text="Изменить цену крафта", callback_data=f"edit_collection_price_{collection_id}")]
    ])
    
    await callback_query.message.answer(f"Выберите, что хотите изменить в коллекции '{collection.name}':", reply_markup=keyboard)
    await callback_query.answer()
    await state.update_data(editing_collection_id=collection_id)

async def edit_collection_field(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"edit_collection_field вызван с данными: {callback_query.data}")
    parts = callback_query.data.split('_')
    field = parts[2]
    collection_id = int(parts[3])
    await state.update_data(editing_collection_id=collection_id, editing_field=field)
    
    if field == "name":
        await state.set_state(AdminStates.editing_collection_name)
        await callback_query.message.answer("Введите новое название коллекции:")
    elif field == "type":
        await state.set_state(AdminStates.editing_collection_type)
        await callback_query.message.answer("Введите новый тип коллекции (permanent, seasonal, event):")
    elif field == "description":
        await state.set_state(AdminStates.editing_collection_description)
        await callback_query.message.answer("Введите новое описание коллекции:")
    elif field == "price":
        await state.set_state(AdminStates.editing_collection_price)
        await callback_query.message.answer("Введите новую цену крафта:")
    
    await callback_query.answer()

async def add_collection(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите тип коллекции (permanent, seasonal, event):")
    await state.set_state(AdminStates.adding_collection_type)

async def add_collection_type(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['permanent', 'seasonal', 'event']:
        await message.answer("Неверный тип. Пожалуйста, выберите из: permanent, seasonal, event")
        return
    await state.update_data(type=message.text.lower())
    await message.answer("Введите описание коллекции:")
    await state.set_state(AdminStates.adding_collection_description)

async def add_collection_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите цену крафта:")
    await state.set_state(AdminStates.adding_collection_price)

async def add_collection_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число для цены крафта.")
        return
    await state.update_data(price_craft=int(message.text))
    await message.answer("Введите имя папки для скинов:")
    await state.set_state(AdminStates.adding_collection_folder)

async def finish_adding_collection(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data['folder_name'] = message.text
    new_collection = await Collection.create(**data)
    await message.answer(f"Коллекция '{new_collection.name}' успешно добавлена!")
    await state.clear()

async def choose_collection_for_skin(callback_query: types.CallbackQuery, state: FSMContext):
    collection_id = int(callback_query.data.split('_')[1])
    await state.update_data(collection_id=collection_id)
    await callback_query.message.answer("Введите название нового скина:")
    await state.set_state(AdminStates.adding_skin_name)
    await callback_query.answer()

async def add_skin_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание скина:")
    await state.set_state(AdminStates.adding_skin_description)

async def add_skin_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите имя файла фото скина:")
    await state.set_state(AdminStates.adding_skin_photo)

async def add_skin_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.text)
    await message.answer("Введите шанс выпадения скина (например, B - 80%):")
    await state.set_state(AdminStates.adding_skin_chance)

async def finish_adding_skin(message: types.Message, state: FSMContext):
    await state.update_data(chance=message.text)
    data = await state.get_data()
    collection = await Collection.get(id=data['collection_id'])
    new_skin = await Skin.create(collection=collection, **data)
    await message.answer(f"Скин '{new_skin.name}' успешно добавлен в коллекцию '{collection.name}'!")
    await state.clear()

async def save_edited_collection(message: types.Message, state: FSMContext):
    data = await state.get_data()
    collection_id = data['editing_collection_id']
    field = data['editing_field']
    
    collection = await Collection.get(id=collection_id)
    
    if field == "name":
        collection.name = message.text
    elif field == "type":
        if message.text.lower() not in ['permanent', 'seasonal', 'event']:
            await message.answer("Неверный тип. Пожалуйста, выберите из: permanent, seasonal, event")
            return
        collection.type = message.text.lower()
    elif field == "description":
        collection.description = message.text
    elif field == "price":
        if not message.text.isdigit():
            await message.answer("Пожалуйста, введите число для цены крафта.")
            return
        collection.price_craft = int(message.text)
    
    await collection.save()
    await message.answer(f"Коллекция успешно обновлена!")
    await state.clear()

async def show_collections_for_skin_edit(callback_query: types.CallbackQuery, state: FSMContext):
    collections = await Collection.all()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=c.name, callback_data=f"edit_skin_collection_{c.id}")] for c in collections
    ])
    await callback_query.message.answer("Выберите коллекцию скина для редактирования:", reply_markup=keyboard)

async def edit_skin_collection(callback_query: types.CallbackQuery, state: FSMContext):
    collection_id = int(callback_query.data.split('_')[3])
    collection = await Collection.get(id=collection_id).prefetch_related('skins')
    
    keyboard = InlineKeyboardBuilder()
    for skin in collection.skins:
        keyboard.button(text=skin.name, callback_data=f"edit_skin_{skin.id}")
    keyboard.adjust(2)
    
    await callback_query.message.answer(f"Выберите скин для редактирования из коллекции '{collection.name}':", reply_markup=keyboard.as_markup())
    await callback_query.answer()

async def edit_skin(callback_query: types.CallbackQuery, state: FSMContext):
    skin_id = int(callback_query.data.split('_')[2])
    skin = await Skin.get(id=skin_id)
    await state.update_data(editing_skin_id=skin_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить название", callback_data=f"edit_skin_name_{skin_id}")],
        [InlineKeyboardButton(text="Изменить описание", callback_data=f"edit_skin_description_{skin_id}")],
        [InlineKeyboardButton(text="Изменить фото", callback_data=f"edit_skin_photo_{skin_id}")],
        [InlineKeyboardButton(text="Изменить шанс выпадения", callback_data=f"edit_skin_chance_{skin_id}")]
    ])
    
    await callback_query.message.answer(f"Выберите, что хотите изменить в скине '{skin.name}':", reply_markup=keyboard)
    await callback_query.answer()

async def edit_skin_field(callback_query: types.CallbackQuery, state: FSMContext):
    field = callback_query.data.split('_')[2]
    await state.update_data(editing_field=field)
    
    if field == "name":
        await state.set_state(AdminStates.editing_skin_name)
        await callback_query.message.answer("Введите новое название скина:")
    elif field == "description":
        await state.set_state(AdminStates.editing_skin_description)
        await callback_query.message.answer("Введите новое описание скина:")
    elif field == "photo":
        await state.set_state(AdminStates.editing_skin_photo)
        await callback_query.message.answer("Введите новое имя файла фото скина:")
    elif field == "chance":
        await state.set_state(AdminStates.editing_skin_chance)
        await callback_query.message.answer("Введите новый шанс выпадения скина (например, B - 80%):")
    
    await callback_query.answer()

async def save_edited_skin(message: types.Message, state: FSMContext):
    data = await state.get_data()
    skin_id = data['editing_skin_id']
    field = data['editing_field']
    
    skin = await Skin.get(id=skin_id)
    
    if field == "name":
        skin.name = message.text
    elif field == "description":
        skin.description = message.text
    elif field == "photo":
        skin.photo = message.text
    elif field == "chance":
        skin.chance = message.text
    
    await skin.save()
    await message.answer(f"Скин успешно обновлен!")
    await state.clear()

def register_handlers_admin(dp: Dispatcher):
    dp.message.register(admin_handler, Command('admin'), AdminFilter())
    dp.message.register(add_item_handler, Command('hack'), AdminFilter())
    dp.message.register(admin_menu, Command('admin_menu'), AdminFilter())
    
    dp.callback_query.register(process_callback, AdminStates.choosing_action)
    
    dp.callback_query.register(edit_collection, F.data.startswith("edit_collection_") & ~F.data.contains("_name_") & ~F.data.contains("_type_") & ~F.data.contains("_description_") & ~F.data.contains("_price_"))
    dp.callback_query.register(edit_collection_field, F.data.startswith("edit_collection_") & (F.data.contains("_name_") | F.data.contains("_type_") | F.data.contains("_description_") | F.data.contains("_price_")))
    
    dp.message.register(save_edited_collection, AdminStates.editing_collection_name)
    dp.message.register(save_edited_collection, AdminStates.editing_collection_type)
    dp.message.register(save_edited_collection, AdminStates.editing_collection_description)
    dp.message.register(save_edited_collection, AdminStates.editing_collection_price)
    
    dp.callback_query.register(edit_skin_collection, F.data.startswith("edit_skin_collection_"))
    dp.callback_query.register(edit_skin, F.data.startswith("edit_skin_"))
    dp.callback_query.register(edit_skin_field, F.data.startswith("edit_skin_name_") | 
                               F.data.startswith("edit_skin_description_") | 
                               F.data.startswith("edit_skin_photo_") | 
                               F.data.startswith("edit_skin_chance_"))
    
    dp.message.register(save_edited_skin, AdminStates.editing_skin_name)
    dp.message.register(save_edited_skin, AdminStates.editing_skin_description)
    dp.message.register(save_edited_skin, AdminStates.editing_skin_photo)
    dp.message.register(save_edited_skin, AdminStates.editing_skin_chance)