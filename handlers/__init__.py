from aiogram.dispatcher import dispatcher
from .start_handler import register_handlers_start
from .clicker_handler import register_handlers_click
from .leaderboard_handler import register_handlers_leaderboard
from .profile_handler import register_handlers_profile
from .user_handler import register_handlers_user
from .user_search_handler import register_handlers_user_search
from .cancel_user_search_handler import register_handlers_cancel_user_search
from .admin_handler import register_handlers_admin


def register_handlers(dp: dispatcher):
    register_handlers_start(dp)
    register_handlers_click(dp)
    register_handlers_leaderboard(dp)
    register_handlers_profile(dp)
    register_handlers_user(dp)
    register_handlers_user_search(dp)
    register_handlers_cancel_user_search(dp)
    register_handlers_admin(dp)
