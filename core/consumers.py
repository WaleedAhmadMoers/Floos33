import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from core.models import DealTrigger, DealHistory
from inquiries.models import Inquiry
from rfqs.models import RFQConversation, RFQMessage
from core.utils.verification import is_verified


class BaseAuthConsumer(AsyncJsonWebsocketConsumer):
    """Base consumer that checks user is authenticated."""

    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        await super().connect()


class DealConsumer(BaseAuthConsumer):
    async def connect(self):
        await super().connect()
        self.deal_id = self.scope["url_route"]["kwargs"]["deal_id"]
        if not await self._allowed():
            await self.close()
            return
        self.group_name = f"deal_{self.deal_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get("type") == "typing":
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "deal.typing", "user": self.scope["user"].email},
            )

    async def deal_typing(self, event):
        await self.send_json({"event": "typing", "user": event["user"]})

    async def deal_update(self, event):
        await self.send_json({"event": "deal_update", "payload": event["payload"]})

    @database_sync_to_async
    def _allowed(self):
        try:
            deal = DealTrigger.objects.select_related("buyer", "seller_user").get(pk=self.deal_id)
        except DealTrigger.DoesNotExist:
            return False
        user = self.scope["user"]
        if not is_verified(user):
            return False
        return user.is_staff or user == deal.buyer or user == deal.seller_user


class InquiryConsumer(BaseAuthConsumer):
    async def connect(self):
        await super().connect()
        self.inquiry_id = self.scope["url_route"]["kwargs"]["inquiry_id"]
        if not await self._allowed():
            await self.close()
            return
        self.group_name = f"inquiry_{self.inquiry_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get("type") == "typing":
            await self.channel_layer.group_send(
                self.group_name, {"type": "thread.typing", "user": self.scope["user"].email}
            )

    async def thread_typing(self, event):
        await self.send_json({"event": "typing", "user": event["user"]})

    async def message_created(self, event):
        await self.send_json({"event": "message_created", "payload": event["payload"]})

    async def deal_update(self, event):
        await self.send_json({"event": "deal_update", "payload": event["payload"]})

    @database_sync_to_async
    def _allowed(self):
        try:
            inquiry = Inquiry.objects.select_related("buyer", "seller_company__owner").get(pk=self.inquiry_id)
        except Inquiry.DoesNotExist:
            return False
        user = self.scope["user"]
        if not is_verified(user):
            return False
        return user.is_staff or user == inquiry.buyer or user == inquiry.seller_company.owner


class RFQConversationConsumer(BaseAuthConsumer):
    async def connect(self):
        await super().connect()
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        if not await self._allowed():
            await self.close()
            return
        self.group_name = f"rfqconv_{self.conversation_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get("type") == "typing":
            await self.channel_layer.group_send(
                self.group_name, {"type": "thread.typing", "user": self.scope["user"].email}
            )

    async def thread_typing(self, event):
        await self.send_json({"event": "typing", "user": event["user"]})

    async def message_created(self, event):
        await self.send_json({"event": "message_created", "payload": event["payload"]})

    async def deal_update(self, event):
        await self.send_json({"event": "deal_update", "payload": event["payload"]})

    @database_sync_to_async
    def _allowed(self):
        try:
            convo = RFQConversation.objects.select_related("buyer", "seller_user").get(pk=self.conversation_id)
        except RFQConversation.DoesNotExist:
            return False
        user = self.scope["user"]
        if not is_verified(user):
            return False
        return user.is_staff or user == convo.buyer or user == convo.seller_user
