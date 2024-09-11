from tortoise import fields
from tortoise.models import Model
from .user import User


class InviteLink(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="invite_links")
    code = fields.CharField(max_length=20, unique=True)  # Увеличил длину до 20
    uses = fields.IntField(default=0)
    max_uses = fields.IntField(default=3)

    class Meta:
        table = "invite_links"