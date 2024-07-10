from tortoise import fields
from tortoise.models import Model


class Skin(Model):
    item_id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, null=False)
    description = fields.TextField(default='Тут должно быть описание но админам стало лень')
    collection_id = fields.IntField(default=0)
    photo = fields.TextField()
