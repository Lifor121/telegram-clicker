from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, null=False)
    clicks = fields.IntField(default=0)
    avatar = fields.CharField(max_length=255, null=True)
    role = fields.CharField(max_length=50, default="user")