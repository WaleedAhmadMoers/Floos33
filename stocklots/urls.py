from django.urls import path

from .views import (
    MarketplaceListView,
    MyStocklotListView,
    StocklotCreateView,
    StocklotActivateView,
    StocklotDeactivateView,
    StocklotDeleteView,
    StocklotDetailView,
    StocklotMarkSoldView,
    StocklotUnmarkSoldView,
    StocklotUpdateView,
)
from .views_favorite import FavoriteListView, FavoriteToggleView

app_name = "stocklots"

urlpatterns = [
    path("", MarketplaceListView.as_view(), name="list"),
    path("create/", StocklotCreateView.as_view(), name="create"),
    path("mine/", MyStocklotListView.as_view(), name="mine"),
    path("favorites/", FavoriteListView.as_view(), name="favorites"),
    path("<slug:slug>/favorite-toggle/", FavoriteToggleView.as_view(), name="favorite_toggle"),
    path("<slug:slug>/edit/", StocklotUpdateView.as_view(), name="edit"),
    path("<slug:slug>/mark-sold/", StocklotMarkSoldView.as_view(), name="mark_sold"),
    path("<slug:slug>/deactivate/", StocklotDeactivateView.as_view(), name="deactivate"),
    path("<slug:slug>/activate/", StocklotActivateView.as_view(), name="activate"),
    path("<slug:slug>/restore/", StocklotUnmarkSoldView.as_view(), name="restore"),
    path("<slug:slug>/delete/", StocklotDeleteView.as_view(), name="delete"),
    path("<slug:slug>/", StocklotDetailView.as_view(), name="detail"),
]
