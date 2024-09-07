import random
from typing import Optional
from db.models import Collection, Skin

RARITY_LEVELS = {
    'B': {'chance': 0.80, 'display': 'B'},
    'A': {'chance': 0.17, 'display': 'A'},
    'S': {'chance': 0.03, 'display': 'S'},
    'SS': {'chance': 0, 'display': 'SS'},
    'C': {'chance': 0, 'display': 'C'}
}

async def random_skin(collection: Collection) -> Optional[Skin]:
    """
    Выбирает случайный скин из коллекции с учетом редкости.
    
    :param collection: Объект коллекции
    :return: Выбранный скин или None, если скин не был выбран
    """
    await collection.fetch_related('skins')
    
    # Группируем скины по редкости
    skins_by_rarity = {rarity: [] for rarity in RARITY_LEVELS.keys()}
    for skin in collection.skins:
        if skin.chance in skins_by_rarity:
            skins_by_rarity[skin.chance].append(skin)
    
    # Удаляем пустые редкости
    available_rarities = [rarity for rarity, skins in skins_by_rarity.items() if skins]
    
    if not available_rarities:
        return None  # Если нет доступных скинов, возвращаем None
    
    # Пересчитываем шансы только для доступных редкостей
    total_chance = sum(RARITY_LEVELS[rarity]['chance'] for rarity in available_rarities)
    adjusted_chances = {rarity: RARITY_LEVELS[rarity]['chance'] / total_chance for rarity in available_rarities}
    
    # Выбираем редкость на основе скорректированных шансов
    rarity = random.choices(
        available_rarities,
        weights=[adjusted_chances[rarity] for rarity in available_rarities],
        k=1
    )[0]
    
    # Выбираем случайный скин из выбранной редкости
    return random.choice(skins_by_rarity[rarity])

async def get_skin_rarity_info(skin: Skin) -> dict:
    """
    Возвращает информацию о редкости скина.
    
    :param skin: Объект скина
    :return: Словарь с информацией о редкости
    """
    return {
        'rarity': skin.chance,
        'display': RARITY_LEVELS[skin.chance]['display'],
        'chance': RARITY_LEVELS[skin.chance]['chance']
    }
