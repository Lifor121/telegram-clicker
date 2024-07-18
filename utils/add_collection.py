import asyncio

from db.models import Collection, Skin
from datetime import datetime


async def init():
    collection = await Collection.create(id=1, name='test', type='event', description='хуй', price_craft=100,
                                         active_from=datetime(2024, 7, 1, 0, 0),
                                         active_to=datetime(2024, 7, 31, 23, 59),
                                         folder_name="dev")

    skin1 = await Skin.create(
        name="dev",
        description="dev",
        collection=collection,
        photo="dev.png",
        chance=0.4
    )


if __name__ == '__main__':
    asyncio.run(init())
