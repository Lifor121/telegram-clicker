import os

from aiogram import F, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, FSInputFile, CallbackQuery, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.models import User, Inventory, Skin
from filters.admin_filter import AdminFilter


class InventoryStates(StatesGroup):
    current_item = State()


async def inventory_handler(message: Message, state: FSMContext):
    user = await User.get(id=message.from_user.id).prefetch_related('inventory_items__skin')
    items = await Inventory.filter(user=user).prefetch_related('skin')
    if not items:
        await message.answer("Инвентарь пуст.")
        return

    await state.update_data(items=items)
    await state.set_state(InventoryStates.current_item)
    await state.update_data(current_item_index=0)

    item = items[0]
    photo = FSInputFile(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db', 'skins', item.skin.photo)))
    builder = InlineKeyboardBuilder()
    builder.button(
        text="<-",
        callback_data='previous_item'
    )
    builder.button(
        text=f"{1}/{len(items)}",
        callback_data='list_index'
    )
    builder.button(
        text="->",
        callback_data='next_item'
    )
    builder.button(
        text="Экипировать",
        callback_data='equip_skin',

    )
    builder.button(
        text="Назад",
        callback_data='back_inventory'
    )
    builder.adjust(3)
    await message.answer_photo(photo,
                               caption=f"Предмет: {item.skin.name}, Количество: {item.quantity}, Описание: {item.skin.description}",
                               reply_markup=builder.as_markup())


async def edit_inventory_item(callback_query: CallbackQuery, items, index):
    item = items[index]
    photo = InputMediaPhoto(
        media=FSInputFile(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db', 'skins',
                                                       item.skin.photo))))
    builder = InlineKeyboardBuilder()
    builder.button(
        text="<-",
        callback_data='previous_item'
    )
    builder.button(
        text=f"{index + 1}/{len(items)}",
        callback_data='current_position'
    )
    builder.button(
        text="->",
        callback_data='next_item'
    )
    builder.button(
        text="Назад",
        callback_data='back_inventory'
    )
    builder.button(
        text="Экипировать",
        callback_data='equip_skin',

    )
    builder.adjust(3)
    await callback_query.message.edit_media(
        media=photo,
        reply_markup=builder.as_markup()
    )
    await callback_query.message.edit_caption(
        caption=f"Предмет: {item.skin.name}, Количество: {item.quantity}, Описание: {item.skin.description}",
        reply_markup=builder.as_markup()
    )


async def inventory_navigation_handler(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items = data.get('items', [])
    current_index = data.get('current_item_index', 0)
    # Крч баг пофиксил костылем но прикол в том что если условно у тебя открыт инвентарь и рестартнуть бота то он уйдет
    # в ошибку из-за того что len(items) == 0 а на 0 делить нельзя. Другой фикс пока не придумал.
    if len(items) == 0:
        await callback_query.answer()
        return
    if callback_query.data == 'previous_item':
        current_index = (current_index - 1) % len(items)
    elif callback_query.data == 'next_item':
        current_index = (current_index + 1) % len(items)

    await state.update_data(current_item_index=current_index)
    await edit_inventory_item(callback_query, items, current_index)
    await callback_query.answer()


def register_handlers_inventory(dp: Dispatcher):
    dp.message.register(inventory_handler, F.text == "Инвентарь")
    dp.callback_query.register(inventory_navigation_handler, F.data.in_(['previous_item', 'next_item']))
