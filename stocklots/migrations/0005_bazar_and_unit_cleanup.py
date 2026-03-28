from django.db import migrations


def add_bazar_category(apps, schema_editor):
    Category = apps.get_model("stocklots", "Category")
    Category.objects.update_or_create(
        slug="bazar",
        defaults={"name": "Bazar", "parent": None, "is_active": True},
    )


def cleanup_unit_type(apps, schema_editor):
    Stocklot = apps.get_model("stocklots", "Stocklot")
    Stocklot.objects.filter(unit_type="container_40ft_hc").update(unit_type="container_40ft")


def reverse_add_bazar(apps, schema_editor):
    Category = apps.get_model("stocklots", "Category")
    Category.objects.filter(slug="bazar").update(is_active=False)


def reverse_cleanup_unit_type(apps, schema_editor):
    Stocklot = apps.get_model("stocklots", "Stocklot")
    Stocklot.objects.filter(unit_type="container_40ft").update(unit_type="container_40ft_hc")


class Migration(migrations.Migration):
    dependencies = [
        ("stocklots", "0004_reseed_categories"),
    ]

    operations = [
        migrations.RunPython(add_bazar_category, reverse_add_bazar),
        migrations.RunPython(cleanup_unit_type, reverse_cleanup_unit_type),
    ]
