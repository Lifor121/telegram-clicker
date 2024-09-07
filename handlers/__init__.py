from aiogram.dispatcher import dispatcher
from .start_handler import register_handlers_start
from .clicker_handler import register_handlers_click
from .leaderboard_handler import register_handlers_leaderboard
from .profile_handler import register_handlers_profile
from .admin_handler import register_handlers_admin
from .craft_handler import register_handlers_craft
from .inventory_handler import register_handlers_inventory
from .support_handler import register_handlers_support
from .new_inventory import register_handlers_new_inventory

def register_handlers(dp: dispatcher):
    register_handlers_start(dp)
    register_handlers_click(dp)
    register_handlers_leaderboard(dp)
    register_handlers_profile(dp)
    register_handlers_admin(dp)
    register_handlers_craft(dp)
    register_handlers_inventory(dp)
    register_handlers_support(dp)
    register_handlers_new_inventory(dp)

