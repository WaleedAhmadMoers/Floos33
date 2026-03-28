from django.urls import path

from .views import (
    InquiryCreateView,
    InquiryDetailView,
    ReceivedInquiryListView,
    SentInquiryListView,
    InquiryDealAcceptView,
    InquiryDealCancelView,
)

app_name = "inquiries"

urlpatterns = [
    path("create/<slug:stocklot_slug>/", InquiryCreateView.as_view(), name="create"),
    path("sent/", SentInquiryListView.as_view(), name="sent"),
    path("received/", ReceivedInquiryListView.as_view(), name="received"),
    path("<int:pk>/deal/accept/", InquiryDealAcceptView.as_view(), name="deal_accept"),
    path("<int:pk>/deal/cancel/", InquiryDealCancelView.as_view(), name="deal_cancel"),
    path("<int:pk>/", InquiryDetailView.as_view(), name="detail"),
]
