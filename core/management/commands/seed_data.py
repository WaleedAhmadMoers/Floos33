import random
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from companies.models import Company
from inquiries.models import Inquiry, InquiryReply
from rfqs.models import RFQ, RFQConversation, RFQMessage
from stocklots.models import Category, Stocklot


class Command(BaseCommand):
    help = "Populate the database with realistic seed data for testing."

    def add_arguments(self, parser):
        parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(options["seed"])
        buyers, sellers = self._create_users()
        companies = self._create_companies(sellers)
        categories = self._ensure_categories()
        stocklots = self._create_stocklots(companies, categories)
        rfqs = self._create_rfqs(buyers, categories)
        conversations = self._create_rfq_conversations(rfqs, companies)
        self._create_inquiries(buyers, companies, stocklots)

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
        self.stdout.write(
            f"Users: {len(buyers) + len(sellers)}, Companies: {len(companies)}, "
            f"Stocklots: {len(stocklots)}, RFQs: {len(rfqs)}, Conversations: {len(conversations)}"
        )

    # ------------------------------------------------------------------ users & companies
    def _create_users(self):
        buyer_names = [
            "Alice Meyer",
            "Bob Fischer",
            "Clara Schmidt",
            "David Braun",
            "Eva Hoffmann",
            "Felix Richter",
            "Greta Schulz",
            "Hanna König",
            "Ian Wagner",
            "Julia Keller",
            "Kevin Berger",
            "Lena Wolf",
            "Max Neumann",
            "Nora Peters",
            "Oscar Vogel",
        ]
        seller_names = [
            "Peter Baumann",
            "Sophie Lehmann",
            "Tobias Hartmann",
            "Uwe Kraus",
            "Vanessa Albrecht",
            "Wolfgang Dietrich",
            "Xenia Kurz",
            "Yannick Lorenz",
            "Zoe Kramer",
            "Marco Schuster",
            "Elena Frei",
            "Rene Lang",
            "Sabine Arnold",
            "Tim Keller",
            "Mara Fuchs",
        ]
        buyers = []
        sellers = []
        for name in buyer_names:
            email = f"{name.lower().replace(' ', '.')}@buyer.demo"
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": name,
                    "is_buyer": True,
                    "is_seller": False,
                    "is_active": True,
                    "preferred_language": User.PreferredLanguage.ENGLISH,
                },
            )
            user.set_password("test1234")
            user.save()
            buyers.append(user)
        for name in seller_names:
            email = f"{name.lower().replace(' ', '.')}@seller.demo"
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": name,
                    "is_buyer": True,
                    "is_seller": True,
                    "is_active": True,
                    "preferred_language": User.PreferredLanguage.ENGLISH,
                },
            )
            user.set_password("test1234")
            user.save()
            sellers.append(user)
        return buyers, sellers

    def _create_companies(self, sellers):
        company_names = [
            "EU Trading GmbH",
            "Global Stock BV",
            "Liquidation Hub SRL",
            "Nordic Surplus Oy",
            "Baltic Wholesale UAB",
            "Alpine Deals AG",
            "Benelux Merchandise NV",
            "Danube Supply Kft",
            "Iberia Lots SL",
            "Adriatic Traders DOO",
            "Central Europe Stock Sp z o.o.",
            "Scandi Liquidators AB",
            "Rhine Commerce GmbH",
            "Baltic Blue OÜ",
            "Vistula Goods SA",
        ]
        eu_cities = [
            ("Germany", "Hamburg"),
            ("Netherlands", "Rotterdam"),
            ("Belgium", "Antwerp"),
            ("Poland", "Gdansk"),
            ("Spain", "Valencia"),
            ("Italy", "Milan"),
            ("France", "Lyon"),
            ("Austria", "Vienna"),
            ("Czech Republic", "Prague"),
            ("Romania", "Bucharest"),
            ("Portugal", "Porto"),
            ("Bulgaria", "Sofia"),
            ("Greece", "Thessaloniki"),
            ("Croatia", "Zagreb"),
            ("Finland", "Helsinki"),
        ]
        companies = []
        for seller, cname, loc in zip(sellers, company_names, eu_cities):
            country, city = loc
            company, _ = Company.objects.get_or_create(
                owner=seller,
                defaults={
                    "name": cname,
                    "legal_name": cname,
                    "description": "European wholesale and liquidation specialist.",
                    "phone": "+49-40-123456",
                    "email": f"contact@{cname.split()[0].lower()}.demo",
                    "country": country,
                    "city": city,
                    "address": f"{cname} Street 12",
                    "website": f"https://{cname.split()[0].lower()}.demo",
                    "registration_number": f"REG-{seller.id}",
                    "vat_number": f"EU{seller.id:05d}",
                    "identity_status": Company.IdentityStatus.REVEALED,
                },
            )
            companies.append(company)
        return companies

    # ------------------------------------------------------------------ categories
    def _ensure_categories(self):
        # Use existing categories; if missing, create a small representative set.
        if Category.objects.exists():
            return list(Category.objects.filter(is_active=True))
        roots = {
            "Electronics": ["Smartphones", "Computers", "TVs"],
            "Clothing": ["Mixed clothing lots", "Shoes", "Accessories"],
            "Home": ["Small appliances", "Large appliances", "Home & garden"],
        }
        categories = []
        for root, children in roots.items():
            parent, _ = Category.objects.get_or_create(name=root, slug=root.lower().replace(" ", "-"))
            categories.append(parent)
            for child in children:
                c, _ = Category.objects.get_or_create(
                    name=child,
                    slug=f"{parent.slug}-{child.lower().replace(' ', '-')}",
                    parent=parent,
                )
                categories.append(c)
        return categories

    # ------------------------------------------------------------------ stocklots
    def _create_stocklots(self, companies, categories):
        titles = [
            "Pallets of refurbished laptops",
            "Overstock winter jackets mixed sizes",
            "Customer return smartphones A/B grade",
            "Kitchen appliance pallets (mix of blenders & coffee makers)",
            "Shelf pull smart TVs 55-65 inch",
            "Mixed footwear lot – branded sneakers",
            "Home cleaning products – EU surplus",
            "Power tools pallet – drills and grinders",
            "Assorted gaming consoles and accessories",
            "Small home appliances – air fryers and toasters",
        ]
        stocklots = []
        for i in range(50):
            seller_company = random.choice(companies)
            category = random.choice(categories)
            title = random.choice(titles) + f" #{i+1}"
            quantity = random.randint(50, 500)
            moq = random.randint(10, min(100, quantity))
            status = Stocklot.Status.APPROVED if i % 10 != 0 else Stocklot.Status.PENDING_REVIEW
            stocklot, _ = Stocklot.objects.get_or_create(
                title=title,
                company=seller_company,
                defaults={
                    "description": f"Batch of {quantity} units. Ideal for B2B resale. Mixed brands, tested where applicable. Lot ref {i+1}.",
                    "category": category,
                    "condition": random.choice(Stocklot.Condition.values),
                    "quantity": quantity,
                    "moq": moq,
                    "unit_type": random.choice(Stocklot.UnitType.values),
                    "price": random.randint(5000, 50000),
                    "currency": random.choice(Stocklot.Currency.values),
                    "location_country": seller_company.country,
                    "location_city": seller_company.city,
                    "status": status,
                    "is_active": True,
                    "is_admin_verified": status == Stocklot.Status.APPROVED,
                },
            )
            stocklots.append(stocklot)
        return stocklots

    # ------------------------------------------------------------------ rfqs
    def _create_rfqs(self, buyers, categories):
        titles = [
            "Looking for pallets of mixed smartphones",
            "Need 2000 pcs branded sneakers",
            "Seeking kitchen appliance returns A/B grade",
            "Request for overstock laptops i5/i7",
            "Buying customer return TVs 50-65 inch",
            "Short-dated food and beverage pallets",
            "Surplus winter clothing adult sizes",
            "Power tools surplus wanted",
            "Office chairs and desks bulk purchase",
            "Home textiles pallets (bedding/towels)",
        ]
        rfqs = []
        for i in range(20):
            buyer = random.choice(buyers)
            category = random.choice(categories)
            rfq, _ = RFQ.objects.get_or_create(
                title=random.choice(titles) + f" #{i+1}",
                buyer=buyer,
                defaults={
                    "description": "We are sourcing for EU distribution. Interested in consistent supply with inspection reports.",
                    "category": category,
                    "quantity": random.randint(200, 2000),
                    "unit_type": random.choice(Stocklot.UnitType.values),
                    "target_price": random.randint(2000, 20000),
                    "currency": random.choice(Stocklot.Currency.values),
                    "location_country": random.choice(
                        ["Germany", "Netherlands", "Belgium", "France", "Spain", "Italy", "Poland", "Portugal"]
                    ),
                    "location_city": random.choice(["Hamburg", "Rotterdam", "Antwerp", "Madrid", "Milan", "Paris"]),
                    "status": RFQ.Status.OPEN,
                },
            )
            rfqs.append(rfq)
        return rfqs

    # ------------------------------------------------------------------ rfq conversations/messages
    def _create_rfq_conversations(self, rfqs, companies):
        conversations = []
        sample_rfqs = random.sample(rfqs, min(8, len(rfqs)))
        for rfq in sample_rfqs:
            seller_company = random.choice(companies)
            convo, _ = RFQConversation.objects.get_or_create(
                rfq=rfq,
                buyer=rfq.buyer,
                seller_company=seller_company,
                seller_user=seller_company.owner,
            )
            # messages
            msgs = [
                ("pending_review", "Hello, we can supply this lot. Please confirm target specs."),
                ("approved", "Offer: 250 units palletized, mixed grades A/B."),
                ("approved", "Price proposal as discussed."),
            ]
            for status, text in msgs:
                RFQMessage.objects.get_or_create(
                    conversation=convo,
                    sender_user=seller_company.owner,
                    sender_company=seller_company,
                    message=text,
                    defaults={
                        "price": random.randint(5000, 20000),
                        "currency": random.choice(Stocklot.Currency.values),
                        "moderation_status": status,
                    },
                )
            conversations.append(convo)
        return conversations

    # ------------------------------------------------------------------ inquiries
    def _create_inquiries(self, buyers, companies, stocklots):
        sample_stocklots = random.sample(stocklots, min(12, len(stocklots)))
        for lot in sample_stocklots:
            buyer = random.choice(buyers)
            if buyer == lot.company.owner:
                continue
            inquiry, _ = Inquiry.objects.get_or_create(
                stocklot=lot,
                buyer=buyer,
                seller_company=lot.company,
                defaults={
                    "subject": f"Inquiry about {lot.title}",
                    "message": "Please share packing list and defect rates.",
                    "status": Inquiry.Status.PENDING_ADMIN,
                    "moderation_status": Inquiry.ModerationStatus.PENDING_REVIEW,
                },
            )
            InquiryReply.objects.get_or_create(
                inquiry=inquiry,
                sender_user=lot.company.owner,
                sender_company=lot.company,
                message="We can provide inspection photos and full manifests.",
                defaults={"moderation_status": InquiryReply.ModerationStatus.APPROVED},
            )
