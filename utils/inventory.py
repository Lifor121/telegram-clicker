from db.models import User, Skin, InventoryItem
from tortoise.functions import Count
import logging

logger = logging.getLogger(__name__)
async def add_skin_to_inventory(user: User, skin: Skin):
    """
    Добавляет скин в инвентарь пользователя.
    
    :param user: Объект пользователя
    :param skin: Объект скина
    """
    # Проверяем, есть ли уже такой скин в инвентаре пользователя
    try:
        logger.info(f"Попытка добавить скин {skin.item_id} пользователю {user.id}")
        
        # Проверяем, существует ли пользователь и скин
        user = await User.get(id=user.id)
        skin = await Skin.get(item_id=skin.item_id)
        
        logger.info(f"Пользователь и скин найдены. Создаем InventoryItem")
        
        # Создаем новый объект InventoryItem
        inventory_item = await InventoryItem.create(user=user, skin=skin)
        
        logger.info(f"InventoryItem успешно создан с id {inventory_item.id}")
        
        return inventory_item
    except Exception as e:
        logger.error(f"Неожиданная ошибка при добавлении скина в инвентарь: {str(e)}")
    
    return None


async def get_user_inventory(user_id: int):
    user = await User.get(id=user_id).prefetch_related(
        'inventory_items__skin__collection',
        'inventory_items__market_listing'
    )
    
    inventory_items = await InventoryItem.filter(user=user).annotate(
        count=Count('id')
    ).prefetch_related('skin__collection')
    
    inventory_data = []
    for item in inventory_items:
        inventory_data.append({
            'skin_name': item.skin.name,
            'collection_name': item.skin.collection.name,
            'count': item.count,
            'is_on_sale': item.is_on_sale
        })
    
    return {
        'username': user.username,
        'total_items': len(inventory_items),
        'inventory': inventory_data
    }