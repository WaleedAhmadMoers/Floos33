from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Exists, F, OuterRef, Value, BooleanField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView

from blog.models import Article, ArticleLike
from core.context_processors import resolve_site_language


class ArticleListView(ListView):
    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        language_code = resolve_site_language(self.request)
        now = timezone.now()
        queryset = (
            Article.objects.filter(status=Article.Status.PUBLISHED, published_at__isnull=False, published_at__lte=now)
            .filter(Article.visible_in_language_q(language_code))
            .annotate(likes_count=Count("likes", distinct=True))
            .order_by("-published_at", "-created_at")
        )

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(is_liked=Exists(ArticleLike.objects.filter(user=self.request.user, article=OuterRef("pk"))))
        else:
            queryset = queryset.annotate(is_liked=Value(False, output_field=BooleanField()))

        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset = queryset.filter(Article.public_search_q(language_code, search_query))

        kind = self.request.GET.get("kind", "").strip()
        if kind in {choice[0] for choice in Article.Kind.choices}:
            queryset = queryset.filter(kind=kind)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language_code = resolve_site_language(self.request)
        for article in context["articles"]:
            article.prepare_for_language(language_code)
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["selected_kind"] = self.request.GET.get("kind", "").strip()
        context["article_kind_choices"] = Article.Kind.choices
        query = self.request.GET.copy()
        query.pop("page", None)
        base_query = query.urlencode()
        context["pagination_base_query"] = f"&{base_query}" if base_query else ""
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = "blog/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        language_code = resolve_site_language(self.request)
        now = timezone.now()
        return (
            Article.objects.filter(status=Article.Status.PUBLISHED, published_at__isnull=False, published_at__lte=now)
            .filter(Article.visible_in_language_q(language_code))
            .annotate(likes_count=Count("likes", distinct=True))
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Article.objects.filter(pk=obj.pk).update(view_count=F("view_count") + 1)
        obj.refresh_from_db(fields=["view_count"])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language_code = resolve_site_language(self.request)
        self.object.prepare_for_language(language_code)
        context["is_liked"] = (
            ArticleLike.objects.filter(user=self.request.user, article=self.object).exists()
            if self.request.user.is_authenticated
            else False
        )
        context["related_articles"] = []
        now = timezone.now()
        related = (
            Article.objects.filter(status=Article.Status.PUBLISHED, published_at__isnull=False, published_at__lte=now, kind=self.object.kind)
            .filter(Article.visible_in_language_q(language_code))
            .exclude(pk=self.object.pk)
            .annotate(likes_count=Count("likes", distinct=True))
            .order_by("-published_at", "-created_at")[:3]
        )
        for article in related:
            article.prepare_for_language(language_code)
            context["related_articles"].append(article)
        return context


class ArticleLikeToggleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        language_code = resolve_site_language(request)
        article = get_object_or_404(
            Article.objects.filter(status=Article.Status.PUBLISHED, published_at__isnull=False, published_at__lte=timezone.now())
            .filter(Article.visible_in_language_q(language_code)),
            slug=kwargs["slug"],
        )

        like, created = ArticleLike.objects.get_or_create(user=request.user, article=article)
        if not created:
            like.delete()
            liked = False
            messages.info(request, "Article removed from your likes.")
        else:
            liked = True
            messages.success(request, "Article liked.")

        like_count = article.likes.count()
        if request.headers.get("HX-Request") or request.headers.get("Accept", "").startswith("application/json"):
            return JsonResponse({"liked": liked, "like_count": like_count})
        return redirect(article.get_absolute_url())
