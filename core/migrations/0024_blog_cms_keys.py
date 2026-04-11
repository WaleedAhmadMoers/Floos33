from django.db import migrations


CMS_BLOG_LABELS = {
    "shared.nav_blog": {
        "page": "shared",
        "text_en": "Blog",
        "text_de": "Blog",
        "text_ar": "المدونة",
        "text_tr": "Blog",
        "text_fa": "وبلاگ",
        "text_fr": "Blog",
        "text_es": "Blog",
        "text_pt": "Blog",
        "text_nl": "Blog",
        "text_zh": "博客",
    },
    "footer.blog_label": {
        "page": "footer",
        "text_en": "Blog",
        "text_de": "Blog",
        "text_ar": "المدونة",
        "text_tr": "Blog",
        "text_fa": "وبلاگ",
        "text_fr": "Blog",
        "text_es": "Blog",
        "text_pt": "Blog",
        "text_nl": "Blog",
        "text_zh": "博客",
    },
}


def seed_blog_cms_blocks(apps, schema_editor):
    CMSBlock = apps.get_model("core", "CMSBlock")

    for key, defaults in CMS_BLOG_LABELS.items():
        CMSBlock.objects.update_or_create(
            key=key,
            defaults={"is_active": True, **defaults},
        )


def noop(apps, schema_editor):
    return None


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0023_aboutcmsblock_contactcmsblock_footercmsblock_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_blog_cms_blocks, noop),
    ]
