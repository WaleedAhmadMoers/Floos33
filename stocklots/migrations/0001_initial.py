from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("companies", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, verbose_name="name")),
                ("slug", models.SlugField(max_length=140, unique=True, verbose_name="slug")),
                ("is_active", models.BooleanField(default=True, verbose_name="active")),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="stocklots.category",
                        verbose_name="parent category",
                    ),
                ),
            ],
            options={
                "verbose_name": "category",
                "verbose_name_plural": "categories",
                "ordering": ["parent__name", "name"],
            },
        ),
        migrations.CreateModel(
            name="Stocklot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="title")),
                ("slug", models.SlugField(blank=True, max_length=280, unique=True, verbose_name="slug")),
                ("description", models.TextField(verbose_name="description")),
                (
                    "condition",
                    models.CharField(
                        choices=[
                            ("new", "New"),
                            ("like_new", "Like new"),
                            ("customer_return", "Customer return"),
                            ("shelf_pull", "Shelf pull"),
                            ("mixed", "Mixed"),
                            ("used", "Used"),
                        ],
                        max_length=30,
                        verbose_name="condition",
                    ),
                ),
                ("quantity", models.PositiveIntegerField(verbose_name="quantity")),
                ("moq", models.PositiveIntegerField(verbose_name="minimum order quantity")),
                (
                    "unit_type",
                    models.CharField(
                        choices=[
                            ("piece", "Piece"),
                            ("carton", "Carton"),
                            ("pallet", "Pallet"),
                            ("set", "Set"),
                            ("kg", "Kilogram"),
                            ("lot", "Lot"),
                        ],
                        default="piece",
                        max_length=20,
                        verbose_name="unit type",
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, default="0.00", max_digits=12, verbose_name="price")),
                (
                    "currency",
                    models.CharField(
                        choices=[
                            ("USD", "US Dollar"),
                            ("EUR", "Euro"),
                            ("SAR", "Saudi Riyal"),
                            ("AED", "UAE Dirham"),
                        ],
                        default="USD",
                        max_length=3,
                        verbose_name="currency",
                    ),
                ),
                ("location_country", models.CharField(max_length=120, verbose_name="location country")),
                ("location_city", models.CharField(max_length=120, verbose_name="location city")),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")],
                        default="draft",
                        max_length=20,
                        verbose_name="status",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="active")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="stocklots",
                        to="stocklots.category",
                        verbose_name="category",
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stocklots",
                        to="companies.company",
                        verbose_name="company",
                    ),
                ),
            ],
            options={
                "verbose_name": "stocklot",
                "verbose_name_plural": "stocklots",
                "ordering": ["-created_at"],
            },
        ),
    ]
