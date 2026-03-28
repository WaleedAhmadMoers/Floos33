from django.urls import re_path

from core import consumers

websocket_urlpatterns = [
    re_path(r"^ws/deal/(?P<deal_id>\d+)/$", consumers.DealConsumer.as_asgi()),
    re_path(r"^ws/inquiry/(?P<inquiry_id>\d+)/$", consumers.InquiryConsumer.as_asgi()),
    re_path(r"^ws/rfq-conversation/(?P<conversation_id>\d+)/$", consumers.RFQConversationConsumer.as_asgi()),
]
