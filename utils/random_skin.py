import random

from db.models import Collection


async def random_skin(collection: Collection):
    skins = await collection.skins
    total_chance = sum(skin.chance for skin in skins)
    random_value = random.uniform(0, total_chance)
    cumulative_chance = 0.0
    selected_skin = None

    for skin in skins:
        cumulative_chance += skin.chance
        if random_value <= cumulative_chance:
            selected_skin = skin
            break
    return selected_skin