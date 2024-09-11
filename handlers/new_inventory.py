from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from db.models import User, InventoryItem, Skin
from aiogram.types import BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from web.routes import send_user_data
import logging

logger = logging.getLogger(__name__)

class NewInventoryStates(StatesGroup):
    viewing = State()

async def generate_inventory_image(user: User, current_page: int):
    inventory_items = await InventoryItem.filter(user=user).prefetch_related('skin__collection')
    image = Image.open("./db/images/shop.png")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("./db/fonts/Jersey25-Regular.ttf", 40)

    draw.text((10, 10), f"Inventory of{user.username} {current_page + 1}", fill='white', font=font)

    cell_size = 180
    padding = 20
    start_x, start_y = 10, 130

    items_per_page = 15
    start_index = current_page * items_per_page
    end_index = start_index + items_per_page

    for i in range(15):
        row = i // 5
        col = i % 5
        x = start_x + col * (cell_size + padding)
        y = start_y + row * (cell_size + padding)
        
        item_index = start_index + i
        if item_index < len(inventory_items):
            item = inventory_items[item_index]
            skin = item.skin
            skin_image = Image.open(f"./db/skins/{skin.collection.folder_name}/{skin.photo}").convert("RGBA")
            skin_image = skin_image.resize((cell_size - 20, cell_size - 20))
            cell_image = Image.new('RGBA', (cell_size - 20, cell_size - 20), (255, 255, 255, 0))
            cell_image.paste(skin_image, (0, 0), skin_image)
            image.paste(cell_image, (x + 10, y + 30), cell_image)

    temp_file = BytesIO()
    image.save(temp_file, format='PNG')
    temp_file.seek(0)
    
    return temp_file

async def new_inventory_handler(message: Message, state: FSMContext):
    user = await User.get(id=message.from_user.id)
    inventory_items = await InventoryItem.filter(user=user).prefetch_related('skin__collection')
    
    if not inventory_items:
        await message.answer("Ваш инвентарь пуст.")
        return

    await state.set_state(NewInventoryStates.viewing)
    await state.update_data(current_page=0, items=inventory_items)

    await show_inventory_page(message, state, is_new=True)

async def show_inventory_page(message_or_query, state: FSMContext, is_new=False):
    data = await state.get_data()
    current_page = data['current_page']
    items = data['items']

    user = await User.get(id=message_or_query.from_user.id)
    inventory_image = await generate_inventory_image(user, current_page)
    
    keyboard = create_inventory_keyboard(current_page, len(items))

    if is_new:
        await message_or_query.answer_photo(
            photo=BufferedInputFile(inventory_image.read(), filename="inventory.jpg"),
            caption=f"Страница {current_page + 1}/{(len(items) - 1) // 15 + 1}",
            reply_markup=keyboard
        )
    else:
        await message_or_query.message.edit_media(
            InputMediaPhoto(
                media=BufferedInputFile(inventory_image.read(), filename="inventory.jpg"),
                caption=f"Страница {current_page + 1}/{(len(items) - 1) // 15 + 1}"
            ),
            reply_markup=keyboard
        )

async def inventory_navigation(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        if not data:
            await callback.answer("Инвентарь устарел. Пожалуйста, откройте инвентарь заново.", show_alert=True)
            return
        
        current_page = data.get('current_page', 0)  # Используем .get() с значением по умолчанию
        items = data.get('items', [])
        total_pages = (len(items) - 1) // 15 + 1

        if callback.data == 'prev_page' and current_page > 0:
            current_page -= 1
        elif callback.data == 'next_page' and current_page < total_pages - 1:
            current_page += 1
        elif callback.data.startswith('slot_'):
            slot_number = int(callback.data.split('_')[1]) - 1
            item_index = current_page * 15 + slot_number
            if item_index < len(items):
                await state.update_data(current_item_index=item_index)
                await show_item_details(callback, state, item_index)
                return

        await state.update_data(current_page=current_page)
        await show_inventory_page(callback, state)
    except Exception as e:
        logger.exception(f"Ошибка при навигации по инвентарю: {e}")
        await callback.answer("Произошла ошибка при навигации по инвентарю", show_alert=True)

async def show_item_details(callback: CallbackQuery, state: FSMContext, item_index: int):
    data = await state.get_data()
    items = data['items']
    item = items[item_index]

    user = await User.get(id=callback.from_user.id)
    is_equipped = user.equipped_skin == item.skin

    collection = await item.skin.collection
    photo = InputMediaPhoto(media=BufferedInputFile(
        open(f"./db/skins/{collection.folder_name}/{item.skin.photo}", "rb").read(),
        filename=f"{item.skin.name}.jpg"
    ))

    keyboard = create_item_details_keyboard(item_index, len(items), is_equipped)

    await callback.message.edit_media(
        media=photo,
        reply_markup=keyboard
    )
    await callback.message.edit_caption(
        caption=f"Предмет: {item.skin.name}\n"
                f"Описание: {item.skin.description}\n"
                f"Коллекция: {collection.name}",
        reply_markup=keyboard
    )

def create_inventory_keyboard(current_page: int, total_items: int):
    builder = InlineKeyboardBuilder()
    total_pages = (total_items - 1) // 15 + 1

    for i in range(1, 16):
        builder.button(text=str(i), callback_data=f"slot_{i}")

    builder.adjust(5)

    if current_page > 0:
        builder.button(text="◀️ Назад", callback_data="prev_page")
    if current_page < total_pages - 1:
        builder.button(text="Вперед ▶️", callback_data="next_page")

    builder.adjust(5)
    return builder.as_markup()

def create_item_details_keyboard(current_index: int, total_items: int, is_equipped: bool):
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️", callback_data="prev_item")
    builder.button(text=f"{current_index + 1}/{total_items}", callback_data="item_index")
    builder.button(text="▶️", callback_data="next_item")
    
    if is_equipped:
        builder.button(text="✅ Экипирован", callback_data="equipped")
    else:
        builder.button(text="Экипировать", callback_data="equip_item")
    
    builder.button(text="Назад к инвентарю", callback_data="back_to_inventory")
    builder.adjust(3, 1, 1)
    return builder.as_markup()

async def item_navigation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items = data['items']
    current_index = data.get('current_item_index', 0)

    if callback.data == "prev_item":
        current_index = (current_index - 1) % len(items)
    elif callback.data == "next_item":
        current_index = (current_index + 1) % len(items)
    elif callback.data == "back_to_inventory":
        await show_inventory_page(callback, state)
        return
    elif callback.data == "equip_item":
        await equip_item(callback, state)
        return

    await state.update_data(current_item_index=current_index)
    await show_item_details(callback, state, current_index)

async def back_to_inventory(callback: CallbackQuery, state: FSMContext):
    await show_inventory_page(callback, state)

async def equip_item(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items = data['items']
    current_index = data['current_item_index']
    
    user = await User.get(id=callback.from_user.id)
    user.equipped_skin = items[current_index].skin
    await user.save()
    
    await callback.answer('Скин успешно экипирован!')
    await send_user_data(user)

    await show_item_details(callback, state, current_index)

def register_handlers_new_inventory(dp: Dispatcher):
    dp.message.register(new_inventory_handler, F.text == "Инвентарь")
    dp.callback_query.register(inventory_navigation, F.data.in_(['prev_page', 'next_page']) | F.data.startswith('slot_'))
    dp.callback_query.register(item_navigation, F.data.in_(['prev_item', 'next_item', 'equip_item']))
    dp.callback_query.register(back_to_inventory, F.data == 'back_to_inventory')