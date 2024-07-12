from tortoise import fields
from tortoise.models import Model


class Skin(Model):
    item_id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, null=False)
    description = fields.TextField(default='Тут должно быть описание но админам стало лень')
    collection = fields.ForeignKeyField('models.Collection', related_name='skins')
    photo = fields.TextField()


class Collection(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, null=False)
    description = fields.TextField(default='Тут должно быть описание но админам стало лень')
    skins = fields.ReverseRelation['Skin']
