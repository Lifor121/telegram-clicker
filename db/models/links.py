from tortoise import fields
from tortoise.models import Model
from .user import User


class InviteLink(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User", related_name="invite_links")
    code = fields.CharField(max_length=10, unique=True)

    class Meta:
        table = "invite_links"