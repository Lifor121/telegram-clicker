from db.models import User, Skin, InventoryItem
from tortoise.functions import Count

async def add_skin_to_inventory(user: User, skin: Skin):
    """
    Добавляет скин в инвентарь пользователя.
    Если скин уже есть в инвентаре, увеличивает его количество.
    
    :param user: Объект пользователя
    :param skin: Объект скина
    """
    # Проверяем, есть ли уже такой скин в инвентаре пользователя
    inventory_item = await InventoryItem.create(user=user, skin=skin)


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
            'is_on_sale': item.is_on_sale,
            'market_price': item.market_listing.price if item.market_listing else None
        })
    
    return {
        'username': user.username,
        'total_items': len(inventory_items),
        'inventory': inventory_data
    }