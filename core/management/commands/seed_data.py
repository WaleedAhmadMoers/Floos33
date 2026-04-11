import base64
import random
from datetime import timedelta
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from accounts.models import BuyerVerificationRequest, SellerVerificationRequest, User
from blog.models import Article, ArticleLike
from companies.models import Company
from core.languages import SUPPORTED_LANGUAGE_CHOICES
from core.models import CMSBlock, DealHistory, DealTrigger, Notification, SupportMessage
from inquiries.models import Inquiry, InquiryReply
from rfqs.models import RFQ, RFQConversation, RFQFavorite, RFQMessage
from stocklots.models import Category, Favorite, Stocklot, StocklotDocument, StocklotImage


class Command(BaseCommand):
    help = "Seed realistic multilingual test data across the floos33 platform."

    SEED_DOMAIN = "seed.floos33.local"
    DEV_PASSWORD = "devpass123"
    IMAGE_BYTES = base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMBAp7xQJ4AAAAASUVORK5CYII="
    )
    PDF_BYTES = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\n%%EOF"
    CSV_BYTES = (
        "sku,description,qty,price\n"
        "SKU-1001,Seed stock item,120,12.00\n"
        "SKU-1002,Seed stock item,80,9.50\n"
    ).encode("utf-8")
    LANGUAGES = [code for code, _label in SUPPORTED_LANGUAGE_CHOICES]

    BUYER_PROFILES = [
        ("Anna Weber", "Germany", "Hamburg", "de"),
        ("Karim Haddad", "United Arab Emirates", "Dubai", "ar"),
        ("Nora Silva", "Portugal", "Porto", "pt"),
        ("Lukas Meier", "Germany", "Stuttgart", "de"),
        ("Mina Rahimi", "United Arab Emirates", "Dubai", "fa"),
        ("Clara Martin", "France", "Lyon", "fr"),
        ("Youssef Mansour", "Egypt", "Cairo", "ar"),
        ("Sofia Alvarez", "Spain", "Valencia", "es"),
        ("Emre Kaya", "Turkey", "Istanbul", "tr"),
        ("Jasper van Dijk", "Netherlands", "Rotterdam", "nl"),
        ("Li Wei", "China", "Shenzhen", "zh"),
        ("Marta Kowalska", "Poland", "Warsaw", "en"),
        ("Daniel Rossi", "Italy", "Milan", "en"),
        ("Rania El Fassi", "Morocco", "Casablanca", "ar"),
        ("Paula Costa", "Portugal", "Lisbon", "pt"),
        ("Hugo Lambert", "Belgium", "Antwerp", "fr"),
        ("Tobias Schmidt", "Germany", "Berlin", "de"),
        ("Salma Farouk", "Jordan", "Amman", "ar"),
    ]

    SELLER_PROFILES = [
        ("Max Fischer", "Germany", "Hamburg", "de"),
        ("Svenja Kruger", "Germany", "Leipzig", "de"),
        ("Jan de Vries", "Netherlands", "Rotterdam", "nl"),
        ("Carlos Duarte", "Portugal", "Porto", "pt"),
        ("Elena Conti", "Italy", "Milan", "en"),
        ("Omar Benali", "Morocco", "Casablanca", "ar"),
        ("Meryem Kaya", "Turkey", "Istanbul", "tr"),
        ("Farid Hosseini", "United Arab Emirates", "Dubai", "fa"),
        ("Claire Bernard", "France", "Lille", "fr"),
        ("Pablo Garcia", "Spain", "Valencia", "es"),
        ("Marek Nowak", "Poland", "Gdansk", "en"),
        ("Niels Jansen", "Netherlands", "Eindhoven", "nl"),
        ("Layla Saeed", "Saudi Arabia", "Jeddah", "ar"),
        ("Chen Yu", "China", "Ningbo", "zh"),
        ("Petra Novak", "Czech Republic", "Brno", "en"),
        ("Ibrahim Khaled", "Egypt", "Alexandria", "ar"),
        ("Yara Salem", "Jordan", "Amman", "ar"),
        ("Aylin Demir", "Turkey", "Izmir", "tr"),
    ]

    COMPANY_PROFILES = [
        ("EuroTech Returns GmbH", "Germany", "Hamburg", "Electronics returns, graded devices, and mobile accessories for export buyers."),
        ("Leipzig Home Outlet", "Germany", "Leipzig", "Kitchen appliances, homeware, and seasonal overstock from retail chains."),
        ("Benelux Fashion Liquidators", "Netherlands", "Rotterdam", "Fashion closeouts, footwear surplus, and cancelled private-label orders."),
        ("Atlantic FMCG Trading", "Portugal", "Porto", "Short-dated FMCG, household consumables, and promo stock for discount channels."),
        ("Milano Retail Surplus", "Italy", "Milan", "Department store returns and mixed general merchandise for off-price buyers."),
        ("Maghreb Stock Bridge", "Morocco", "Casablanca", "EU closeout lots with regular volume for North Africa and Gulf buyers."),
        ("Bosphorus Industrial Lots", "Turkey", "Istanbul", "Industrial tools, machinery spares, and construction-related stocklots."),
        ("Dubai Recommerce Hub", "United Arab Emirates", "Dubai", "Cross-border electronics and lifestyle stock for MENA wholesale demand."),
        ("Nord France Palettes", "France", "Lille", "Mixed pallets of apparel, footwear, and seasonal retail surplus."),
        ("Iberia Mobile Supply", "Spain", "Valencia", "Mobile accessories, small electronics, and consumer-tech overstock."),
        ("Baltic Tools Wholesale", "Poland", "Gdansk", "Tools, DIY assortments, and warehouse-clearance hardware lines."),
        ("Brainport Smart Goods", "Netherlands", "Eindhoven", "Consumer electronics, smart home goods, and refurbished devices."),
        ("Red Sea Commerce Co.", "Saudi Arabia", "Jeddah", "Household goods, packaged food, and mixed pallets for regional resale."),
        ("Ningbo Export Deals", "China", "Ningbo", "Factory overrun consumer products packed for export container business."),
    ]

    CATEGORY_TREE = {
        "electronics": ("Electronics", ["Mobile Accessories", "Mixed Electronics", "Smart Home"]),
        "fmcg": ("FMCG", ["Packaged Grocery", "Household Cleaners", "Personal Care"]),
        "apparel": ("Apparel", ["Shoes", "Kids Apparel", "Fashion Mix"]),
        "machinery": ("Machinery", ["Industrial Equipment", "Construction Tools", "Sewing Machines"]),
        "home": ("Home & Living", ["Small Appliances", "Home Textiles", "Furniture"]),
    }

    ITEM_TRANSLATIONS = {
        "mixed_electronics": {"en": "mixed electronics returns", "de": "gemischte Elektronik-Retouren", "ar": "مرتجعات إلكترونيات متنوعة", "tr": "karisik elektronik iadeleri", "fa": "مرجوعي الکترونيک مخلوط", "fr": "retours electroniques mixtes", "es": "devoluciones electronicas mixtas", "pt": "devolucoes eletronicas mistas", "nl": "gemengde elektronica-retouren", "zh": "混合电子退货"},
        "phone_accessories": {"en": "smartphone accessories bundle", "de": "Smartphone-Zubehor-Bundle", "ar": "دفعة اكسسوارات هواتف ذكية", "tr": "akilli telefon aksesuar paketi", "fa": "بسته لوازم جانبي گوشي هوشمند", "fr": "lot d'accessoires smartphone", "es": "lote de accesorios para smartphone", "pt": "lote de acessorios para smartphone", "nl": "bundel smartphone-accessoires", "zh": "手机配件组合"},
        "branded_sneakers": {"en": "branded sneakers liquidation", "de": "Marken-Sneaker-Liquidation", "ar": "تصفية احذية رياضية بعلامات معروفة", "tr": "markali spor ayakkabi tasfiyesi", "fa": "تسويه کفش ورزشي برنددار", "fr": "liquidation de baskets de marque", "es": "liquidacion de zapatillas de marca", "pt": "liquidacao de tenis de marca", "nl": "liquidatie van merksneakers", "zh": "品牌运动鞋清仓"},
        "kitchen_appliances": {"en": "small kitchen appliances", "de": "kleine Kuchengerate", "ar": "اجهزة مطبخ صغيرة", "tr": "kucuk mutfak cihazlari", "fa": "لوازم کوچک آشپزخانه", "fr": "petits appareils de cuisine", "es": "pequenos electrodomesticos de cocina", "pt": "pequenos aparelhos de cozinha", "nl": "kleine keukenapparaten", "zh": "小型厨房电器"},
        "hotel_linen": {"en": "hotel bed linen surplus", "de": "Hotel-Bettwasche-Uberschuss", "ar": "فائض مفروشات فنادق", "tr": "otel nevresim fazlasi", "fa": "مازاد ملحفه هتل", "fr": "surplus de linge d'hotel", "es": "excedente de ropa de cama hotelera", "pt": "excedente de roupa de cama de hotel", "nl": "overschot aan hotelbeddengoed", "zh": "酒店床品余货"},
        "cleaners": {"en": "household cleaners pallets", "de": "Haushaltsreiniger auf Paletten", "ar": "طبليات منظفات منزلية", "tr": "ev temizlik urunleri paleti", "fa": "پالت مواد پاک کننده خانگي", "fr": "palettes de produits de nettoyage", "es": "palets de limpiadores del hogar", "pt": "paletes de produtos de limpeza", "nl": "pallets met huishoudreinigers", "zh": "家用清洁用品托盘"},
        "power_tools": {"en": "construction power tools", "de": "Bau-Elektrowerkzeuge", "ar": "معدات كهربائية للبناء", "tr": "insaat tipi elektrikli aletler", "fa": "ابزار برقي ساختماني", "fr": "outils electriques de chantier", "es": "herramientas electricas de obra", "pt": "ferramentas eletricas de construcao", "nl": "elektrisch bouwgereedschap", "zh": "建筑电动工具"},
        "sewing_machines": {"en": "industrial sewing machines", "de": "industrielle Nahmaschinen", "ar": "ماكينات خياطة صناعية", "tr": "endustriyel dikis makineleri", "fa": "چرخ خياطي صنعتي", "fr": "machines a coudre industrielles", "es": "maquinas de coser industriales", "pt": "maquinas de costura industriais", "nl": "industriële naaimachines", "zh": "工业缝纫机"},
        "baby_apparel": {"en": "baby apparel closeout", "de": "Babybekleidung-Abverkauf", "ar": "تصفية ملابس اطفال", "tr": "bebek giyim kapanis lotu", "fa": "تسويه پوشاک نوزاد", "fr": "destockage de vetements bebe", "es": "liquidacion de ropa de bebe", "pt": "queima de roupas de bebe", "nl": "uitverkoop babykleding", "zh": "婴童服装清仓"},
        "office_chairs": {"en": "grade B office chairs", "de": "B-Ware Burostuhle", "ar": "كراسي مكتب درجة ب", "tr": "B kalite ofis sandalyeleri", "fa": "صندلي اداري گريد B", "fr": "chaises de bureau grade B", "es": "sillas de oficina grado B", "pt": "cadeiras de escritorio grau B", "nl": "kantoorstoelen klasse B", "zh": "B级办公椅"},
        "packaged_grocery": {"en": "packaged grocery mix", "de": "Sortiment verpackter Lebensmittel", "ar": "تشكيلة مواد غذائية معبأة", "tr": "paketli market urunleri karisimi", "fa": "ترکيب خواربار بسته بندي", "fr": "mix d'epicerie emballee", "es": "mezcla de abarrotes envasados", "pt": "mix de mercearia embalada", "nl": "mix van verpakte kruidenierswaren", "zh": "包装食品混合货"},
        "solar_lights": {"en": "solar lighting kits", "de": "Solarbeleuchtungs-Sets", "ar": "اطقم انارة شمسية", "tr": "gunes enerjili aydinlatma setleri", "fa": "کيت روشنايي خورشيدي", "fr": "kits d'eclairage solaire", "es": "kits de iluminacion solar", "pt": "kits de iluminacao solar", "nl": "sets voor zonne-verlichting", "zh": "太阳能照明套件"},
    }
    ARTICLE_TOPICS = {
        "inspect_returns": {"en": "How to inspect mixed electronics returns", "de": "So prufen Sie gemischte Elektronik-Retouren", "ar": "كيف تفحص مرتجعات الإلكترونيات المتنوعة", "tr": "Karisik elektronik iadeleri nasil kontrol edilir", "fa": "چگونه مرجوعي هاي الکترونيکي مخلوط را بررسي کنيم", "fr": "Comment controler des retours electroniques mixtes", "es": "Como inspeccionar devoluciones electronicas mixtas", "pt": "Como inspecionar devolucoes eletronicas mistas", "nl": "Zo inspecteert u gemengde elektronica-retouren", "zh": "如何检查混合电子退货"},
        "short_dated": {"en": "5 checks before buying short-dated FMCG", "de": "5 Prufpunkte vor dem Kauf kurz datierter FMCG", "ar": "5 فحوصات قبل شراء سلع استهلاكية قصيرة الصلاحية", "tr": "Kisa tarihli FMCG almadan once 5 kontrol", "fa": "5 بررسي پيش از خريد FMCG کوتاه تاريخ", "fr": "5 verifications avant d'acheter du FMCG a date courte", "es": "5 controles antes de comprar FMCG de fecha corta", "pt": "5 verificacoes antes de comprar FMCG de data curta", "nl": "5 controles voor aankoop van kortgedateerde FMCG", "zh": "购买临期快消品前的5项检查"},
        "export_workflow": {"en": "Building a repeatable export workflow from EU warehouses", "de": "So bauen Sie einen wiederholbaren Exportprozess aus EU-Lagern auf", "ar": "بناء سير عمل تصدير قابل للتكرار من مخازن الاتحاد الأوروبي", "tr": "AB depolarindan tekrar edilebilir bir ihracat akisi kurmak", "fa": "ساختن يک روند صادراتي تکرارپذير از انبارهاي اروپا", "fr": "Construire un flux export repetable depuis les entrepots europeens", "es": "Como crear un flujo exportable repetible desde almacenes UE", "pt": "Como montar um fluxo de exportacao repetivel a partir de armazens da UE", "nl": "Een herhaalbare exportworkflow opzetten vanuit EU-magazijnen", "zh": "从欧盟仓库建立可重复的出口流程"},
        "rfq_vs_listing": {"en": "When to post an RFQ instead of browsing listings", "de": "Wann Sie besser ein RFQ posten statt Angebote zu durchsuchen", "ar": "متى تنشر طلب شراء بدلاً من تصفح العروض", "tr": "Liste bakmak yerine ne zaman RFQ yayinlamalisiniz", "fa": "چه زماني به جاي مرور آگهي ها بايد RFQ ثبت کنيد", "fr": "Quand publier un RFQ au lieu de parcourir les offres", "es": "Cuando publicar un RFQ en lugar de navegar anuncios", "pt": "Quando publicar um RFQ em vez de navegar anuncios", "nl": "Wanneer u beter een RFQ plaatst dan listings te bekijken", "zh": "什么时候应发布询价而不是浏览商品"},
        "loading_plans": {"en": "Loading plans that reduce damage on footwear pallets", "de": "Ladeplane, die Schaden auf Schuhpaletten reduzieren", "ar": "خطط تحميل تقلل التلف في طبليات الأحذية", "tr": "Ayakkabi paletlerinde hasari azaltan yukleme planlari", "fa": "برنامه هاي بارگيري که آسيب پالت کفش را کم مي کند", "fr": "Plans de chargement qui reduisent les dommages sur palettes de chaussures", "es": "Planes de carga que reducen danos en palets de calzado", "pt": "Planos de carregamento que reduzem danos em paletes de calcado", "nl": "Laadplannen die schade op schoenenpallets verminderen", "zh": "减少鞋类托盘损坏的装载方案"},
        "seller_review": {"en": "What sellers should prepare before admin review", "de": "Was Verkaufer vor der Admin-Prufung vorbereiten sollten", "ar": "ما الذي يجب على البائعين تحضيره قبل مراجعة الإدارة", "tr": "Saticilar yonetici incelemesinden once ne hazirlamali", "fa": "فروشندگان پيش از بررسي مدير چه چيزي بايد آماده کنند", "fr": "Ce que les vendeurs doivent preparer avant la revue admin", "es": "Que deben preparar los vendedores antes de la revision admin", "pt": "O que vendedores devem preparar antes da revisao admin", "nl": "Wat verkopers moeten voorbereiden voor de admincontrole", "zh": "卖家在管理员审核前应准备什么"},
        "manifest_format": {"en": "A manifest format buyers actually trust", "de": "Ein Manifest-Format, dem Kaufer wirklich vertrauen", "ar": "صيغة بيان شحن يثق بها المشترون فعلاً", "tr": "Alicilarin gercekten guvendigi bir manifest formati", "fa": "فرمت مانيـفستي که خريداران واقعا به آن اعتماد مي کنند", "fr": "Un format de manifeste auquel les acheteurs font confiance", "es": "Un formato de manifiesto en el que los compradores confian", "pt": "Um formato de manifesto em que compradores realmente confiam", "nl": "Een manifestformaat dat kopers echt vertrouwen", "zh": "买家真正信任的清单格式"},
        "mena_packaging": {"en": "Packaging tips for MENA-bound stocklots", "de": "Verpackungstipps fur Stocklots in Richtung MENA", "ar": "نصائح تغليف للدفعات المتجهة إلى الشرق الأوسط وشمال أفريقيا", "tr": "MENA hedefli partiler icin paketleme ipuclari", "fa": "نکات بسته بندي براي محموله هاي مقصد منا", "fr": "Conseils d'emballage pour des lots a destination MENA", "es": "Consejos de embalaje para lotes con destino MENA", "pt": "Dicas de embalagem para lotes destinados ao MENA", "nl": "Verpakkingstips voor stocklots richting MENA", "zh": "面向中东北非货盘的包装建议"},
    }

    def add_arguments(self, parser):
        parser.add_argument("--seed", type=int, default=20260403, help="Random seed for reproducible data.")
        parser.add_argument("--reset", action="store_true", help="Delete previously generated seed data first.")

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(options["seed"])
        if options["reset"]:
            self._reset_seed_data()

        categories = self._ensure_categories()
        buyers, sellers = self._create_users()
        companies = self._create_companies(sellers)
        self._create_buyer_verifications(buyers)
        self._create_seller_verifications(sellers, companies)
        stocklots = self._create_stocklots(companies, categories)
        rfqs, conversations = self._create_rfqs_and_conversations(buyers, companies, categories)
        inquiries = self._create_inquiries(buyers, stocklots)
        articles = self._create_articles()
        self._create_support_messages(buyers, sellers)
        self._create_activity(buyers, sellers, stocklots, rfqs, articles)
        self._create_deals(inquiries, conversations)

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
        self.stdout.write(f"Users: {len(buyers) + len(sellers)}")
        self.stdout.write(f"Companies: {len(companies)}")
        self.stdout.write(f"Listings: {len(stocklots)}")
        self.stdout.write(f"RFQs: {len(rfqs)}")
        self.stdout.write(f"Blog articles: {len(articles)}")
        self.stdout.write(f"Support messages: {SupportMessage.objects.filter(email__endswith=self.SEED_DOMAIN).count()}")
        self.stdout.write(f"CMS missing fields: {self._cms_missing_count()}")
        self.stdout.write(f"Dev password for seeded accounts: {self.DEV_PASSWORD}")
        self.stdout.write(f"Example buyer login: {buyers[0].email}")
        self.stdout.write(f"Example seller login: {sellers[0].email}")

    def _reset_seed_data(self):
        ArticleLike.objects.filter(user__email__endswith=self.SEED_DOMAIN).delete()
        Article.objects.filter(slug__startswith="seed-").delete()
        SupportMessage.objects.filter(Q(email__endswith=self.SEED_DOMAIN) | Q(user__email__endswith=self.SEED_DOMAIN)).delete()
        Notification.objects.filter(Q(recipient__email__endswith=self.SEED_DOMAIN) | Q(actor__email__endswith=self.SEED_DOMAIN)).delete()
        DealHistory.objects.filter(Q(deal__buyer__email__endswith=self.SEED_DOMAIN) | Q(deal__seller_user__email__endswith=self.SEED_DOMAIN)).delete()
        DealTrigger.objects.filter(Q(buyer__email__endswith=self.SEED_DOMAIN) | Q(seller_user__email__endswith=self.SEED_DOMAIN)).delete()
        RFQMessage.objects.filter(Q(conversation__buyer__email__endswith=self.SEED_DOMAIN) | Q(sender_user__email__endswith=self.SEED_DOMAIN)).delete()
        RFQConversation.objects.filter(Q(buyer__email__endswith=self.SEED_DOMAIN) | Q(seller_user__email__endswith=self.SEED_DOMAIN)).delete()
        RFQFavorite.objects.filter(Q(user__email__endswith=self.SEED_DOMAIN) | Q(rfq__buyer__email__endswith=self.SEED_DOMAIN)).delete()
        RFQ.objects.filter(buyer__email__endswith=self.SEED_DOMAIN).delete()
        InquiryReply.objects.filter(Q(inquiry__buyer__email__endswith=self.SEED_DOMAIN) | Q(sender_user__email__endswith=self.SEED_DOMAIN)).delete()
        Inquiry.objects.filter(Q(buyer__email__endswith=self.SEED_DOMAIN) | Q(stocklot__company__owner__email__endswith=self.SEED_DOMAIN)).delete()
        Favorite.objects.filter(Q(user__email__endswith=self.SEED_DOMAIN) | Q(stocklot__company__owner__email__endswith=self.SEED_DOMAIN)).delete()
        Stocklot.objects.filter(company__owner__email__endswith=self.SEED_DOMAIN).delete()
        SellerVerificationRequest.objects.filter(user__email__endswith=self.SEED_DOMAIN).delete()
        BuyerVerificationRequest.objects.filter(user__email__endswith=self.SEED_DOMAIN).delete()
        Company.objects.filter(owner__email__endswith=self.SEED_DOMAIN).delete()
        User.objects.filter(email__endswith=self.SEED_DOMAIN).delete()

    def _ensure_categories(self):
        categories = {}
        for root_slug, (root_name, children) in self.CATEGORY_TREE.items():
            root, _ = Category.objects.get_or_create(
                slug=root_slug,
                defaults={"name": root_name, "is_active": True},
            )
            categories[root_slug] = root
            for child_name in children:
                child_slug = f"{root_slug}-{child_name.lower().replace(' ', '-')}"
                child, _ = Category.objects.get_or_create(
                    slug=child_slug,
                    defaults={"name": child_name, "parent": root, "is_active": True},
                )
                categories[child_slug] = child
        return categories

    def _create_users(self):
        buyers = []
        sellers = []
        for index, (name, country, city, language) in enumerate(self.BUYER_PROFILES):
            buyers.append(self._upsert_user("buyer", index, name, language, country, city))
        for index, (name, country, city, language) in enumerate(self.SELLER_PROFILES):
            sellers.append(self._upsert_user("seller", index, name, language, country, city))
        return buyers, sellers

    def _upsert_user(self, role, index, name, language, country, city):
        local = name.lower().replace(" ", ".")
        email = f"{local}.{role}@{self.SEED_DOMAIN}"
        user, _ = User.objects.get_or_create(email=email)
        user.full_name = "" if index % 6 == 0 else name
        user.preferred_language = language
        user.email_verified = index % 5 != 0
        user.is_active = index % 9 != 0
        user.is_buyer = role == "buyer"
        user.is_seller = role == "seller"
        user.is_verified_user = index % 4 == 0
        user.identity_status = User.IdentityStatus.REVEALED if index % 3 == 0 else User.IdentityStatus.HIDDEN
        user.set_password(self.DEV_PASSWORD)
        user.save()
        return user

    def _create_companies(self, sellers):
        companies = []
        for seller, (name, country, city, description) in zip(sellers[:14], self.COMPANY_PROFILES):
            company, _ = Company.objects.get_or_create(owner=seller)
            company.name = name
            company.legal_name = name
            company.description = description
            company.phone = "+49 1575 4967414"
            company.email = f"contact@{name.lower().split()[0]}.{self.SEED_DOMAIN}"
            company.country = country
            company.city = city
            company.address = f"{city} Trade District 14"
            company.website = f"https://{name.lower().split()[0]}.{self.SEED_DOMAIN}"
            company.registration_number = f"SEED-REG-{seller.id:04d}"
            company.vat_number = f"SEEDVAT{seller.id:06d}"
            company.identity_status = Company.IdentityStatus.REVEALED if len(companies) % 2 == 0 else Company.IdentityStatus.HIDDEN
            company.save()
            companies.append(company)
        return companies

    def _create_buyer_verifications(self, buyers):
        statuses = [
            BuyerVerificationRequest.Status.VERIFIED,
            BuyerVerificationRequest.Status.PENDING,
            BuyerVerificationRequest.Status.REJECTED,
        ]
        for index, buyer in enumerate(buyers[:12]):
            request, _ = BuyerVerificationRequest.objects.get_or_create(user=buyer)
            request.legal_full_name = buyer.full_name or f"Buyer {buyer.id}"
            request.phone_number = "+49 30 000000"
            request.country = self.BUYER_PROFILES[index][1]
            request.city = self.BUYER_PROFILES[index][2]
            request.address = f"{request.city} Business Center {index + 1}"
            request.identity_document_type = BuyerVerificationRequest.DocumentType.PASSPORT
            request.identity_document.save(f"buyer-id-{buyer.id}.pdf", ContentFile(self.PDF_BYTES), save=False)
            request.selfie_document.save(f"buyer-selfie-{buyer.id}.png", ContentFile(self.IMAGE_BYTES), save=False)
            request.status = statuses[index % len(statuses)]
            request.review_notes = "Seeded verification case for admin review."
            request.save()
            if request.status == BuyerVerificationRequest.Status.VERIFIED:
                buyer.is_verified_user = True
                buyer.save(update_fields=["is_verified_user"])

    def _create_seller_verifications(self, sellers, companies):
        approved_owner_ids = {company.owner_id for company in companies}
        for index, seller in enumerate(sellers):
            request, _ = SellerVerificationRequest.objects.get_or_create(user=seller)
            request.company_name = companies[index].name if index < len(companies) else f"Pending Seller {index + 1}"
            request.contact_person_name = seller.full_name or f"Seller {seller.id}"
            request.phone_number = "+49 40 100000"
            request.company_email = seller.email
            request.company_address = f"{self.SELLER_PROFILES[index][2]} Export Zone"
            request.country = self.SELLER_PROFILES[index][1]
            request.city = self.SELLER_PROFILES[index][2]
            request.business_type = "Wholesale"
            request.business_description = "Seeded seller verification workflow with realistic B2B trade information."
            request.registration_number = f"SREG-{seller.id:04d}"
            request.vat_number = f"SVAT{seller.id:06d}"
            request.supporting_document.save(f"seller-doc-{seller.id}.pdf", ContentFile(self.PDF_BYTES), save=False)
            if seller.id in approved_owner_ids:
                request.status = SellerVerificationRequest.Status.APPROVED
            elif index % 2 == 0:
                request.status = SellerVerificationRequest.Status.PENDING
            else:
                request.status = SellerVerificationRequest.Status.REJECTED
            request.review_notes = "Seeded seller verification workflow."
            request.save()

    def _create_stocklots(self, companies, categories):
        category_keys = [
            "electronics-mobile-accessories",
            "electronics-mixed-electronics",
            "apparel-shoes",
            "home-small-appliances",
            "home-home-textiles",
            "fmcg-household-cleaners",
            "machinery-construction-tools",
            "machinery-sewing-machines",
            "apparel-kids-apparel",
            "home-furniture",
            "fmcg-packaged-grocery",
            "electronics-smart-home",
        ]
        item_codes = list(self.ITEM_TRANSLATIONS.keys())
        language_cycle = ["en", "de", "ar", "fr", "tr", "fa", "es", "pt", "nl", "zh"]
        profiles = ["original_only", "en_de_ar", "original_plus_en", "full"]
        stocklots = []

        for index in range(52):
            company = companies[index % len(companies)]
            original_language = language_cycle[index % len(language_cycle)]
            item_code = item_codes[index % len(item_codes)]
            quantity = random.choice([120, 240, 480, 900, 1600, 3200])
            unit_type = random.choice(
                [
                    Stocklot.UnitType.PIECE,
                    Stocklot.UnitType.PALLET,
                    Stocklot.UnitType.CARTON,
                    Stocklot.UnitType.SET,
                    Stocklot.UnitType.LOT,
                ]
            )
            stocklot, _ = Stocklot.objects.update_or_create(
                slug=f"seed-{index + 1}-{item_code}",
                defaults={
                    "company": company,
                    "title": self._listing_title(item_code, original_language, index + 1),
                    "description": self._listing_description(item_code, original_language, company.city, company.country, quantity, unit_type),
                    "original_language": original_language,
                    "category": categories[category_keys[index % len(category_keys)]],
                    "condition": random.choice(list(Stocklot.Condition.values)),
                    "quantity": quantity,
                    "moq": max(1, int(quantity / random.choice([8, 10, 12]))),
                    "unit_type": unit_type,
                    "price": Decimal(str(random.choice([1.9, 4.5, 8.75, 16, 42, 95, 220, 1800]))),
                    "currency": random.choice([Stocklot.Currency.EUR, Stocklot.Currency.USD]),
                    "location_country": company.country,
                    "location_city": company.city,
                    "status": Stocklot.Status.APPROVED if index % 5 != 0 else Stocklot.Status.PENDING_REVIEW,
                    "is_admin_verified": index % 3 == 0,
                    "is_active": index % 7 != 0,
                },
            )
            self._apply_translations(stocklot, item_code, company.city, company.country, quantity, unit_type, profiles[index % len(profiles)], content_type="listing")
            stocklot.save()
            self._attach_stocklot_media(stocklot, index)
            stocklots.append(stocklot)
        return stocklots

    def _create_rfqs_and_conversations(self, buyers, companies, categories):
        rfqs = []
        conversations = []
        item_codes = list(self.ITEM_TRANSLATIONS.keys())
        language_cycle = ["ar", "de", "en", "fr", "tr", "fa", "en", "de"]
        profiles = ["original_only", "original_plus_en", "en_de_ar", "full"]

        for index in range(28):
            buyer = buyers[index % len(buyers)]
            original_language = language_cycle[index % len(language_cycle)]
            item_code = item_codes[(index + 3) % len(item_codes)]
            quantity = random.choice([200, 450, 900, 1500, 3000, 12000])
            unit_type = random.choice(
                [
                    Stocklot.UnitType.PIECE,
                    Stocklot.UnitType.PALLET,
                    Stocklot.UnitType.CARTON,
                    Stocklot.UnitType.SET,
                    Stocklot.UnitType.LOT,
                ]
            )
            rfq, _ = RFQ.objects.update_or_create(
                buyer=buyer,
                title=f"{self._rfq_title(item_code, original_language)} #{index + 1}",
                defaults={
                    "description": self._rfq_description(item_code, original_language, quantity, unit_type, self.BUYER_PROFILES[index % len(self.BUYER_PROFILES)][2], self.BUYER_PROFILES[index % len(self.BUYER_PROFILES)][1]),
                    "original_language": original_language,
                    "category": random.choice(list(categories.values())),
                    "quantity": Decimal(str(quantity)),
                    "unit_type": unit_type,
                    "target_price": Decimal(str(random.choice([2.2, 6.8, 15, 38, 110, 2200]))),
                    "currency": random.choice([Stocklot.Currency.EUR, Stocklot.Currency.USD]),
                    "location_country": self.BUYER_PROFILES[index % len(self.BUYER_PROFILES)][1],
                    "location_city": self.BUYER_PROFILES[index % len(self.BUYER_PROFILES)][2],
                    "moderation_status": RFQ.ModerationStatus.APPROVED if index % 4 != 0 else RFQ.ModerationStatus.PENDING_REVIEW,
                    "status": RFQ.Status.OPEN if index % 6 != 0 else RFQ.Status.CLOSED,
                },
            )
            self._apply_translations(rfq, item_code, rfq.location_city, rfq.location_country, quantity, unit_type, profiles[index % len(profiles)], content_type="rfq")
            rfq.save()
            rfqs.append(rfq)

            if index < 16:
                seller_company = companies[index % len(companies)]
                conversation, _ = RFQConversation.objects.get_or_create(
                    rfq=rfq,
                    buyer=buyer,
                    seller_company=seller_company,
                    seller_user=seller_company.owner,
                )
                RFQMessage.objects.get_or_create(
                    conversation=conversation,
                    sender_user=seller_company.owner,
                    sender_company=seller_company,
                    message="We can supply this volume with a phased loading plan and an updated manifest.",
                    defaults={
                        "price": rfq.target_price or Decimal("0.00"),
                        "currency": rfq.currency,
                        "moderation_status": RFQMessage.ModerationStatus.APPROVED,
                    },
                )
                RFQMessage.objects.get_or_create(
                    conversation=conversation,
                    sender_user=buyer,
                    sender_company=None,
                    message="Please confirm lead time, packing details, and whether inspection can be arranged.",
                    defaults={"moderation_status": RFQMessage.ModerationStatus.APPROVED},
                )
                conversations.append(conversation)
        return rfqs, conversations

    def _create_inquiries(self, buyers, stocklots):
        inquiries = []
        approved_stocklots = [stocklot for stocklot in stocklots if stocklot.status == Stocklot.Status.APPROVED]
        for index, stocklot in enumerate(approved_stocklots[:24]):
            buyer = buyers[index % len(buyers)]
            if stocklot.company.owner_id == buyer.id:
                continue
            inquiry, _ = Inquiry.objects.get_or_create(
                stocklot=stocklot,
                buyer=buyer,
                seller_company=stocklot.company,
                defaults={
                    "subject": f"Availability check for {stocklot.title}",
                    "message": "Please share current availability, pallet mix, and whether a fresh manifest is ready.",
                    "status": Inquiry.Status.REPLIED if index % 3 == 0 else Inquiry.Status.APPROVED,
                    "moderation_status": Inquiry.ModerationStatus.APPROVED if index % 4 != 0 else Inquiry.ModerationStatus.PENDING_REVIEW,
                },
            )
            if index % 2 == 0:
                InquiryReply.objects.get_or_create(
                    inquiry=inquiry,
                    sender_user=stocklot.company.owner,
                    sender_company=stocklot.company,
                    message="Current stock is available. We can share the manifest and arrange loading within five working days.",
                    defaults={"moderation_status": InquiryReply.ModerationStatus.APPROVED},
                )
            inquiries.append(inquiry)
        return inquiries

    def _create_articles(self):
        articles = []
        topics = list(self.ARTICLE_TOPICS.keys())
        profiles = [
            ("en", "en_only"),
            ("en", "en_de"),
            ("en", "en_ar"),
            ("de", "en_de"),
            ("ar", "en_ar"),
            ("en", "full"),
            ("en", "en_only"),
            ("de", "en_de"),
            ("ar", "en_ar"),
            ("en", "full"),
            ("en", "en_only"),
            ("fr", "original_plus_en"),
            ("tr", "original_plus_en"),
            ("fa", "original_plus_en"),
        ]
        kinds = list(Article.Kind.values)
        for index, (original_language, profile) in enumerate(profiles):
            topic_code = topics[index % len(topics)]
            article, _ = Article.objects.update_or_create(
                slug=f"seed-{index + 1}-{topic_code}",
                defaults={
                    "original_language": original_language,
                    "kind": kinds[index % len(kinds)],
                    "title": self.ARTICLE_TOPICS[topic_code][original_language],
                    "body": self._article_body(topic_code, original_language),
                    "status": Article.Status.PUBLISHED if index < 12 else Article.Status.DRAFT,
                    "published_at": timezone.now() - timedelta(days=30 - index) if index < 12 else None,
                    "view_count": 40 + (index * 17),
                },
            )
            self._apply_article_translations(article, topic_code, profile)
            article.featured_image.save(f"article-{index + 1}.png", ContentFile(self.IMAGE_BYTES), save=False)
            article.save()
            articles.append(article)
        return articles

    def _create_support_messages(self, buyers, sellers):
        sample_users = buyers[:6] + sellers[:6]
        subjects = [
            "Need help understanding seller verification",
            "Question about why my listing is still pending",
            "Cannot access the RFQ conversation thread",
            "Need clarification on buyer verification documents",
            "Support request for saved items not updating",
            "Need help with contact form follow-up",
        ]
        for index, user in enumerate(sample_users):
            message, _ = SupportMessage.objects.get_or_create(
                email=user.email,
                subject=subjects[index % len(subjects)],
                defaults={
                    "user": user,
                    "name": user.full_name or f"Seed User {user.id}",
                    "phone": "+49 1575 4967414",
                    "message": "This is a seeded support case used to test the support inbox, admin workflow, and contact UX.",
                    "status": SupportMessage.Status.NEW if index % 3 else SupportMessage.Status.HANDLED,
                },
            )
            message.user = user
            message.name = user.full_name or f"Seed User {user.id}"
            message.status = SupportMessage.Status.NEW if index % 3 else SupportMessage.Status.HANDLED
            message.save()

    def _create_activity(self, buyers, sellers, stocklots, rfqs, articles):
        active_users = [user for user in buyers + sellers if user.is_active]
        for index, stocklot in enumerate(stocklots[:36]):
            user = active_users[index % len(active_users)]
            if stocklot.company.owner_id != user.id:
                Favorite.objects.get_or_create(user=user, stocklot=stocklot)

        for index, rfq in enumerate(rfqs[:20]):
            user = active_users[(index + 4) % len(active_users)]
            if rfq.buyer_id != user.id:
                RFQFavorite.objects.get_or_create(user=user, rfq=rfq)

        for index, article in enumerate(articles[:12]):
            for liker in active_users[index:index + 5]:
                ArticleLike.objects.get_or_create(user=liker, article=article)

        note_types = list(Notification.Type.values)
        for index, user in enumerate(active_users[:24]):
            Notification.objects.get_or_create(
                recipient=user,
                title=f"Seed activity update {index + 1}",
                body="You have seeded platform activity for dashboard, inbox, and notification testing.",
                defaults={
                    "notification_type": note_types[index % len(note_types)],
                    "url": "/dashboard/",
                    "is_read": index % 3 == 0,
                },
            )

    def _create_deals(self, inquiries, conversations):
        statuses = [
            (DealTrigger.Status.PENDING, DealTrigger.Progress.NOT_STARTED),
            (DealTrigger.Status.MUTUAL, DealTrigger.Progress.NOT_STARTED),
            (DealTrigger.Status.APPROVED, DealTrigger.Progress.IN_PROGRESS),
            (DealTrigger.Status.APPROVED, DealTrigger.Progress.READY),
            (DealTrigger.Status.APPROVED, DealTrigger.Progress.COMPLETED),
            (DealTrigger.Status.REJECTED, DealTrigger.Progress.NOT_STARTED),
        ]
        for index, inquiry in enumerate(inquiries[:10]):
            status, progress = statuses[index % len(statuses)]
            deal, _ = DealTrigger.objects.get_or_create(
                inquiry=inquiry,
                deal_type=DealTrigger.DealType.INQUIRY,
                defaults={
                    "buyer": inquiry.buyer,
                    "seller_user": inquiry.seller_company.owner,
                    "seller_company": inquiry.seller_company,
                    "buyer_accepted": index % 2 == 0,
                    "seller_accepted": index % 3 != 0,
                    "buyer_identity_revealed": index % 2 == 0,
                    "seller_identity_revealed": index % 4 == 0,
                    "status": status,
                    "progress_status": progress,
                },
            )
            DealHistory.objects.get_or_create(
                deal=deal,
                action="seeded_state",
                note=f"Seeded inquiry deal with status {deal.status} and progress {deal.progress_status}.",
            )

        for index, conversation in enumerate(conversations[:8]):
            status, progress = statuses[(index + 2) % len(statuses)]
            deal, _ = DealTrigger.objects.get_or_create(
                rfq_conversation=conversation,
                deal_type=DealTrigger.DealType.RFQ,
                defaults={
                    "buyer": conversation.buyer,
                    "seller_user": conversation.seller_user,
                    "seller_company": conversation.seller_company,
                    "buyer_accepted": True,
                    "seller_accepted": index % 2 == 0,
                    "buyer_identity_revealed": index % 2 == 0,
                    "seller_identity_revealed": index % 3 == 0,
                    "status": status,
                    "progress_status": progress,
                },
            )
            DealHistory.objects.get_or_create(
                deal=deal,
                action="seeded_state",
                note=f"Seeded RFQ deal with status {deal.status} and progress {deal.progress_status}.",
            )

    def _apply_translations(self, obj, item_code, city, country, quantity, unit_type, profile, content_type="listing"):
        for language in self._profile_languages(profile, obj.original_language):
            if content_type == "listing":
                setattr(obj, f"title_{language}", self._listing_title(item_code, language, random.randint(11, 98)))
                setattr(obj, f"description_{language}", self._listing_description(item_code, language, city, country, quantity, unit_type))
            else:
                setattr(obj, f"title_{language}", self._rfq_title(item_code, language))
                setattr(obj, f"description_{language}", self._rfq_description(item_code, language, quantity, unit_type, city, country))

    def _apply_article_translations(self, article, topic_code, profile):
        for language in self._profile_languages(profile, article.original_language):
            setattr(article, f"title_{language}", self.ARTICLE_TOPICS[topic_code][language])
            setattr(article, f"body_{language}", self._article_body(topic_code, language))

    def _profile_languages(self, profile, original_language):
        if profile == "original_only":
            languages = []
        elif profile == "en_de_ar":
            languages = ["en", "de", "ar"]
        elif profile == "original_plus_en":
            languages = ["en"]
        elif profile == "en_only":
            languages = ["en"]
        elif profile == "en_de":
            languages = ["en", "de"]
        elif profile == "en_ar":
            languages = ["en", "ar"]
        elif profile == "full":
            languages = self.LANGUAGES
        else:
            languages = []
        return [language for language in languages if language != original_language]

    def _listing_title(self, item_code, language, batch_number):
        item = self.ITEM_TRANSLATIONS[item_code][language]
        templates = {
            "en": f"{item} - batch {batch_number}",
            "de": f"{item} - Partie {batch_number}",
            "ar": f"{item} - دفعة {batch_number}",
            "tr": f"{item} - parti {batch_number}",
            "fa": f"{item} - محموله {batch_number}",
            "fr": f"{item} - lot {batch_number}",
            "es": f"{item} - lote {batch_number}",
            "pt": f"{item} - lote {batch_number}",
            "nl": f"{item} - partij {batch_number}",
            "zh": f"{item} - 批次{batch_number}",
        }
        return templates[language]

    def _listing_description(self, item_code, language, city, country, quantity, unit_type):
        item = self.ITEM_TRANSLATIONS[item_code][language]
        unit = self._unit_label(unit_type, language)
        templates = {
            "en": f"{item.capitalize()} available ex-warehouse in {city}, {country}. Approx. {quantity} {unit} ready for wholesale resale. Manifest, packing notes, and loading window can be shared on request.",
            "de": f"{item.capitalize()} ist ab Lager in {city}, {country} verfugbar. Rund {quantity} {unit} stehen fur den Grosshandel bereit. Manifest, Packdetails und Ladefenster sind auf Anfrage verfugbar.",
            "ar": f"{item} متوفر من مستودع {city} في {country}. الكمية التقريبية {quantity} {unit}. يمكن مشاركة البيان وقائمة التعبئة وخطة التحميل عند الطلب.",
            "tr": f"{item.capitalize()} {city}, {country} deposundan hazir. Yaklasik {quantity} {unit} toptan satis icin uygun. Manifesto, paketleme notlari ve yukleme plani talep uzerine paylasilir.",
            "fa": f"{item} از انبار {city} در {country} آماده است. حدود {quantity} {unit} براي فروش عمده موجود است. مانيـفست، جزئيات بسته بندي و زمان بارگيري در صورت درخواست ارائه مي شود.",
            "fr": f"{item.capitalize()} disponible au depart de l'entrepot de {city}, {country}. Environ {quantity} {unit} prets pour la revente de gros. Le manifeste et le planning de chargement sont disponibles sur demande.",
            "es": f"{item.capitalize()} disponible desde almacen en {city}, {country}. Aproximadamente {quantity} {unit} listos para reventa mayorista. Manifiesto y plan de carga disponibles bajo solicitud.",
            "pt": f"{item.capitalize()} disponivel a partir do armazem em {city}, {country}. Cerca de {quantity} {unit} prontos para revenda no atacado. Manifesto e plano de carga disponiveis sob solicitacao.",
            "nl": f"{item.capitalize()} beschikbaar uit magazijn in {city}, {country}. Ongeveer {quantity} {unit} klaar voor groothandel. Manifest, verpakkingsinfo en laadvenster zijn op aanvraag beschikbaar.",
            "zh": f"{item} 可从 {country}{city} 仓库发货，约有 {quantity}{unit} 可供批发转售。可按需提供清单、包装说明和装柜时间。",
        }
        return templates[language]

    def _rfq_title(self, item_code, language):
        item = self.ITEM_TRANSLATIONS[item_code][language]
        templates = {
            "en": f"Looking for {item}",
            "de": f"Gesucht: {item}",
            "ar": f"مطلوب {item}",
            "tr": f"{item} araniyor",
            "fa": f"درخواست {item}",
            "fr": f"Recherche de {item}",
            "es": f"Buscando {item}",
            "pt": f"Buscando {item}",
            "nl": f"Gezocht: {item}",
            "zh": f"求购{item}",
        }
        return templates[language]

    def _rfq_description(self, item_code, language, quantity, unit_type, city, country):
        item = self.ITEM_TRANSLATIONS[item_code][language]
        unit = self._unit_label(unit_type, language)
        templates = {
            "en": f"Buyer sourcing {item} for resale demand in {city}, {country}. Required volume is about {quantity} {unit}. Suppliers should be ready to confirm packing details, lead time, and inspection options.",
            "de": f"Kaufer sucht {item} fur den Weiterverkauf in {city}, {country}. Benotigt werden etwa {quantity} {unit}. Lieferanten sollen Packdetails, Vorlaufzeit und Inspektionsmoglichkeiten bestatigen.",
            "ar": f"المشتري يبحث عن {item} لتغطية طلب إعادة البيع في {city}، {country}. الحجم المطلوب حوالي {quantity} {unit}. يجب على الموردين توضيح التعبئة ووقت التجهيز وخيارات الفحص.",
            "tr": f"Alici {city}, {country} icin yeniden satis talebine yonelik {item} ariyor. Hedef hacim yaklasik {quantity} {unit}. Tedarikciler paketleme, termin ve kontrol seceneklerini netlestirmelidir.",
            "fa": f"خريدار براي تقاضاي فروش مجدد در {city}، {country} به دنبال {item} است. حجم مورد نياز حدود {quantity} {unit} است. تامين کنندگان بايد بسته بندي، زمان تحويل و امکان بازرسي را مشخص کنند.",
            "fr": f"L'acheteur recherche {item} pour une demande de revente a {city}, {country}. Le volume vise est d'environ {quantity} {unit}. Les fournisseurs doivent confirmer le conditionnement, le delai et l'inspection.",
            "es": f"El comprador busca {item} para demanda de reventa en {city}, {country}. El volumen requerido es de aproximadamente {quantity} {unit}. Los proveedores deben confirmar empaque, plazo e inspeccion.",
            "pt": f"O comprador procura {item} para revenda em {city}, {country}. O volume esperado e de cerca de {quantity} {unit}. Fornecedores devem confirmar embalagem, prazo e inspecao.",
            "nl": f"Koper zoekt {item} voor wederverkoop in {city}, {country}. Gevraagde hoeveelheid is ongeveer {quantity} {unit}. Leveranciers moeten verpakking, doorlooptijd en inspectieopties bevestigen.",
            "zh": f"买家在 {country}{city} 为转售需求采购{item}，需求量约为 {quantity}{unit}。供应商需确认包装细节、交期和验货安排。",
        }
        return templates[language]

    def _article_body(self, topic_code, language):
        topic = self.ARTICLE_TOPICS[topic_code][language]
        templates = {
            "en": f"{topic} matters because the fastest deals usually come from well-prepared information, not just low price. This article explains how wholesale teams can improve manifests, loading plans, and buyer communication before the lot goes public. It is written for cross-border trade between EU stock holders and MENA demand teams.",
            "de": f"{topic} ist wichtig, weil die schnellsten Deals aus guter Vorbereitung entstehen und nicht nur aus dem niedrigsten Preis. Dieser Beitrag zeigt, wie Grosshandelsteams Manifest, Ladeplan und Kommunikation verbessern konnen. Er richtet sich an den Handel zwischen EU-Bestanden und MENA-Nachfrage.",
            "ar": f"{topic} مهم لأن الصفقات الأسرع تأتي من معلومات مرتبة جيدًا وليس من السعر المنخفض فقط. يشرح هذا المقال كيف يمكن لفرق الجملة تحسين البيان وخطة التحميل والتواصل قبل نشر العرض. النص موجه للتجارة بين مخزون الاتحاد الأوروبي وطلب منطقة الشرق الأوسط وشمال أفريقيا.",
            "tr": f"{topic} onemlidir cunku en hizli anlasmalar sadece dusuk fiyatla degil, iyi hazirlanmis bilgiyle gelir. Bu yazi toptan ekiplerin manifestoyu, yukleme planini ve alici iletisimini nasil iyilestirebilecegini anlatir. Avrupa stoklari ile MENA talebi arasindaki ticaret icin yazilmistir.",
            "fa": f"{topic} مهم است چون سريع ترين معاملات فقط با قيمت پايين شکل نمي گيرد بلکه با اطلاعات منظم ايجاد مي شود. اين مقاله توضيح مي دهد که تيم هاي عمده فروشي چگونه مانيـفست، برنامه بارگيري و ارتباط با خريدار را بهتر کنند. متن براي تجارت ميان انبارهاي اروپايي و تقاضاي منطقه منا نوشته شده است.",
            "fr": f"{topic} est important car les transactions les plus rapides viennent d'une bonne preparation et pas seulement d'un prix bas. Cet article explique comment ameliorer manifeste, plan de chargement et communication acheteur. Il vise le commerce entre stocks europeens et demande MENA.",
            "es": f"{topic} importa porque los negocios mas rapidos nacen de informacion bien preparada y no solo de un precio bajo. Este articulo explica como mejorar manifiesto, plan de carga y comunicacion con compradores. Esta pensado para comercio entre stock europeo y demanda MENA.",
            "pt": f"{topic} e importante porque os negocios mais rapidos surgem de informacao bem preparada e nao apenas de preco baixo. Este artigo mostra como equipes atacadistas podem melhorar manifesto, plano de carga e comunicacao com compradores. O foco e o comercio entre estoque europeu e demanda MENA.",
            "nl": f"{topic} is belangrijk omdat de snelste deals voortkomen uit goede voorbereiding en niet alleen uit een lage prijs. Dit artikel laat zien hoe groothandelsteams manifest, laadplan en communicatie kunnen verbeteren. Het is gericht op handel tussen EU-voorraad en MENA-vraag.",
            "zh": f"{topic} 很重要，因为更快的成交通常来自准备充分的信息，而不仅仅是低价。本文说明批发团队如何在发布货盘前改进清单、装载计划和买家沟通，适用于欧盟库存与中东北非需求之间的跨境贸易。",
        }
        return templates[language]

    def _unit_label(self, unit_type, language):
        unit_map = {
            Stocklot.UnitType.PIECE: {"en": "pieces", "de": "Stuck", "ar": "قطعة", "tr": "adet", "fa": "عدد", "fr": "pieces", "es": "piezas", "pt": "pecas", "nl": "stuks", "zh": "件"},
            Stocklot.UnitType.PALLET: {"en": "pallets", "de": "Paletten", "ar": "طبليات", "tr": "palet", "fa": "پالت", "fr": "palettes", "es": "palets", "pt": "paletes", "nl": "pallets", "zh": "托盘"},
            Stocklot.UnitType.CARTON: {"en": "cartons", "de": "Kartons", "ar": "كراتين", "tr": "koli", "fa": "کارتن", "fr": "cartons", "es": "cajas", "pt": "caixas", "nl": "dozen", "zh": "箱"},
            Stocklot.UnitType.SET: {"en": "sets", "de": "Sets", "ar": "مجموعات", "tr": "set", "fa": "ست", "fr": "sets", "es": "sets", "pt": "conjuntos", "nl": "sets", "zh": "套"},
            Stocklot.UnitType.LOT: {"en": "lots", "de": "Lose", "ar": "دفعات", "tr": "lot", "fa": "لات", "fr": "lots", "es": "lotes", "pt": "lotes", "nl": "partijen", "zh": "批"},
        }
        return unit_map.get(unit_type, unit_map[Stocklot.UnitType.PIECE])[language]

    def _attach_stocklot_media(self, stocklot, index):
        if stocklot.images.count() == 0:
            StocklotImage.objects.create(
                stocklot=stocklot,
                file=ContentFile(self.IMAGE_BYTES, name=f"{stocklot.slug}-cover.png"),
            )
        if index % 3 == 0 and stocklot.documents.count() == 0:
            StocklotDocument.objects.create(
                stocklot=stocklot,
                file=ContentFile(self.CSV_BYTES, name=f"{stocklot.slug}-manifest.csv"),
                doc_type=StocklotDocument.DocType.EXCEL,
            )
            StocklotDocument.objects.create(
                stocklot=stocklot,
                file=ContentFile(self.PDF_BYTES, name=f"{stocklot.slug}-spec.pdf"),
                doc_type=StocklotDocument.DocType.PDF,
            )

    def _cms_missing_count(self):
        fields = ["text_en", "text_de", "text_ar", "text_tr", "text_fa", "text_fr", "text_es", "text_pt", "text_nl", "text_zh"]
        missing = 0
        for block in CMSBlock.objects.all():
            for field in fields:
                if not getattr(block, field):
                    missing += 1
        return missing
