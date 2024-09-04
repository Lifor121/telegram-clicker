from db.models import User, Skin, Inventory

async def add_skin_to_inventory(user: User, skin: Skin):
    """
    Добавляет скин в инвентарь пользователя.
    Если скин уже есть в инвентаре, увеличивает его количество.
    
    :param user: Объект пользователя
    :param skin: Объект скина
    """
    # Проверяем, есть ли уже такой скин в инвентаре пользователя
    inventory_item = await Inventory.get_or_none(user=user, skin=skin)
    
    if inventory_item:
        # Если скин уже есть, увеличиваем количество
        inventory_item.quantity += 1
        await inventory_item.save()
    else:
        # Если скина нет, создаем новую запись в инвентаре
        await Inventory.create(user=user, skin=skin, quantity=1)