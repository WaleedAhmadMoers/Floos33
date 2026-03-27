from django.db import migrations


def seed_categories(apps, schema_editor):
    Category = apps.get_model("stocklots", "Category")

    category_tree = {
        "electronics": {
            "name": "Electronics",
            "children": [
                ("phones", "Phones"),
                ("accessories", "Accessories"),
                ("chargers", "Chargers"),
                ("small-appliances", "Small appliances"),
            ],
        },
        "home-kitchen": {
            "name": "Home & Kitchen",
            "children": [
                ("cookware", "Cookware"),
                ("storage", "Storage"),
                ("cleaning-items", "Cleaning items"),
            ],
        },
        "fashion": {
            "name": "Fashion",
            "children": [
                ("clothing", "Clothing"),
                ("shoes", "Shoes"),
                ("bags", "Bags"),
            ],
        },
        "health-beauty": {
            "name": "Health & Beauty",
            "children": [
                ("cosmetics", "Cosmetics"),
                ("personal-care", "Personal care"),
            ],
        },
        "baby-kids": {
            "name": "Baby & Kids",
            "children": [
                ("toys", "Toys"),
                ("baby-products", "Baby products"),
            ],
        },
        "industrial": {
            "name": "Industrial",
            "children": [
                ("tools", "Tools"),
                ("electrical-items", "Electrical items"),
                ("machinery-parts", "Machinery parts"),
            ],
        },
        "office-stationery": {"name": "Office & Stationery", "children": []},
        "food-beverage": {"name": "Food & Beverage", "children": []},
        "general-merchandise": {"name": "General Merchandise", "children": []},
    }

    for parent_slug, payload in category_tree.items():
        parent, _ = Category.objects.get_or_create(
            slug=parent_slug,
            defaults={"name": payload["name"], "is_active": True},
        )
        if parent.name != payload["name"] or not parent.is_active or parent.parent_id is not None:
            parent.name = payload["name"]
            parent.is_active = True
            parent.parent = None
            parent.save()

        for child_slug, child_name in payload["children"]:
            child, _ = Category.objects.get_or_create(
                slug=child_slug,
                defaults={"name": child_name, "parent": parent, "is_active": True},
            )
            if child.name != child_name or child.parent_id != parent.id or not child.is_active:
                child.name = child_name
                child.parent = parent
                child.is_active = True
                child.save()


def reverse_seed_categories(apps, schema_editor):
    Category = apps.get_model("stocklots", "Category")
    slugs = [
        "electronics",
        "phones",
        "accessories",
        "chargers",
        "small-appliances",
        "home-kitchen",
        "cookware",
        "storage",
        "cleaning-items",
        "fashion",
        "clothing",
        "shoes",
        "bags",
        "health-beauty",
        "cosmetics",
        "personal-care",
        "baby-kids",
        "toys",
        "baby-products",
        "industrial",
        "tools",
        "electrical-items",
        "machinery-parts",
        "office-stationery",
        "food-beverage",
        "general-merchandise",
    ]
    Category.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("stocklots", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_categories, reverse_seed_categories),
    ]
