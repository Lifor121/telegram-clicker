from aiogram import F, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.active_collections import get_active_collections
from db.models import Collection, User
from utils.random_skin import random_skin, get_skin_rarity_info
from utils.inventory import add_skin_to_inventory

async def craft_handler(message: Message):
    collections = await get_active_collections()
    builder = InlineKeyboardBuilder()
    for collection in collections:
        builder.button(
            text=f'{collection.type} {collection.name} - {collection.price_craft} clicks',
            callback_data=f"collection_{collection.id}"
        )

    await message.answer(text="Крафт", reply_markup=builder.as_markup())


async def collection_callback_handler(callback_query: CallbackQuery):
    collection_id = int(callback_query.data.split('_')[1])
    collection = await Collection.get(id=collection_id)
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Скрафтить - {collection.price_craft} clicks',
                   callback_data=f"craft_collection_{collection.id}")
    builder.button(text=f'Отмена',
                   callback_data=f"cancel_collection")
    await callback_query.message.edit_text(
        text=f"Коллекцию {collection.name}.\nОписание: {collection.description}\nЦена: {collection.price_craft} кликов.",
        reply_markup=builder.as_markup()
    )
    await callback_query.answer()


async def craft_callback_cancel_handler(callback_query: CallbackQuery):
    collections = await get_active_collections()
    builder = InlineKeyboardBuilder()
    for collection in collections:
        builder.button(
            text=f'{collection.type} {collection.name} - {collection.price_craft} clicks',
            callback_data=f"collection_{collection.id}"
        )

    await callback_query.message.edit_text(text="Крафт", reply_markup=builder.as_markup())


async def craft_collection_callback_handler(callback_query: CallbackQuery):
    user = await User.get(id=callback_query.from_user.id)
    collection_id = int(callback_query.data.split('_')[2])
    collection = await Collection.get(id=collection_id)
    
    if user.clicks >= collection.price_craft:
        # Обновляем только поле clicks
        await User.filter(id=user.id).update(clicks=user.clicks - collection.price_craft)
        
        selected_skin = await random_skin(collection)
        print(selected_skin, collection.id, collection.name)
        if selected_skin:
            rarity_info = await get_skin_rarity_info(selected_skin)
            await add_skin_to_inventory(user, selected_skin)
            await callback_query.answer(
                text=f"Вы успешно скрафтили {selected_skin.name} ({rarity_info['display']}) "
                     f"из коллекции {collection.name}! Шанс: {rarity_info['chance']*100}%"
            )
        else:
            await callback_query.answer(text="Произошла ошибка при крафте. Попробуйте снова.")
    else:
        await callback_query.answer(text="Недостаточно кликов для крафта.")

def register_handlers_craft(dp: Dispatcher):
    dp.message.register(craft_handler, F.text == "Крафт")
    dp.callback_query.register(collection_callback_handler, F.data.startswith('collection_'))
    dp.callback_query.register(craft_callback_cancel_handler, F.data.startswith('cancel_collection'))
    dp.callback_query.register(craft_collection_callback_handler, F.data.startswith('craft_collection_'))