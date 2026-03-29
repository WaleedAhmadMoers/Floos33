import random
from decimal import Decimal
import base64
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile

from accounts.models import User, SellerVerificationRequest
from companies.models import Company
from stocklots.models import Stocklot, Category
from rfqs.models import RFQ, RFQConversation, RFQMessage
from inquiries.models import Inquiry, InquiryReply
from core.models import DealTrigger, DealHistory


class Command(BaseCommand):
    help = "Populate realistic demo data for the floos33 marketplace (safe to re-run)."

    DEMO_DOMAIN = "demo.floos33.com"

    def add_arguments(self, parser):
        parser.add_argument("--seed", type=int, default=1234, help="Random seed for reproducibility")
        parser.add_argument("--reset", action="store_true", help="Delete previously generated demo data first")

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(options["seed"])
        if options["reset"]:
            self._reset()

        categories = self._ensure_categories()
        buyers, sellers = self._create_users()
        companies = self._create_companies(sellers)
        self._approve_sellers(companies)
        stocklots = self._create_stocklots(companies, categories)
        rfqs = self._create_rfqs(buyers, categories)
        conversations = self._create_rfq_conversations(rfqs, companies)
        inquiries = self._create_inquiries(buyers, stocklots)
        deals = self._create_deals(inquiries, conversations)

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
        self.stdout.write(
            f"Users: {User.objects.filter(email__icontains=self.DEMO_DOMAIN).count()} "
            f"(buyers {len(buyers)}, sellers {len(sellers)}), "
            f"Companies: {len(companies)}, Stocklots: {len(stocklots)}, "
            f"RFQs: {len(rfqs)}, Conversations: {len(conversations)}, "
            f"Inquiries: {len(inquiries)}, Deals: {len(deals)}"
        )

    # ------------------------------------------------------------------ setup helpers
    def _reset(self):
        DealHistory.objects.filter(deal__buyer__email__icontains=self.DEMO_DOMAIN).delete()
        DealTrigger.objects.filter(buyer__email__icontains=self.DEMO_DOMAIN).delete()
        RFQMessage.objects.filter(conversation__buyer__email__icontains=self.DEMO_DOMAIN).delete()
        RFQConversation.objects.filter(buyer__email__icontains=self.DEMO_DOMAIN).delete()
        RFQ.objects.filter(buyer__email__icontains=self.DEMO_DOMAIN).delete()
        InquiryReply.objects.filter(sender_user__email__icontains=self.DEMO_DOMAIN).delete()
        Inquiry.objects.filter(buyer__email__icontains=self.DEMO_DOMAIN).delete()
        Stocklot.objects.filter(company__owner__email__icontains=self.DEMO_DOMAIN).delete()
        SellerVerificationRequest.objects.filter(user__email__icontains=self.DEMO_DOMAIN).delete()
        Company.objects.filter(owner__email__icontains=self.DEMO_DOMAIN).delete()
        User.objects.filter(email__icontains=self.DEMO_DOMAIN).delete()
        self.stdout.write("Previous demo data removed.")

    def _ensure_categories(self):
        cat_tree = {
            "Electronics": ["Mobile Accessories", "Small Appliances", "Mixed Electronics"],
            "Apparel": ["Shoes", "Men's Apparel", "Women's Apparel", "Kids Apparel"],
            "Tools & DIY": ["Power Tools", "Hand Tools"],
            "Home & Kitchen": ["Cookware", "Small Kitchen", "Home Textiles"],
            "General Merchandise": ["Supermarket Goods", "Furniture", "Stationery"],
        }
        categories = {}
        for parent_name, children in cat_tree.items():
            parent, _ = Category.objects.get_or_create(
                slug=slugify(parent_name), defaults={"name": parent_name, "parent": None, "is_active": True}
            )
            categories[parent.slug] = parent
            for child in children:
                child_slug = slugify(child)
                cat, _ = Category.objects.get_or_create(
                    slug=child_slug, defaults={"name": child, "parent": parent, "is_active": True}
                )
                categories[child_slug] = cat
        return categories

    # ------------------------------------------------------------------ users & companies
    def _create_users(self):
        buyer_names = [
            "Anna Weber", "Lukas Hoffmann", "Sophie Braun", "Tim Seidel", "Nora Klein", "Jonas Adler",
            "Marta Kowalska", "Piotr Nowak", "Eva Novak", "Daniel Rossi", "Elena Petrova", "Hugo Lambert",
            "Isabella Conti", "Victor Garcia"
        ]
        seller_names = [
            "Max Fischer", "Laura Vogel", "Peter Schmitt", "Olga Ivanova", "Jan de Vries", "Sara Nilsson",
            "Pavel Horak", "Kamil Zielinski", "Maja Novak", "Filip Marin", "Carlos Duarte", "Emma Schroeder"
        ]
        buyers = []
        for idx, name in enumerate(buyer_names):
            email = f"{slugify(name)}@{self.DEMO_DOMAIN}"
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": name,
                    "is_buyer": True,
                    "is_seller": False,
                    "is_active": True,
                    "is_verified_user": idx % 3 == 0,  # some admin-verified
                },
            )
            buyers.append(user)

        sellers = []
        for idx, name in enumerate(seller_names):
            email = f"{slugify(name)}@{self.DEMO_DOMAIN}"
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": name,
                    "is_buyer": False,
                    "is_seller": True,
                    "is_active": True,
                    "is_verified_user": idx % 4 == 0,
                },
            )
            sellers.append(user)
        return buyers, sellers

    def _create_companies(self, sellers):
        company_profiles = [
            ("EuroTech Wholesale", "Germany", "Hamburg", "Bulk consumer electronics and graded returns."),
            ("Nordic Liquidators", "Sweden", "Malmo", "Department store returns and overstock pallets."),
            ("Benelux Apparel Trading", "Netherlands", "Rotterdam", "Fashion closeouts and cancelled orders."),
            ("Baltic Tools Supply", "Poland", "Gdansk", "Hand and power tools surplus."),
            ("Adriatic Home Goods", "Croatia", "Zagreb", "Home & kitchen excess inventory."),
            ("Iberia Mobile Parts", "Spain", "Valencia", "Mobile accessories and small devices."),
            ("Danube Construction Lots", "Austria", "Linz", "Construction consumables and fittings."),
            ("Alpine Outfitters", "Switzerland", "Zurich", "Outdoor apparel and footwear."),
            ("Baltic Shoes Exchange", "Lithuania", "Vilnius", "Footwear liquidation lots."),
            ("Central EU Mix", "Czechia", "Brno", "Mixed consumer goods and supermarket returns."),
            ("Appliance Clearance EU", "Germany", "Leipzig", "Small appliances and whitegoods clearance."),
            ("Med Market Traders", "Belgium", "Antwerp", "Health & personal care surplus."),
        ]
        companies = []
        for seller, profile in zip(sellers, company_profiles):
            name, country, city, desc = profile
            company, _ = Company.objects.get_or_create(
                owner=seller,
                defaults={
                    "name": name,
                    "country": country,
                    "city": city,
                    "description": desc,
                },
            )
            companies.append(company)
        return companies

    def _approve_sellers(self, companies):
        for company in companies[:7]:  # approve a subset
            req, _ = SellerVerificationRequest.objects.get_or_create(
                user=company.owner,
                defaults={
                    "company_name": company.name,
                    "contact_person_name": company.owner.full_name,
                    "phone_number": "+49-30-123456",
                    "company_email": company.owner.email,
                    "company_address": f"{company.city} HQ",
                    "country": company.country,
                    "city": company.city,
                    "business_type": "Wholesale",
                    "business_description": company.description,
                    "status": SellerVerificationRequest.Status.APPROVED,
                },
            )
            if req.status != SellerVerificationRequest.Status.APPROVED:
                req.status = SellerVerificationRequest.Status.APPROVED
                req.save(update_fields=["status"])

    # ------------------------------------------------------------------ stocklots
    def _create_stocklots(self, companies, categories):
        template_lots = [
            ("Mixed electronics returns – grade B/C", "mixed-electronics", "customer_return", 22, 5, "pallet", 5200, "EUR", "Germany", "Hamburg"),
            ("Mobile accessories bundle (chargers/cables)", "mobile-accessories", "overstock", 5000, 500, "piece", 0.85, "EUR", "Spain", "Valencia"),
            ("Small kitchen appliances – refurb", "small-appliances", "refurbished", 380, 50, "piece", 18.5, "EUR", "Germany", "Leipzig"),
            ("Power tools assorted pallets", "power-tools", "shelf_pull", 12, 2, "pallet", 6400, "EUR", "Poland", "Poznan"),
            ("Hand tools mixed boxes", "hand-tools", "overstock", 2400, 200, "piece", 3.6, "EUR", "Czechia", "Brno"),
            ("Outdoor jackets A/B grade", "mens-apparel", "b_grade_return", 1800, 200, "piece", 9.5, "EUR", "Netherlands", "Rotterdam"),
            ("Women’s fashion closeout SS25", "womens-apparel", "brand_new", 3200, 400, "piece", 6.2, "EUR", "Belgium", "Antwerp"),
            ("Kids apparel assorted packs", "kids-apparel", "mixed_grade", 2800, 300, "piece", 4.1, "EUR", "Germany", "Cologne"),
            ("Footwear liquidation – mixed sizes", "shoes", "c_grade_return", 2400, 200, "piece", 5.4, "EUR", "Lithuania", "Vilnius"),
            ("Home textiles clearance", "home-textiles", "overstock", 4200, 400, "piece", 3.2, "EUR", "Croatia", "Zagreb"),
            ("Cookware sets – new carton damage", "cookware", "shelf_pull", 900, 100, "set", 14.8, "EUR", "Poland", "Warsaw"),
            ("Supermarket near-expiry mix (dry)", "supermarket-goods", "as_is", 18, 3, "pallet", 2100, "EUR", "Germany", "Duisburg"),
            ("Furniture flatpacks – customer returns", "furniture", "customer_return", 7, 1, "pallet", 7800, "EUR", "Austria", "Linz"),
            ("Stationery bulk cartons", "stationery", "brand_new", 9500, 950, "piece", 0.45, "EUR", "Czechia", "Prague"),
            ("Small appliances salvage", "small-appliances", "salvage", 25, 5, "pallet", 1800, "EUR", "Hungary", "Budapest"),
            ("Mobile phones used grade B", "mixed-electronics", "used", 320, 50, "piece", 65, "EUR", "Germany", "Berlin"),
            ("Tablets mixed models untested", "mixed-electronics", "untested", 180, 30, "piece", 28, "EUR", "Netherlands", "Eindhoven"),
            ("Gaming accessories bundle", "mobile-accessories", "overstock", 2600, 200, "piece", 4.9, "EUR", "Poland", "Gdansk"),
            ("Kitchen smalls new overstock", "small-appliances", "brand_new", 540, 60, "piece", 22, "EUR", "Germany", "Leipzig"),
            ("DIY consumables (screws/anchors)", "hand-tools", "brand_new", 120000, 5000, "piece", 0.03, "EUR", "Spain", "Valencia"),
            ("Lighting fixtures returns", "mixed-electronics", "b_grade_return", 850, 80, "piece", 11.5, "EUR", "Belgium", "Liege"),
            ("Whitegoods scratch & dent", "small-appliances", "c_grade_return", 60, 5, "piece", 130, "EUR", "Germany", "Leipzig"),
            ("Baby clothing bundles", "kids-apparel", "brand_new", 6000, 600, "piece", 2.2, "EUR", "Poland", "Lodz"),
            ("Chef knives sets", "cookware", "brand_new", 1400, 140, "set", 7.9, "EUR", "Italy", "Milan"),
            ("Workwear trousers mix", "mens-apparel", "mixed_grade", 2100, 200, "piece", 8.1, "EUR", "Germany", "Munich"),
            ("Sneakers liquidation B-grade", "shoes", "b_grade_return", 1800, 150, "piece", 11.0, "EUR", "Netherlands", "Tilburg"),
            ("Garden tools assortment", "hand-tools", "overstock", 1600, 160, "piece", 6.7, "EUR", "France", "Lille"),
            ("USB-C chargers EU plug", "mobile-accessories", "brand_new", 9000, 900, "piece", 1.9, "EUR", "Spain", "Madrid"),
            ("Bluetooth speakers pallet", "mixed-electronics", "overstock", 480, 60, "piece", 16.5, "EUR", "Germany", "Hanover"),
            ("Kitchen mixers refurb", "small-appliances", "refurbished", 220, 30, "piece", 35, "EUR", "Germany", "Hamburg"),
            ("Hotel towels surplus", "home-textiles", "brand_new", 5000, 500, "piece", 1.45, "EUR", "Portugal", "Porto"),
            ("Office chairs grade B", "furniture", "b_grade_return", 140, 20, "piece", 48, "EUR", "Germany", "Berlin"),
            ("Supermarket candy short-dated", "supermarket-goods", "as_is", 14, 2, "pallet", 1650, "EUR", "Belgium", "Ghent"),
            ("Household cleaning bundle", "supermarket-goods", "overstock", 18, 3, "pallet", 2400, "EUR", "Germany", "Essen"),
            ("Kitchen knives slight packaging damage", "cookware", "shelf_pull", 1800, 180, "piece", 5.2, "EUR", "Austria", "Graz"),
            ("Refurb laptops mix i5/i7", "mixed-electronics", "refurbished", 140, 20, "piece", 185, "EUR", "Germany", "Berlin"),
            ("PPE gloves cartons", "general-merchandise", "brand_new", 22000, 2000, "piece", 0.06, "EUR", "Poland", "Poznan"),
            ("Bulk batteries AA/AAA", "mixed-electronics", "brand_new", 32000, 2000, "piece", 0.12, "EUR", "Netherlands", "Rotterdam"),
        ]
        stocklots = []
        for idx, lot in enumerate(template_lots):
            (
                title,
                cat_slug,
                condition,
                qty,
                moq,
                unit,
                price,
                currency,
                country,
                city,
            ) = lot
            company = companies[idx % len(companies)]
            category = categories.get(cat_slug) or random.choice(list(categories.values()))
            slug = slugify(f"{title}-{idx}")
            stocklot, created = Stocklot.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "category": category,
                    "company": company,
                    "description": f"{title} available ex-warehouse {city}. Mixed brands, full manifest on request.",
                    "condition": condition,
                    "quantity": qty,
                    "moq": moq,
                    "unit_type": unit,
                    "price": Decimal(str(price)),
                    "currency": currency,
                    "location_country": country,
                    "location_city": city,
                    "status": Stocklot.Status.APPROVED,
                    "is_admin_verified": idx % 3 == 0,
                    "is_active": True,
                },
            )
            if stocklot.images.count() == 0:
                self._attach_placeholder_image(stocklot, idx)
            stocklots.append(stocklot)
        return stocklots

    def _attach_placeholder_image(self, stocklot, seed_idx):
        # 1x1 transparent PNG
        png_bytes = base64.b64decode(
            b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMBAp7xQJ4AAAAASUVORK5CYII="
        )
        image_file = ContentFile(png_bytes, name=f"{stocklot.slug}-{seed_idx}.png")
        stocklot.images.create(file=image_file)

    # ------------------------------------------------------------------ rfqs & conversations
    def _create_rfqs(self, buyers, categories):
        rfq_templates = [
            ("Looking for 20 pallets mixed electronics returns", "mixed-electronics", 20, "pallet", 5200, "Germany", "Hamburg"),
            ("Need 5000 pcs baby clothing", "kids-apparel", 5000, "piece", 2.3, "Poland", "Lodz"),
            ("Searching for EU tools pallets", "hand-tools", 12, "pallet", 5800, "Czechia", "Prague"),
            ("Want 3000 phone chargers EU plug", "mobile-accessories", 3000, "piece", 1.6, "Spain", "Madrid"),
            ("Buying small kitchen appliances refurb", "small-appliances", 400, "piece", 20, "Germany", "Leipzig"),
            ("Looking for sneakers liquidation lot", "shoes", 1500, "piece", 9, "Netherlands", "Amsterdam"),
            ("Household cleaners pallets", "supermarket-goods", 15, "pallet", 1900, "Germany", "Cologne"),
            ("Office chairs B-grade", "furniture", 120, "piece", 45, "Germany", "Berlin"),
            ("A4 paper bulk supply monthly", "stationery", 10000, "piece", 0.8, "Poland", "Warsaw"),
            ("Power tools refurbished stock", "power-tools", 300, "piece", 58, "Austria", "Linz"),
            ("LED lighting fixtures", "mixed-electronics", 1200, "piece", 7.5, "Belgium", "Brussels"),
            ("Workwear trousers ongoing", "mens-apparel", 2500, "piece", 7, "Germany", "Munich"),
            ("Garden tools spring promo", "hand-tools", 1800, "piece", 5.5, "France", "Lille"),
            ("Home textiles hotel quality", "home-textiles", 6000, "piece", 1.8, "Portugal", "Porto"),
            ("Pallets of AA batteries", "mixed-electronics", 25000, "piece", 0.11, "Netherlands", "Rotterdam"),
        ]
        rfqs = []
        for idx, tpl in enumerate(rfq_templates):
            title, cat_slug, qty, unit, target_price, country, city = tpl
            buyer = buyers[idx % len(buyers)]
            category = categories.get(cat_slug) or random.choice(list(categories.values()))
            rfq, _ = RFQ.objects.update_or_create(
                title=title,
                buyer=buyer,
                defaults={
                    "description": title,
                    "category": category,
                    "quantity": qty,
                    "unit_type": unit,
                    "target_price": Decimal(str(target_price)),
                    "currency": Stocklot.Currency.EUR,
                    "location_country": country,
                    "location_city": city,
                    "moderation_status": RFQ.ModerationStatus.APPROVED if idx % 3 != 0 else RFQ.ModerationStatus.PENDING_REVIEW,
                    "status": RFQ.Status.OPEN if idx % 4 != 0 else RFQ.Status.CLOSED,
                },
            )
            rfqs.append(rfq)
        return rfqs

    def _create_rfq_conversations(self, rfqs, companies):
        conversations = []
        for idx, rfq in enumerate(rfqs[:20]):
            seller_company = companies[idx % len(companies)]
            convo, _ = RFQConversation.objects.get_or_create(
                rfq=rfq, seller_company=seller_company, seller_user=seller_company.owner, buyer=rfq.buyer
            )
            # seed a couple of messages
            RFQMessage.objects.get_or_create(
                conversation=convo,
                sender_user=seller_company.owner,
                sender_company=seller_company,
                message=f"Offer for {rfq.title}: can supply {rfq.quantity} {rfq.unit_type} from {seller_company.city}.",
                defaults={"price": rfq.target_price or Decimal("0"), "currency": rfq.currency, "moderation_status": RFQMessage.ModerationStatus.APPROVED},
            )
            RFQMessage.objects.get_or_create(
                conversation=convo,
                sender_user=rfq.buyer,
                sender_company=None,
                message="Can you share manifest and nearest loading date?",
                defaults={"moderation_status": RFQMessage.ModerationStatus.PENDING_REVIEW},
            )
            conversations.append(convo)
        return conversations

    # ------------------------------------------------------------------ inquiries
    def _create_inquiries(self, buyers, stocklots):
        inquiries = []
        for idx, stocklot in enumerate(stocklots[:30]):
            buyer = buyers[idx % len(buyers)]
            inquiry, _ = Inquiry.objects.get_or_create(
                stocklot=stocklot,
                buyer=buyer,
                seller_company=stocklot.company,
                defaults={
                    "subject": f"Inquiry about {stocklot.title}",
                    "message": "Please share latest availability and pallet photos.",
                    "status": Inquiry.Status.APPROVED if idx % 3 else Inquiry.Status.PENDING_ADMIN,
                    "moderation_status": Inquiry.ModerationStatus.APPROVED if idx % 2 else Inquiry.ModerationStatus.PENDING_REVIEW,
                },
            )
            if idx % 2 == 0:
                InquiryReply.objects.get_or_create(
                    inquiry=inquiry,
                    sender_user=stocklot.company.owner,
                    sender_company=stocklot.company,
                    message="Availability confirmed, manifests attached on request.",
                    defaults={"moderation_status": InquiryReply.ModerationStatus.APPROVED},
                )
            inquiries.append(inquiry)
        return inquiries

    # ------------------------------------------------------------------ deals
    def _create_deals(self, inquiries, conversations):
        deals = []
        now = timezone.now()
        # Deals from inquiries
        statuses = [
            (DealTrigger.Status.PENDING, DealTrigger.Progress.NOT_STARTED),
            (DealTrigger.Status.MUTUAL, DealTrigger.Progress.NOT_STARTED),
            (DealTrigger.Status.APPROVED, DealTrigger.Progress.IN_PROGRESS),
            (DealTrigger.Status.APPROVED, DealTrigger.Progress.COMPLETED),
            (DealTrigger.Status.REJECTED, DealTrigger.Progress.NOT_STARTED),
            (DealTrigger.Status.CANCELLED, DealTrigger.Progress.NOT_STARTED),
        ]
        for idx, inquiry in enumerate(inquiries[:12]):
            status, progress = statuses[idx % len(statuses)]
            deal, _ = DealTrigger.objects.get_or_create(
                inquiry=inquiry,
                deal_type=DealTrigger.DealType.INQUIRY,
                defaults={
                    "buyer": inquiry.buyer,
                    "seller_user": inquiry.seller_company.owner,
                    "seller_company": inquiry.seller_company,
                    "status": status,
                    "progress_status": progress,
                    "buyer_accepted": status != DealTrigger.Status.PENDING,
                    "seller_accepted": status in (DealTrigger.Status.MUTUAL, DealTrigger.Status.APPROVED),
                    "buyer_identity_revealed": idx % 3 == 0,
                    "seller_identity_revealed": idx % 4 == 0,
                    "created_at": now - timedelta(days=idx + 1),
                },
            )
            deals.append(deal)
            if deal.buyer_identity_revealed:
                DealHistory.objects.create(
                    deal=deal, actor=inquiry.buyer, action="identity_decision", note="Admin approved identity for buyer"
                )
            if deal.seller_identity_revealed:
                DealHistory.objects.create(
                    deal=deal, actor=inquiry.seller_company.owner, action="identity_decision", note="Admin approved identity for seller"
                )

        # Deals from RFQ conversations
        for idx, convo in enumerate(conversations[:8]):
            status, progress = statuses[(idx + 2) % len(statuses)]
            deal, _ = DealTrigger.objects.get_or_create(
                rfq_conversation=convo,
                deal_type=DealTrigger.DealType.RFQ,
                defaults={
                    "buyer": convo.buyer,
                    "seller_user": convo.seller_user,
                    "seller_company": convo.seller_company,
                    "status": status,
                    "progress_status": progress,
                    "buyer_accepted": True,
                    "seller_accepted": status in (DealTrigger.Status.MUTUAL, DealTrigger.Status.APPROVED),
                    "buyer_identity_revealed": idx % 2 == 0,
                    "seller_identity_revealed": idx % 3 == 0,
                    "created_at": now - timedelta(days=idx + 2),
                },
            )
            deals.append(deal)
        return deals
