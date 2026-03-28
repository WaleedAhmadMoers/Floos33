from django.urls import path

from rfqs.views import (
    ConversationDetailView,
    ConversationStartView,
    ConversationDealAcceptView,
    ConversationDealCancelView,
    ConversationDealRejectView,
    MyResponsesListView,
    MyRFQListView,
    RFQCreateView,
    RFQDetailView,
    RFQListView,
    BuyerConversationListView,
)

app_name = "rfqs"

urlpatterns = [
    path("", RFQListView.as_view(), name="list"),
    path("create/", RFQCreateView.as_view(), name="create"),
    path("mine/", MyRFQListView.as_view(), name="my_rfqs"),
    path("conversations/buyer/", BuyerConversationListView.as_view(), name="buyer_conversations"),
    path("conversations/seller/", MyResponsesListView.as_view(), name="seller_conversations"),
    path("<int:pk>/conversation/deal/accept/", ConversationDealAcceptView.as_view(), name="conversation_deal_accept"),
    path("<int:pk>/conversation/deal/reject/", ConversationDealRejectView.as_view(), name="conversation_deal_reject"),
    path("<int:pk>/conversation/deal/cancel/", ConversationDealCancelView.as_view(), name="conversation_deal_cancel"),
    path("<int:pk>/conversation/", ConversationDetailView.as_view(), name="conversation_detail"),
    path("<int:pk>/start/", ConversationStartView.as_view(), name="start_conversation"),
    path("<int:pk>/", RFQDetailView.as_view(), name="detail"),
]
