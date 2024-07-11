from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, null=False)
    clicks = fields.IntField(default=0)
    role = fields.CharField(default='user', max_length=50)
    avatar = fields.CharField(max_length=255, null=True)
    inventory_items = fields.ReverseRelation['Inventory']


class Inventory(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='inventory_items')
    skin = fields.ForeignKeyField('models.Skin', related_name='inventory_items')
    quantity = fields.IntField(default=1)

    async def update_quantity(self, new_quantity):
        if new_quantity <= 0:
            await self.delete()
        else:
            self.quantity = new_quantity
            await self.save()
