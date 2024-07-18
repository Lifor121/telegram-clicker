from tortoise import fields
from tortoise.models import Model


class Skin(Model):
    item_id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, null=False)
    description = fields.TextField(default='Тут должно быть описание но админам стало лень')
    collection = fields.ForeignKeyField('models.Collection', related_name='skins')
    photo = fields.TextField()
    chance = fields.FloatField(null=False, default=0)


class Collection(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, null=False)
    type = fields.CharField(default='permanent', max_length=20, null=False) # permanent, seasonal, event
    description = fields.TextField(default='Тут должно быть описание но админам стало лень')
    skins = fields.ReverseRelation['Skin']
    price_craft = fields.IntField()
    active_from = fields.DatetimeField(null=True)
    active_to = fields.DatetimeField(null=True)
    folder_name = fields.TextField()
