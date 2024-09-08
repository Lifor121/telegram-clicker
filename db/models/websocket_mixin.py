from tortoise import fields
from tortoise.models import Model

class WebSocketMixin:
    _websocket = None

    @property
    def websocket(self):
        return self._websocket

    @websocket.setter
    def websocket(self, value):
        self._websocket = value