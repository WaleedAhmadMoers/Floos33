from django.db import migrations


LANGUAGE_FIELDS = (
    "text_de",
    "text_ar",
    "text_tr",
    "text_fa",
    "text_fr",
    "text_es",
    "text_pt",
    "text_nl",
    "text_zh",
)


def t(de, ar, tr, fa, fr, es, pt, nl, zh):
    return dict(zip(LANGUAGE_FIELDS, (de, ar, tr, fa, fr, es, pt, nl, zh)))


CMS_TRANSLATIONS = {
    "footer.about_label": t("Über uns", "حول", "Hakkında", "درباره", "À propos", "Acerca de", "Sobre", "Over", "关于"),
    "footer.about_text": t(
        "Ein B2B-Marktplatz zum Durchsuchen von Stocklots, Veröffentlichen von RFQs und Voranbringen von Deals mit mehr Vertrauen und Struktur.",
        "منصة B2B لتصفح المخزونات ونشر طلبات الشراء ودفع الصفقات إلى الأمام بثقة وهيكل أفضل.",
        "Stock partilerini gezmek, RFQ yayinlamak ve anlasmalari daha fazla guven ve yapiyla ilerletmek icin bir B2B pazaryeri.",
        "یک بازار B2B برای مرور استاک لات ها، ثبت RFQ و پیشبرد معاملات با اعتماد و ساختار بیشتر.",
        "Une place de marche B2B pour parcourir des lots de stock, publier des RFQ et faire avancer les transactions avec plus de confiance et de structure.",
        "Un marketplace B2B para explorar lotes de stock, publicar RFQ y avanzar operaciones con mas confianza y estructura.",
        "Um marketplace B2B para navegar por lotes de stock, publicar RFQs e fazer avancar negociacoes com mais confianca e estrutura.",
        "Een B2B-marktplaats om stocklots te bekijken, RFQ's te plaatsen en deals met meer vertrouwen en structuur vooruit te helpen.",
        "一个用于浏览尾货批次、发布 RFQ 并在更强信任与结构下推进交易的 B2B 市场平台。",
    ),
    "footer.account_about": t("Über floos33", "حول floos33", "floos33 Hakkında", "درباره floos33", "À propos de floos33", "Acerca de floos33", "Sobre a floos33", "Over floos33", "关于 floos33"),
    "footer.account_profile": t("Profil", "الملف الشخصي", "Profil", "پروفایل", "Profil", "Perfil", "Perfil", "Profiel", "个人资料"),
    "footer.account_saved": t("Gespeichert", "المحفوظات", "Kaydedilenler", "ذخیره شده", "Enregistres", "Guardados", "Guardados", "Opgeslagen", "已保存"),
    "footer.account_settings": t("Einstellungen", "الإعدادات", "Ayarlar", "تنظیمات", "Parametres", "Configuracion", "Definicoes", "Instellingen", "设置"),
    "footer.account_title": t("Konto", "الحساب", "Hesap", "حساب", "Compte", "Cuenta", "Conta", "Account", "账户"),
    "footer.contact_label": t("Kontakt", "اتصال", "Iletisim", "تماس", "Contact", "Contacto", "Contacto", "Contact", "联系"),
    "footer.help_label": t("Hilfe", "المساعدة", "Yardim", "کمک", "Aide", "Ayuda", "Ajuda", "Hulp", "帮助"),
    "footer.impressum_label": t("Impressum", "إمبريسوم", "Impressum", "ایمپرسوم", "Mentions legales", "Aviso legal", "Impressum", "Impressum", "公司信息"),
    "footer.legal_title": t("Rechtliches & Support", "القانوني والدعم", "Yasal ve destek", "حقوقی و پشتیبانی", "Juridique et support", "Legal y soporte", "Legal e suporte", "Juridisch en support", "法律与支持"),
    "footer.live_platform_description": t(
        "floos33 hilft verifizierten Unternehmen, überschüssige Bestände zu bewegen, Nachfrage schneller zu beantworten und Handelsgespräche auf einer Plattform zu verwalten.",
        "تساعد floos33 الشركات الموثقة على تحريك المخزون الفائض والاستجابة للطلب بشكل أسرع وإدارة محادثات التجارة داخل منصة واحدة.",
        "floos33, dogrulanmis isletmelerin fazla stogu hareket ettirmesine, talebe daha hizli cevap vermesine ve ticari gorusmeleri tek bir platformda yonetmesine yardim eder.",
        "floos33 به کسب وکارهای تاییدشده کمک می کند تا موجودی مازاد را جابه جا کنند، سریع تر به تقاضا پاسخ دهند و گفتگوهای تجاری را در یک پلتفرم مدیریت کنند.",
        "floos33 aide les entreprises verifiees a ecouler leurs stocks excedentaires, a repondre plus vite a la demande et a gerer les echanges commerciaux sur une seule plateforme.",
        "floos33 ayuda a empresas verificadas a mover excedentes, responder mas rapido a la demanda y gestionar conversaciones comerciales en una sola plataforma.",
        "A floos33 ajuda empresas verificadas a mover stock excedentario, responder mais rapido a procura e gerir conversas comerciais numa unica plataforma.",
        "floos33 helpt geverifieerde bedrijven overtollige voorraad te verplaatsen, sneller op vraag te reageren en handelsgesprekken op een platform te beheren.",
        "floos33 帮助已验证企业处理剩余库存、更快响应需求，并在一个平台上管理交易沟通。",
    ),
    "footer.live_platform_eyebrow": t("Live-Plattform", "المنصة المباشرة", "Canli platform", "پلتفرم زنده", "Plateforme active", "Plataforma activa", "Plataforma ativa", "Live platform", "实时平台"),
    "footer.live_platform_title": t(
        "Verbindet EU-Verkäufer mit MENA-Käufern.",
        "يربط البائعين في الاتحاد الأوروبي بالمشترين في منطقة الشرق الأوسط وشمال أفريقيا.",
        "AB saticilarini MENA alicilariyla bulusturur.",
        "فروشندگان اتحادیه اروپا را به خریداران منطقه منا متصل می کند.",
        "Connecte les vendeurs de l'UE aux acheteurs MENA.",
        "Conecta vendedores de la UE con compradores de MENA.",
        "Liga vendedores da UE a compradores MENA.",
        "Verbindt EU-verkopers met MENA-kopers.",
        "连接欧盟卖家与中东和北非买家。",
    ),
    "footer.marketplace_browse_listings": t("Listings durchsuchen", "تصفح العروض", "Ilanlara goz at", "مرور فهرست ها", "Parcourir les annonces", "Explorar listados", "Explorar listagens", "Vermeldingen bekijken", "浏览列表"),
    "footer.marketplace_categories": t("Kategorien", "الفئات", "Kategoriler", "دسته ها", "Categories", "Categorias", "Categorias", "Categorieen", "分类"),
    "footer.marketplace_machinery": t("Maschinen", "الآلات", "Makine", "ماشین آلات", "Machines", "Maquinaria", "Maquinaria", "Machines", "机械"),
    "footer.marketplace_services": t("Services", "الخدمات", "Hizmetler", "خدمات", "Services", "Servicios", "Servicos", "Diensten", "服务"),
    "footer.marketplace_supplier_database": t("Lieferantendatenbank", "قاعدة بيانات الموردين", "Tedarikci veritabani", "پایگاه داده تامین کنندگان", "Base fournisseurs", "Base de proveedores", "Base de fornecedores", "Leveranciersdatabase", "供应商数据库"),
    "footer.marketplace_title": t("Marktplatz", "السوق", "Pazaryeri", "بازار", "Marketplace", "Marketplace", "Marketplace", "Marketplace", "市场"),
    "footer.platform_subtitle": t("Handelsplattform EU nach MENA", "منصة تجارة من الاتحاد الأوروبي إلى منطقة الشرق الأوسط وشمال أفريقيا", "AB'den MENA'ya ticaret platformu", "پلتفرم تجاری از اروپا به منا", "Plateforme commerciale UE vers MENA", "Plataforma comercial UE a MENA", "Plataforma comercial UE para MENA", "EU-naar-MENA handelsplatform", "欧盟到中东和北非贸易平台"),
    "footer.privacy_label": t("Datenschutzerklärung", "سياسة الخصوصية", "Gizlilik Politikasi", "سیاست حریم خصوصی", "Politique de confidentialite", "Politica de privacidad", "Politica de privacidade", "Privacybeleid", "隐私政策"),
    "footer.rfq_browse": t("RFQs durchsuchen", "تصفح طلبات الشراء", "RFQ'lara goz at", "مرور RFQها", "Parcourir les RFQ", "Explorar RFQ", "Explorar RFQs", "RFQ's bekijken", "浏览 RFQ"),
    "footer.rfq_my": t("Meine RFQs", "طلبات الشراء الخاصة بي", "RFQ'larim", "RFQهای من", "Mes RFQ", "Mis RFQ", "Os meus RFQs", "Mijn RFQ's", "我的 RFQ"),
    "footer.rfq_post": t("RFQ veröffentlichen", "نشر طلب شراء", "RFQ yayinla", "ثبت RFQ", "Publier un RFQ", "Publicar RFQ", "Publicar RFQ", "RFQ plaatsen", "发布 RFQ"),
    "footer.rfq_support": t("RFQ-Support", "دعم طلبات الشراء", "RFQ destegi", "پشتیبانی RFQ", "Support RFQ", "Soporte RFQ", "Suporte RFQ", "RFQ-support", "RFQ 支持"),
    "footer.rfq_title": t("RFQs", "طلبات الشراء", "RFQ'lar", "RFQها", "RFQ", "RFQ", "RFQs", "RFQ's", "RFQ"),
    "footer.sitemap_label": t("Sitemap", "خريطة الموقع", "Site haritasi", "نقشه سایت", "Plan du site", "Mapa del sitio", "Mapa do site", "Sitemap", "网站地图"),
    "footer.stats_businesses_body": t(
        "Aktive Käufer und Verkäufer in grenzüberschreitenden Handelsströmen.",
        "مشترون وبائعون نشطون عبر تدفقات التجارة العابرة للحدود.",
        "Sinir otesi ticaret akislarinda aktif alicilar ve saticilar.",
        "خریداران و فروشندگان فعال در جریان های تجارت فرامرزی.",
        "Acheteurs et vendeurs actifs dans les flux commerciaux transfrontaliers.",
        "Compradores y vendedores activos en flujos de comercio transfronterizo.",
        "Compradores e vendedores ativos em fluxos de comercio transfronteirico.",
        "Actieve kopers en verkopers in grensoverschrijdende handelsstromen.",
        "活跃于跨境贸易流程中的买家和卖家。",
    ),
    "footer.stats_businesses_label": t("Unternehmen", "الشركات", "Isletmeler", "کسب وکارها", "Entreprises", "Empresas", "Empresas", "Bedrijven", "企业"),
    "footer.stats_businesses_value": t("3,800+", "3,800+", "3,800+", "3,800+", "3,800+", "3,800+", "3,800+", "3,800+", "3,800+"),
    "footer.stats_listings_body": t(
        "Überbestand, Liquidation, Paletten und gemischte kommerzielle Lose.",
        "فائض مخزون وتصفيات ومنصات نقالة وشحنات تجارية مختلطة.",
        "Fazla stok, tasfiye, paletler ve karisik ticari partiler.",
        "مازاد موجودی، تصفیه، پالت ها و محموله های تجاری ترکیبی.",
        "Surstocks, liquidation, palettes et lots commerciaux mixtes.",
        "Sobrestock, liquidacion, palets y lotes comerciales mixtos.",
        "Excesso de stock, liquidacao, paletes e lotes comerciais mistos.",
        "Overstock, liquidatie, pallets en gemengde commerciële partijen.",
        "过剩库存、清仓货、托盘和混合商业批次。",
    ),
    "footer.stats_listings_label": t("Listings", "العروض", "Ilanlar", "فهرست ها", "Annonces", "Listados", "Listagens", "Vermeldingen", "列表"),
    "footer.stats_listings_value": t("1,200+", "1,200+", "1,200+", "1,200+", "1,200+", "1,200+", "1,200+", "1,200+", "1,200+"),
    "footer.stats_trades_body": t(
        "RFQs, Anfragen und moderierte Deal-Fortschritte finden jeden Tag statt.",
        "طلبات الشراء والاستفسارات وتقدم الصفقات المُدار يحدث كل يوم.",
        "RFQ'lar, talepler ve denetlenen anlasma ilerlemeleri her gun gerceklesir.",
        "RFQها، استعلام ها و پیشرفت کنترل شده معاملات هر روز در جریان است.",
        "Des RFQ, des demandes et des progres de transaction moderes ont lieu chaque jour.",
        "RFQ, consultas y progreso moderado de operaciones ocurren cada dia.",
        "RFQs, consultas e progresso moderado das negociacoes acontecem todos os dias.",
        "RFQ's, aanvragen en gemodereerde dealvoortgang gebeuren elke dag.",
        "RFQ、询盘和受控交易进展每天都在发生。",
    ),
    "footer.stats_trades_label": t("Handel", "الصفقات", "Ticaretler", "معاملات", "Transactions", "Operaciones", "Negociacoes", "Transacties", "交易"),
    "footer.stats_trades_value": t("Täglich aktiv", "نشط يومياً", "Her gun aktif", "روزانه فعال", "Actif chaque jour", "Activo a diario", "Ativo diariamente", "Dagelijks actief", "每日活跃"),
    "footer.terms_label": t("Nutzungsbedingungen", "شروط الخدمة", "Hizmet Sartlari", "شرایط خدمات", "Conditions d'utilisation", "Terminos del servicio", "Termos de servico", "Servicevoorwaarden", "服务条款"),
}


def fill_cms_translations(apps, schema_editor):
    CMSBlock = apps.get_model("core", "CMSBlock")

    for block in CMSBlock.objects.filter(key__in=CMS_TRANSLATIONS):
        values = CMS_TRANSLATIONS[block.key]
        for field_name, value in values.items():
            setattr(block, field_name, value)
        block.save(update_fields=[*LANGUAGE_FIELDS, "updated_at"])


def noop(apps, schema_editor):
    return None


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0018_fill_cms_legal_pages_languages"),
    ]

    operations = [
        migrations.RunPython(fill_cms_translations, noop),
    ]
