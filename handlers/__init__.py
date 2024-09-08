from aiogram.dispatcher import dispatcher
from .start_handler import register_handlers_start
from .clicker_handler import register_handlers_click
from .leaderboard_handler import register_handlers_leaderboard
from .profile_handler import register_handlers_profile
from .admin_handler import register_handlers_admin
from .craft_handler import register_handlers_craft
from .inventory_handler import register_handlers_inventory
from .settings_handler import register_handlers_settings
from .search_handler import register_handlers_search
from .invite_link_handler import register_handlers_invite_link
from .support_handler import register_handlers_support
from .new_inventory import register_handlers_new_inventory
from .invite_link_handler import register_handlers_invite_link

def register_handlers(dp: dispatcher):
    register_handlers_start(dp)
    register_handlers_click(dp)
    register_handlers_leaderboard(dp)
    register_handlers_profile(dp)
    register_handlers_admin(dp)
    register_handlers_craft(dp)
    register_handlers_settings(dp)
    register_handlers_search(dp)
    register_handlers_invite_link(dp)
    register_handlers_support(dp)
    register_handlers_new_inventory(dp)
    register_handlers_invite_link(dp)