from aiogram import Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery
from db.models import User

#хуита не работает ыыы данные не обновляются

async def settings(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Конфиденциальность",
        callback_data='privacy'
    )
    builder.row()
    builder.button(
        text="Уведомления",
        callback_data='notifications'
    )
    await message.answer(
        text="Настройки",
        reply_markup=builder.as_markup()
    )


async def privacy(callback_query: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отображение инвентаря",
        callback_data='inventory_display'
    )
    builder.row()
    builder.button(
        text="Отображение завершённых коллекций",
        callback_data='collections_display'
    )
    await callback_query.message.edit_text(
        text="Конфиденциальность",
        reply_markup=builder.as_markup()
    )


async def notifications(callback_query: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Уведомления о продаже",
        callback_data='sale_notifications'
    )
    builder.row()
    builder.button(
        text="Уведомление о вознаграждении (авторам)",
        callback_data='reward_notifications'
    )
    await callback_query.message.edit_text(
        text="Уведомления",
        reply_markup=builder.as_markup()
    )


async def inventory_display(callback_query: CallbackQuery, state: FSMContext):
    user = await User.get(id=callback_query.from_user.id)
    user.inventory_display = not user.inventory_display
    user.save()
    print(user.inventory_display)
    if user.inventory_display:
        await callback_query.message.edit_text("Теперь инвентарь отображается в Вашем профиле")
    else:
        await callback_query.message.edit_text("Инвентарь больше не отображается в Вашем профиле")


async def collections_display(callback_query: CallbackQuery, state: FSMContext):
    user = await User.get(id=callback_query.from_user.id)
    user.collections_display = not user.collections_display
    user.save()
    print(user.collections_display)
    if user.collections_display:
        await callback_query.message.edit_text("Теперь коллекции отображается в Вашем профиле")
    else:
        await callback_query.message.edit_text("Коллекции больше не отображается в Вашем профиле")


async def sale_notifications(callback_query: CallbackQuery, state: FSMContext):
    user = await User.get(id=callback_query.from_user.id)
    user.sale_notifications = not user.sale_notifications
    user.save()
    print(user.sale_notifications)
    if user.sale_notifications:
        await callback_query.message.edit_text("Уведомления о продаже были включены")
    else:
        await callback_query.message.edit_text("Уведомления о продаже были отключены")


async def reward_notifications(callback_query: CallbackQuery, state: FSMContext):
    user = await User.get(id=callback_query.from_user.id)
    user.reward_notifications = not user.reward_notifications
    user.save()
    print(user.reward_notifications)
    if user.reward_notifications:
        await callback_query.message.edit_text("Уведомления о вознаграждении были включены")
    else:
        await callback_query.message.edit_text("Уведомления о вознаграждении были отключены")


def register_handlers_settings(dp: Dispatcher):
    dp.message.register(settings, F.text == "Настройки")
    dp.callback_query.register(privacy, F.data == "privacy")
    dp.callback_query.register(notifications, F.data == "notifications")
    dp.callback_query.register(inventory_display, F.data == "inventory_display")
    dp.callback_query.register(collections_display, F.data == "collections_display")
    dp.callback_query.register(sale_notifications, F.data == "sale_notifications")
    dp.callback_query.register(reward_notifications, F.data == "reward_notifications")