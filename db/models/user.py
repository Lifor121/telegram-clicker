from tortoise import fields
from tortoise.models import Model
import uuid
from .websocket_mixin import WebSocketMixin


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, null=True)  # Изменил на null=True
    clicks = fields.IntField(default=0)
    role = fields.CharField(default='user', max_length=50)
    avatar = fields.CharField(max_length=255, null=True)
    inventory_items = fields.ReverseRelation['InventoryItem']
    inventory_display = fields.BooleanField(default=True)
    collections_display = fields.BooleanField(default=True)
    sale_notifications = fields.BooleanField(default=True)
    reward_notifications = fields.BooleanField(default=True)
    equipped_skin = fields.ForeignKeyField('models.Skin', related_name='equipped_users', null=True)
    market_listings = fields.ReverseRelation['MarketListing']

    class Meta:
        table = "user"  


class InventoryItem(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField('models.User', related_name='inventory_items')
    skin = fields.ForeignKeyField('models.Skin', related_name='inventory_items')
    acquired_at = fields.DatetimeField(auto_now_add=True)
    is_on_sale = fields.BooleanField(default=False)


class MarketListing(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    seller = fields.ForeignKeyField('models.User', related_name='market_listings')
    inventory_item = fields.OneToOneField('models.InventoryItem', related_name='market_listing')
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    listed_at = fields.DatetimeField(auto_now_add=True)
    status = fields.CharField(max_length=20, default='active')  # active, sold, cancelled
