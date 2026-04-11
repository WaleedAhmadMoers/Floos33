from django.contrib import admin

from core.languages import translation_field_names

from blog.models import Article, ArticleLike


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "original_language", "status", "published_at", "view_count", "updated_at")
    list_filter = ("kind", "status", "original_language", "published_at")
    search_fields = ("title", "slug", "body", *translation_field_names(base_names=("title", "body")))
    readonly_fields = ("created_at", "updated_at", "view_count")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Article", {"fields": ("kind", "status", "original_language", "title", "slug", "body", "featured_image")}),
        ("Publishing", {"fields": ("published_at",)}),
        ("Translations", {"fields": translation_field_names(base_names=("title", "body")), "classes": ("collapse",)}),
        ("Metrics", {"fields": ("view_count", "created_at", "updated_at")}),
    )


@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email", "article__title")
    raw_id_fields = ("user", "article")
