import asyncio

import dotenv

from db.models import Collection, Skin
from datetime import datetime
from db.init_db import init_db


dotenv.load_dotenv()
async def init():
    await init_db()
    collection = await Collection.create(id=1, name='dev', type='permanent', description='dev', price_craft=100,
                                         folder_name="dev")

    skin1 = await Skin.create(
        name="dev",
        description="dev",
        collection=collection,
        photo="dev.png",
        chance="B"
    )



if __name__ == '__main__':
    asyncio.run(init())