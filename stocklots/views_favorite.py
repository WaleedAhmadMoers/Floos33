from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView

from stocklots.models import Favorite, Stocklot


class FavoriteToggleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        stocklot = get_object_or_404(Stocklot, slug=kwargs.get("slug"))
        favorite, created = Favorite.objects.get_or_create(user=request.user, stocklot=stocklot)
        if not created:
            favorite.delete()
            messages.info(request, "Removed from saved listings.")
        else:
            messages.success(request, "Saved to your favorites.")
        if request.headers.get("HX-Request") or request.headers.get("Accept", "").startswith("application/json"):
            return JsonResponse({"saved": created, "is_favorited": created})
        return redirect(stocklot.get_absolute_url())


class FavoriteListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = "stocklots/favorites_list.html"
    context_object_name = "favorites"

    def get_queryset(self):
        return (
            Favorite.objects.select_related("stocklot", "stocklot__company", "stocklot__category", "stocklot__category__parent")
            .filter(user=self.request.user, stocklot__status=Stocklot.Status.APPROVED, stocklot__is_active=True)
            .order_by("-created_at")
        )
