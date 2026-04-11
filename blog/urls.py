from django.urls import path

from blog.views import ArticleDetailView, ArticleLikeToggleView, ArticleListView

app_name = "blog"

urlpatterns = [
    path("", ArticleListView.as_view(), name="list"),
    path("<slug:slug>/like/", ArticleLikeToggleView.as_view(), name="like_toggle"),
    path("<slug:slug>/", ArticleDetailView.as_view(), name="detail"),
]
