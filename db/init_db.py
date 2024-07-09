from tortoise import Tortoise
import os


async def init_db():
    await Tortoise.init(
        db_url=os.getenv('DB_URL'),
        modules={"models": ["db.models"]}
    )
    await Tortoise.generate_schemas()
