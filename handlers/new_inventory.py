from aiogram import Dispatcher, F
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from db.models import User, InventoryItem, Skin
from aiogram.types import BufferedInputFile


async def generate_inventory_image(user: User):
    # Получаем все предметы инвентаря пользователя
    inventory_items = await InventoryItem.filter(user=user).prefetch_related('skin__collection')
    
    # Создаем новое изображение
    width, height = 830, 600  # Уменьшаем высоту, так как 3 ряда занимают меньше места
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("./db/fonts/PixelifySans.ttf", 20)
    
    # Рисуем заголовок
    draw.text((10, 10), f"Инвентарь пользователя {user.username}", fill='black', font=font)
    
    # Размеры и отступы для ячеек
    cell_size = 150
    padding = 10
    start_x, start_y = 10, 50
    
    for i in range(15):
        row = i // 5
        col = i % 5
        x = start_x + col * (cell_size + padding)
        y = start_y + row * (cell_size + padding)
        
        # Рисуем ячейку
        draw.rectangle([x, y, x + cell_size, y + cell_size], outline='black', width=2)
        
        # Рисуем номер ячейки
        draw.text((x + 5, y + 5), str(i + 1), fill='black', font=font)
        
        if i < len(inventory_items):
            item = inventory_items[i]
            skin = item.skin
            # Загружаем изображение скина с прозрачным фоном
            skin_image = Image.open(f"./db/skins/{skin.collection.folder_name}/{skin.photo}").convert("RGBA")
            skin_image = skin_image.resize((cell_size - 20, cell_size - 20))
            
            # Создаем новое изображение с белым фоном
            cell_image = Image.new('RGBA', (cell_size - 20, cell_size - 20), (255, 255, 255, 0))
            # Накладываем изображение скина на белый фон
            cell_image.paste(skin_image, (0, 0), skin_image)
            
            # Вставляем изображение скина в ячейку
            image.paste(cell_image, (x + 10, y + 30), cell_image)
    
    # Сохраняем изображение в байтовый поток
    temp_file = BytesIO()
    image.save(temp_file, format='PNG')
    temp_file.seek(0)
    
    return temp_file


async def new_inventory_handler(message: Message):
    user = await User.get(id=message.from_user.id)
    inventory_image = await generate_inventory_image(user)
    await message.answer_photo(photo=BufferedInputFile(
                inventory_image.read(),
                filename="buffer img.jpg"
            ), caption="Ваш инвентарь", reply_markup=create_number_keyboard())


def register_handlers_new_inventory(dp: Dispatcher):
    dp.message.register(new_inventory_handler, F.text == "Inventory")



def create_number_keyboard():
    keyboard = []
    for i in range(0, 15, 5):
        row = [InlineKeyboardButton(text=str(j+1), callback_data=f"number_{j+1}") for j in range(i, i+5)]
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)