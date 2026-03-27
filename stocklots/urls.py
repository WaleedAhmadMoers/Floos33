from django.urls import path

from .views import MarketplaceListView, MyStocklotListView, StocklotCreateView, StocklotDetailView
from .views import StocklotUpdateView

app_name = "stocklots"

urlpatterns = [
    path("stocklots/", MarketplaceListView.as_view(), name="list"),
    path("stocklots/create/", StocklotCreateView.as_view(), name="create"),
    path("stocklots/mine/", MyStocklotListView.as_view(), name="mine"),
    path("stocklots/<slug:slug>/edit/", StocklotUpdateView.as_view(), name="edit"),
    path("stocklots/<slug:slug>/", StocklotDetailView.as_view(), name="detail"),
]
