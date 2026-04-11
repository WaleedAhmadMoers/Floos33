import base64
from io import BytesIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from companies.models import Company
from stocklots.models import Category, Stocklot, StocklotDocument, StocklotImage


class Command(BaseCommand):
    help = "Populate the database with demo users, company, categories, and stocklots (with multiple images/docs)."

    def handle(self, *args, **options):
        with transaction.atomic():
            self._ensure_categories()
            seller = self._create_user(
                email="seller@example.com",
                full_name="Demo Seller",
                password="password123",
                is_seller=True,
            )
            company = self._create_company(seller, name="Demo Trading LLC")
            self._create_stocklots(company)
        self.stdout.write(self.style.SUCCESS("Demo data created."))

    def _ensure_categories(self):
        # Ensure at least a couple of categories exist for demo listings
        root, _ = Category.objects.get_or_create(slug="bazar", defaults={"name": "Bazar", "is_active": True})
        Category.objects.get_or_create(
            slug="electronics-pallets",
            defaults={"name": "Electronics pallets", "parent": root, "is_active": True},
        )
        Category.objects.get_or_create(
            slug="mixed-shoe-lots",
            defaults={"name": "Mixed shoe lots", "parent": root, "is_active": True},
        )

    def _create_user(self, email, full_name, password, is_seller=False):
        User = get_user_model()
        user, created = User.objects.get_or_create(email=email, defaults={"full_name": full_name, "is_seller": is_seller})
        if created or not user.check_password(password):
            user.set_password(password)
            user.is_seller = is_seller
            user.save()
        return user

    def _create_company(self, user, name):
        company, _ = Company.objects.get_or_create(
            owner=user,
            defaults={
                "name": name,
                "legal_name": name,
                "description": "Sample trading company for demo listings.",
                "phone": "+49 30 0000000",
                "email": "contact@example.com",
                "country": "Germany",
                "city": "Berlin",
                "address": "Demo Street 1",
                "website": "https://example.com",
                "registration_number": "HRB-000000",
                "vat_number": "DE000000000",
            },
        )
        return company

    def _sample_png(self):
        # 1x1 pixel transparent PNG
        png_base64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
        )
        return base64.b64decode(png_base64)

    def _sample_csv(self):
        return "sku,description,qty,price\nSKU-001,Sample item,100,10.00\nSKU-002,Sample item 2,200,8.50\n".encode()

    def _sample_pdf(self):
        # Minimal PDF header with placeholder text (not a full spec PDF but enough for demo download)
        return b"%PDF-1.4\\n1 0 obj<</Type/Catalog>>endobj\\n%%EOF"

    def _create_stocklots(self, company):
        electronics_category = Category.objects.filter(slug="electronics-pallets").first()
        shoes_category = Category.objects.filter(slug="mixed-shoe-lots").first()

        listings = [
            {
                "title": "Mixed electronics pallets",
                "category": electronics_category,
                "description": "Assorted consumer electronics pallets. Mixed brands, tested returns and overstock.",
                "condition": Stocklot.Condition.OVERSTOCK,
                "quantity": 10,
                "moq": 1,
                "unit_type": Stocklot.UnitType.PALLET,
                "price": 12000,
                "currency": Stocklot.Currency.EUR,
                "location_country": "Germany",
                "location_city": "Hamburg",
                "status": Stocklot.Status.APPROVED,
                "is_active": True,
                "is_admin_verified": True,
            },
            {
                "title": "Mixed shoe lots - branded surplus",
                "category": shoes_category,
                "description": "Branded shoes surplus. Mixed sizes, men and women, mostly boxed.",
                "condition": Stocklot.Condition.BRAND_NEW,
                "quantity": 500,
                "moq": 50,
                "unit_type": Stocklot.UnitType.PIECE,
                "price": 6.5,
                "currency": Stocklot.Currency.USD,
                "location_country": "Netherlands",
                "location_city": "Rotterdam",
                "status": Stocklot.Status.APPROVED,
                "is_active": True,
                "is_admin_verified": True,
            },
        ]

        for data in listings:
            stocklot, _ = Stocklot.objects.update_or_create(
                title=data["title"],
                company=company,
                defaults=data,
            )
            self._attach_media(stocklot)

    def _attach_media(self, stocklot):
        png_bytes = self._sample_png()
        csv_bytes = self._sample_csv()
        pdf_bytes = self._sample_pdf()

        # Attach multiple images
        for idx in range(1, 4):
            StocklotImage.objects.create(
                stocklot=stocklot,
                file=ContentFile(png_bytes, name=f"photo-{idx}.png"),
            )

        # Documents
        StocklotDocument.objects.create(
            stocklot=stocklot,
            file=ContentFile(csv_bytes, name="manifest.csv"),
            doc_type=StocklotDocument.DocType.EXCEL,
        )
        StocklotDocument.objects.create(
            stocklot=stocklot,
            file=ContentFile(pdf_bytes, name="brochure.pdf"),
            doc_type=StocklotDocument.DocType.PDF,
        )
