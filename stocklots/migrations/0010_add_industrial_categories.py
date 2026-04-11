from django.db import migrations
from django.template.defaultfilters import slugify


INDUSTRIAL_CATEGORIES = [
    "Metalworking Machinery & Machine Tools",
    "Construction Machinery",
    "Printing Machinery & Printing Presses",
    "Woodworking Machinery",
    "Conveyor Technology & Drive Technology",
    "Forklifts & Material Handling Equipment",
    "Food Processing Machinery",
    "Automation Technology",
    "Storage & Warehousing Technology",
]


def add_categories(apps, schema_editor):
    Category = apps.get_model("stocklots", "Category")
    for name in INDUSTRIAL_CATEGORIES:
        slug = slugify(name)
        Category.objects.get_or_create(slug=slug, defaults={"name": name, "parent": None, "is_active": True})


def remove_categories(apps, schema_editor):
    Category = apps.get_model("stocklots", "Category")
    Category.objects.filter(slug__in=[slugify(n) for n in INDUSTRIAL_CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("stocklots", "0009_favorite"),
    ]

    operations = [
        migrations.RunPython(add_categories, reverse_code=remove_categories),
    ]
