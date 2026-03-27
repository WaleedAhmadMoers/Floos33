from django.views.generic import TemplateView

from stocklots.models import Stocklot


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["homepage_stocklots"] = (
            Stocklot.objects.select_related("company", "category", "category__parent")
            .filter(status=Stocklot.Status.PUBLISHED, is_active=True)
            .order_by("-created_at")[:6]
        )
        return context


class AboutView(TemplateView):
    template_name = "core/about.html"


class ContactView(TemplateView):
    template_name = "core/contact.html"
