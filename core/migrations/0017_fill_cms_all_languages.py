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
    "about": {
        "eyebrow": t("Über uns", "حول", "Hakkında", "درباره", "À propos", "Acerca de", "Sobre", "Over", "关于"),
        "intro": t(
            "floos33 ist ein B2B-Marktplatz, der genehmigte Stocklots, Käufernachfrage und moderierte Deal-Workflows im grenzüberschreitenden Handel zusammenführt.",
            "floos33 هي منصة B2B صُممت لربط المخزونات المعتمدة وطلب المشترين وسير الصفقات المُدار ضمن التجارة العابرة للحدود.",
            "floos33, onaylı stok partilerini, alıcı talebini ve denetlenen anlaşma akışlarını sınır ötesi ticarette buluşturmak için tasarlanmış bir B2B pazaryeridir.",
            "floos33 یک بازار B2B است که برای اتصال استاک لات های تاییدشده، تقاضای خریداران و فرایندهای مدیریت شده معامله در تجارت فرامرزی طراحی شده است.",
            "floos33 est une place de marche B2B conçue pour relier les lots de stock approuvés, la demande des acheteurs et des workflows de transaction modérés dans le commerce transfrontalier.",
            "floos33 es un marketplace B2B diseñado para conectar lotes de stock aprobados, demanda de compradores y flujos de operación moderados en el comercio transfronterizo.",
            "A floos33 e uma plataforma B2B criada para ligar lotes de stock aprovados, procura de compradores e fluxos de negociacao moderados no comercio transfronteirico.",
            "floos33 is een B2B-marktplaats die goedgekeurde stocklots, kopersvraag en gemodereerde dealworkflows in grensoverschrijdende handel samenbrengt.",
            "floos33 是一个 B2B 市场平台，旨在连接已审核的尾货批次、买家需求以及跨境贸易中的受控交易流程。",
        ),
        "meta_description": t(
            "Erfahren Sie mehr über floos33, die B2B-Plattform für genehmigte Stocklots, RFQs und strukturierte grenzüberschreitende Handelsabläufe.",
            "تعرّف على floos33، منصة B2B للمخزونات المعتمدة وطلبات الشراء وسير العمل المنظم للتجارة العابرة للحدود.",
            "Onaylı stok partileri, RFQ'lar ve yapılandırılmış sınır ötesi ticaret akışları için B2B platformu floos33 hakkında bilgi edinin.",
            "درباره floos33، پلتفرم B2B برای استاک لات های تاییدشده، RFQها و فرایندهای ساختارمند تجارت فرامرزی بیشتر بدانید.",
            "Decouvrez floos33, la plateforme B2B pour les lots de stock approuves, les RFQ et les workflows structures de commerce transfrontalier.",
            "Conozca floos33, la plataforma B2B para lotes de stock aprobados, RFQ y flujos estructurados de comercio transfronterizo.",
            "Conheca a floos33, a plataforma B2B para lotes de stock aprovados, RFQs e fluxos estruturados de comercio transfronteirico.",
            "Lees meer over floos33, het B2B-platform voor goedgekeurde stocklots, RFQ's en gestructureerde grensoverschrijdende handelsworkflows.",
            "了解 floos33，这个面向已审核尾货批次、RFQ 和结构化跨境贸易流程的 B2B 平台。",
        ),
        "meta_title": t("Über floos33", "حول floos33", "floos33 Hakkında", "درباره floos33", "À propos de floos33", "Acerca de floos33", "Sobre a floos33", "Over floos33", "关于 floos33"),
        "section_1_body": t(
            "Die Plattform hilft Verkäufern, genehmigte Liquidations- und Überbestandslose zu veröffentlichen, während Käufer Angebote entdecken, RFQs einstellen und sich über strukturierte Abläufe verbinden.",
            "تساعد المنصة البائعين على نشر شحنات التصفية والفائض المعتمدة، بينما يكتشف المشترون العرض وينشرون طلبات الشراء ويتواصلون عبر سير عمل منظم.",
            "Platform, saticilarin onayli tasfiye ve fazla stok partilerini yayinlamasina yardim ederken alicilarin tedariği kesfetmesini, RFQ yayinlamasini ve yapilandirilmis akislar uzerinden baglanti kurmasini saglar.",
            "این پلتفرم به فروشندگان کمک می کند تا محموله های تاییدشده مازاد و تصفیه ای را منتشر کنند، در حالی که خریداران عرضه را پیدا می کنند، RFQ ثبت می کنند و از طریق فرایندهای ساختارمند ارتباط می گیرند.",
            "La plateforme aide les vendeurs a publier des lots approuves de liquidation et de surstock, tandis que les acheteurs decouvrent l'offre, publient des RFQ et se connectent via des workflows structures.",
            "La plataforma ayuda a los vendedores a publicar lotes aprobados de liquidacion y sobrestock, mientras los compradores descubren oferta, publican RFQ y se conectan mediante flujos estructurados.",
            "A plataforma ajuda os vendedores a publicar lotes aprovados de liquidacao e excesso de stock, enquanto os compradores descobrem oferta, publicam RFQs e ligam-se por fluxos estruturados.",
            "Het platform helpt verkopers goedgekeurde liquidatie- en overstockpartijen te publiceren, terwijl kopers aanbod ontdekken, RFQ's plaatsen en via gestructureerde workflows contact leggen.",
            "该平台帮助卖家发布已审核的清仓和积压库存批次，同时让买家发现供应、发布 RFQ，并通过结构化流程建立联系。",
        ),
        "section_1_title": t(
            "Was die Plattform macht",
            "ما الذي تقوم به المنصة",
            "Platform ne yapar",
            "پلتفرم چه کاری انجام می دهد",
            "Ce que fait la plateforme",
            "Que hace la plataforma",
            "O que a plataforma faz",
            "Wat het platform doet",
            "平台的作用",
        ),
        "section_2_body": t(
            "Verifizierung, Moderation, Identitätskontrollen und Freigabepunkte sind in das Produkt integriert, damit Handelsgespräche mit besserer Aufsicht voranschreiten können.",
            "تم دمج التحقق والإشراف وضوابط الهوية ونقاط الموافقة داخل المنتج حتى تتحرك محادثات التجارة بإشراف أفضل.",
            "Dogrulama, moderasyon, kimlik kontrolleri ve onay noktaları ürüne yerleştirildi; böylece ticari görüşmeler daha iyi gözetimle ilerleyebilir.",
            "راستی آزمایی، نظارت، کنترل های هویتی و نقاط تایید در محصول تعبیه شده اند تا گفتگوهای تجاری با نظارت بهتر پیش بروند.",
            "La verification, la moderation, les controles d'identite et les points d'approbation sont integres au produit afin que les echanges commerciaux avancent avec une meilleure supervision.",
            "La verificacion, la moderacion, los controles de identidad y los puntos de aprobacion estan integrados en el producto para que las conversaciones comerciales avancen con mejor supervision.",
            "A verificacao, moderacao, controlos de identidade e pontos de aprovacao estao integrados no produto para que as conversas comerciais avancem com melhor supervisao.",
            "Verificatie, moderatie, identiteitscontroles en goedkeuringsmomenten zijn in het product ingebouwd zodat handelsgesprekken met beter toezicht kunnen verlopen.",
            "验证、审核、身份控制和审批节点都已集成到产品中，使交易沟通能够在更完善的监管下推进。",
        ),
        "section_2_title": t(
            "Wie Vertrauen umgesetzt wird",
            "كيف تتم إدارة الثقة",
            "Guven nasil saglaniyor",
            "اعتماد چگونه مدیریت می شود",
            "Comment la confiance est geree",
            "Como se gestiona la confianza",
            "Como a confianca e gerida",
            "Hoe vertrouwen wordt geregeld",
            "信任如何建立",
        ),
        "section_3_body": t(
            "Das aktuelle Produkt konzentriert sich auf Marktplatzsuche, RFQs, kontrollierte Kommunikation und mehrsprachige Sichtbarkeit, damit öffentliche Inhalte für jedes Publikum relevant bleiben.",
            "يركز المنتج الحالي على تصفح السوق وطلبات الشراء والتواصل المنضبط والظهور متعدد اللغات حتى يبقى المحتوى العام مناسباً لكل جمهور.",
            "Mevcut ürün, pazar yeri gezintisi, RFQ'lar, kontrollü iletişim ve çok dilli görünürlük üzerine odaklanır; böylece herkese açık içerik her kitle için alakalı kalır.",
            "محصول فعلی بر مرور بازار، RFQها، ارتباط کنترل شده و نمایش چندزبانه تمرکز دارد تا محتوای عمومی برای هر مخاطب مرتبط بماند.",
            "Le produit actuel se concentre sur la navigation de la marketplace, les RFQ, la communication controlee et la visibilite multilingue afin que le contenu public reste pertinent pour chaque audience.",
            "El producto actual se centra en la navegacion del marketplace, los RFQ, la comunicacion controlada y la visibilidad multilingue para que el contenido publico siga siendo relevante para cada audiencia.",
            "O produto atual foca-se na navegacao do marketplace, RFQs, comunicacao controlada e visibilidade multilingue para que o conteudo publico se mantenha relevante para cada audiencia.",
            "Het huidige product richt zich op marketplace-browsing, RFQ's, gecontroleerde communicatie en meertalige zichtbaarheid zodat publieke content relevant blijft voor elk publiek.",
            "当前产品聚焦于市场浏览、RFQ、受控沟通以及多语言可见性，确保公开内容始终与各类受众相关。",
        ),
        "section_3_title": t(
            "Aktuelle Produktrichtung",
            "اتجاه المنتج الحالي",
            "Mevcut urun yonu",
            "جهت فعلی محصول",
            "Orientation actuelle du produit",
            "Direccion actual del producto",
            "Direcao atual do produto",
            "Huidige productrichting",
            "当前产品方向",
        ),
        "title": t("Über floos33", "حول floos33", "floos33 Hakkında", "درباره floos33", "À propos de floos33", "Acerca de floos33", "Sobre a floos33", "Over floos33", "关于 floos33"),
    },
    "contact": {
        "direct_email_hint": t("Oder schreiben Sie uns direkt an:", "أو راسلنا مباشرة على:", "Veya bize dogrudan su adresten e-posta gonderin:", "یا مستقیماً به این نشانی ایمیل بزنید:", "Ou ecrivez-nous directement a :", "O escribanos directamente a:", "Ou envie-nos um email diretamente para:", "Of mail ons direct via:", "或者直接发送邮件至："),
        "direct_text": t(
            "Wenn Sie möchten, können Sie uns direkt kontaktieren und Ihren Firmennamen sowie Ihr Anliegen in der E-Mail angeben.",
            "إذا رغبت، يمكنك التواصل معنا مباشرة وذكر اسم شركتك ومشكلتك في البريد الإلكتروني.",
            "Tercih ederseniz bize dogrudan ulasabilir ve e-postada sirket adinizi ve sorununuzu belirtebilirsiniz.",
            "اگر ترجیح می دهید، می توانید مستقیماً با ما تماس بگیرید و نام شرکت و موضوع خود را در ایمیل ذکر کنید.",
            "Si vous preferez, vous pouvez nous contacter directement et inclure le nom de votre entreprise ainsi que votre demande dans l'email.",
            "Si lo prefiere, puede contactarnos directamente e incluir el nombre de su empresa y el problema en el correo.",
            "Se preferir, pode contactar-nos diretamente e incluir o nome da sua empresa e o assunto no email.",
            "Als u wilt, kunt u rechtstreeks contact met ons opnemen en uw bedrijfsnaam en vraag in de e-mail vermelden.",
            "如果您愿意，也可以直接联系我们，并在邮件中注明您的公司名称和问题。",
        ),
        "direct_title": t("Direkte E-Mail", "بريد إلكتروني مباشر", "Dogrudan e-posta", "ایمیل مستقیم", "Email direct", "Correo directo", "Email direto", "Directe e-mail", "直接邮件"),
        "email_subject_fallback": t("Supportanfrage von floos33", "طلب دعم من floos33", "floos33 destek talebi", "درخواست پشتیبانی از floos33", "Demande d'assistance de floos33", "Solicitud de soporte de floos33", "Pedido de suporte da floos33", "Supportverzoek van floos33", "来自 floos33 的支持请求"),
        "eyebrow": t("Kontakt / Support", "اتصال / الدعم", "Iletisim / Destek", "تماس / پشتیبانی", "Contact / Support", "Contacto / Soporte", "Contacto / Suporte", "Contact / Support", "联系 / 支持"),
        "form_intro": t(
            "Teilen Sie uns mit, wobei Sie Hilfe benötigen, und wir melden uns per E-Mail bei Ihnen.",
            "أخبرنا بما تحتاج إلى المساعدة فيه وسنتابع معك عبر البريد الإلكتروني.",
            "Hangi konuda yardima ihtiyaciniz oldugunu bize bildirin, size e-postayla donelim.",
            "به ما بگویید در چه موردی به کمک نیاز دارید و از طریق ایمیل با شما پیگیری می کنیم.",
            "Dites-nous ce dont vous avez besoin et nous reviendrons vers vous par email.",
            "Diganos con que necesita ayuda y le responderemos por correo electronico.",
            "Diga-nos em que precisa de ajuda e responderemos por email.",
            "Laat ons weten waarbij u hulp nodig heeft en we nemen per e-mail contact met u op.",
            "告诉我们您需要什么帮助，我们会通过电子邮件跟进您。",
        ),
        "form_title": t("Nachricht senden", "إرسال رسالة", "Mesaj gonder", "ارسال پیام", "Envoyer un message", "Enviar un mensaje", "Enviar mensagem", "Stuur een bericht", "发送消息"),
        "help_item_1": t("Kontozugang und Verifizierung", "الوصول إلى الحساب والتحقق", "Hesap erisimi ve dogrulama", "دسترسی به حساب و تایید", "Acces au compte et verification", "Acceso a la cuenta y verificacion", "Acesso a conta e verificacao", "Toegang tot account en verificatie", "账户访问与验证"),
        "help_item_2": t("Marktplatzangebote und Anfragen", "عروض السوق والاستفسارات", "Pazaryeri ilanlari ve talepler", "فهرست های بازار و استعلام ها", "Annonces marketplace et demandes", "Listados del marketplace y consultas", "Listagens do marketplace e consultas", "Marketplace-vermeldingen en aanvragen", "市场列表和询盘"),
        "help_item_3": t("RFQs und Verkäuferantworten", "طلبات الشراء وردود البائعين", "RFQ'lar ve satici yanitlari", "RFQها و پاسخ های فروشندگان", "RFQ et reponses des vendeurs", "RFQ y respuestas de vendedores", "RFQs e respostas dos vendedores", "RFQ's en verkopersreacties", "RFQ 与卖家回复"),
        "help_item_4": t("Allgemeiner Plattform-Support", "دعم عام للمنصة", "Genel platform destegi", "پشتیبانی عمومی پلتفرم", "Support general de la plateforme", "Soporte general de la plataforma", "Suporte geral da plataforma", "Algemene platformondersteuning", "一般平台支持"),
        "help_title": t("Hilfe bei", "تحتاج مساعدة في", "Su konuda yardim", "نیاز به کمک در", "Besoin d'aide pour", "Necesita ayuda con", "Precisa de ajuda com", "Hulp nodig bij", "需要帮助的事项"),
        "intro": t(
            "Nutzen Sie das untenstehende Formular für Kontofragen, Marktplatzprobleme, RFQ-Hilfe oder allgemeinen Support. Wir halten es bewusst einfach, damit Sie uns schnell erreichen.",
            "استخدم النموذج أدناه لأسئلة الحساب أو مشكلات السوق أو المساعدة في طلبات الشراء أو الدعم العام. نبقي الأمر بسيطاً حتى تتمكن من الوصول إلينا بسرعة.",
            "Hesap sorulari, pazaryeri sorunlari, RFQ yardimi veya genel destek icin asagidaki formu kullanin. Size hizli ulasabilmeniz icin sureci basit tutuyoruz.",
            "برای پرسش های حساب، مشکلات بازار، کمک درباره RFQ یا پشتیبانی عمومی از فرم زیر استفاده کنید. ما روند را ساده نگه می داریم تا سریع به ما برسید.",
            "Utilisez le formulaire ci-dessous pour les questions de compte, les problemes de marketplace, l'aide RFQ ou l'assistance generale. Nous restons simples afin que vous puissiez nous joindre rapidement.",
            "Use el formulario de abajo para preguntas sobre su cuenta, problemas del marketplace, ayuda con RFQ o soporte general. Lo mantenemos simple para que pueda contactarnos rapido.",
            "Use o formulario abaixo para questoes de conta, problemas do marketplace, ajuda com RFQs ou suporte geral. Mantemos tudo simples para que nos possa contactar rapidamente.",
            "Gebruik het onderstaande formulier voor accountvragen, marketplace-problemen, RFQ-hulp of algemene ondersteuning. We houden het eenvoudig zodat u ons snel kunt bereiken.",
            "如需账户问题、市场问题、RFQ 帮助或一般支持，请使用下方表单。我们保持流程简单，方便您快速联系我们。",
        ),
        "meta_description": t(
            "Kontaktieren Sie den floos33-Support für Kontohilfe, Marktplatzfragen, RFQ-Themen und allgemeine Plattformunterstützung.",
            "تواصل مع دعم floos33 للحصول على مساعدة الحساب وأسئلة السوق ومشكلات طلبات الشراء والمساعدة العامة للمنصة.",
            "Hesap yardimi, pazaryeri sorulari, RFQ konulari ve genel platform destegi icin floos33 destek ekibiyle iletisime gecin.",
            "برای کمک حساب، سوالات بازار، مسائل RFQ و پشتیبانی عمومی پلتفرم با پشتیبانی floos33 تماس بگیرید.",
            "Contactez le support floos33 pour l'aide au compte, les questions marketplace, les problemes RFQ et l'assistance generale.",
            "Contacte con el soporte de floos33 para ayuda con la cuenta, preguntas del marketplace, temas de RFQ y asistencia general.",
            "Contacte o suporte da floos33 para ajuda com a conta, questoes de marketplace, RFQs e assistencia geral da plataforma.",
            "Neem contact op met floos33-support voor hulp bij accounts, marketplace-vragen, RFQ-issues en algemene platformondersteuning.",
            "联系 floos33 支持团队，获取账户帮助、市场咨询、RFQ 问题和一般平台支持。",
        ),
        "meta_title": t("Kontakt / Support", "اتصال / الدعم", "Iletisim / Destek", "تماس / پشتیبانی", "Contact / Support", "Contacto / Soporte", "Contacto / Suporte", "Contact / Support", "联系 / 支持"),
        "phone_label": t("Telefon", "الهاتف", "Telefon", "تلفن", "Telephone", "Telefono", "Telefone", "Telefoon", "电话"),
        "phone_text": t(
            "Erreichbar über die im Projekt bereits genutzte Support-Hotline.",
            "يمكن الوصول إليه عبر خط دعم المنصة المستخدم بالفعل في المشروع.",
            "Projede halihazirda kullanilan platform destek hatti uzerinden ulasilabilir.",
            "از طریق خط پشتیبانی پلتفرم که پیش تر در پروژه استفاده شده قابل دسترسی است.",
            "Joignable via la ligne de support de la plateforme deja utilisee dans le projet.",
            "Disponible a traves de la linea de soporte de la plataforma ya utilizada en el proyecto.",
            "Disponivel atraves da linha de suporte da plataforma ja usada no projeto.",
            "Bereikbaar via de supportlijn van het platform die al in het project wordt gebruikt.",
            "可通过项目中已使用的平台支持热线联系。",
        ),
        "success_message": t("Ihre Nachricht wurde gesendet. Wir melden uns in Kürze.", "تم إرسال رسالتك. سنرد عليك قريباً.", "Mesajiniz gonderildi. Kisa sure icinde size donus yapacagiz.", "پیام شما ارسال شد. به زودی پاسخ می دهیم.", "Votre message a ete envoye. Nous vous repondrons sous peu.", "Su mensaje ha sido enviado. Le responderemos en breve.", "A sua mensagem foi enviada. Responderemos em breve.", "Uw bericht is verzonden. We reageren spoedig.", "您的消息已发送。我们会尽快回复。"),
        "support_email_label": t("Support-E-Mail", "بريد الدعم الإلكتروني", "Destek e-postasi", "ایمیل پشتیبانی", "Email support", "Correo de soporte", "Email de suporte", "Support-e-mail", "支持邮箱"),
        "support_email_text": t("Direkter Rückfallkontakt für dringenden Support.", "جهة اتصال مباشرة بديلة للدعم العاجل.", "Acil destek icin dogrudan yedek iletisim noktasi.", "راه تماس مستقیم جایگزین برای پشتیبانی فوری.", "Contact direct de secours pour une assistance urgente.", "Contacto directo alternativo para soporte urgente.", "Contacto direto alternativo para suporte urgente.", "Direct fallback-contact voor dringende ondersteuning.", "紧急支持的直接备用联系方式。"),
        "title": t(
            "Brauchen Sie Hilfe? Kontaktieren Sie unser Support-Team und wir melden uns bei Ihnen.",
            "هل تحتاج إلى مساعدة؟ تواصل مع فريق الدعم وسنعود إليك.",
            "Yardima mi ihtiyaciniz var? Destek ekibimizle iletisime gecin, size geri donelim.",
            "به کمک نیاز دارید؟ با تیم پشتیبانی ما تماس بگیرید تا با شما در ارتباط باشیم.",
            "Besoin d'aide ? Contactez notre equipe support et nous reviendrons vers vous.",
            "Necesita ayuda? Contacte con nuestro equipo de soporte y le responderemos.",
            "Precisa de ajuda? Contacte a nossa equipa de suporte e responderemos.",
            "Hulp nodig? Neem contact op met ons supportteam en we komen bij u terug.",
            "需要帮助吗？请联系支持团队，我们会与您联系。",
        ),
    },
    "footer": {},
    "home": {},
    "impressum": {},
    "privacy": {},
    "shared": {
        "contact_button": t("Kontakt", "اتصل", "Iletisim", "تماس", "Contact", "Contacto", "Contacto", "Contact", "联系"),
        "create_account": t("Konto erstellen", "إنشاء حساب", "Hesap olustur", "ایجاد حساب", "Creer un compte", "Crear cuenta", "Criar conta", "Account aanmaken", "创建账户"),
        "dashboard": t("Dashboard", "لوحة التحكم", "Panel", "داشبورد", "Tableau de bord", "Panel", "Painel", "Dashboard", "仪表板"),
        "default_meta_description": t(
            "floos33 ist ein B2B-Marktplatz für EU-Stocklots, Liquidationsbestände und Käufer-RFQs, der EU-Verkäufer mit MENA-Käufern verbindet.",
            "floos33 هي منصة B2B لمخزونات الاتحاد الأوروبي ومخزون التصفية وطلبات شراء المشترين، وتربط بين البائعين في الاتحاد الأوروبي والمشترين في منطقة الشرق الأوسط وشمال أفريقيا.",
            "floos33, AB stok partileri, tasfiye envanteri ve alici RFQ'lari icin AB saticilarini MENA alicilariyla bulusturan bir B2B pazaryeridir.",
            "floos33 یک بازار B2B برای استاک لات های اروپایی، موجودی های تصفیه ای و RFQ خریداران است که فروشندگان اتحادیه اروپا را به خریداران منطقه منا متصل می کند.",
            "floos33 est une plateforme B2B pour les lots de stock europeens, les stocks de liquidation et les RFQ acheteurs reliant les vendeurs de l'UE aux acheteurs MENA.",
            "floos33 es un marketplace B2B de lotes de stock de la UE, inventario de liquidacion y RFQ de compradores que conecta vendedores de la UE con compradores de MENA.",
            "A floos33 e um marketplace B2B para lotes de stock da UE, inventario de liquidacao e RFQs de compradores que liga vendedores da UE a compradores MENA.",
            "floos33 is een B2B-marktplaats voor EU-stocklots, liquidatievoorraad en kopers-RFQ's die EU-verkopers verbindt met MENA-kopers.",
            "floos33 是一个面向欧盟尾货批次、清仓库存和买家 RFQ 的 B2B 市场平台，连接欧盟卖家与中东和北非买家。",
        ),
        "default_site_title": t(
            "B2B-Stocklots- und RFQ-Marktplatz",
            "سوق B2B للمخزونات وطلبات الشراء",
            "B2B Stok Partileri ve RFQ Pazaryeri",
            "بازار B2B استاک لات و RFQ",
            "Marketplace B2B de lots de stock et RFQ",
            "Marketplace B2B de lotes de stock y RFQ",
            "Marketplace B2B de lotes de stock e RFQ",
            "B2B-marktplaats voor stocklots en RFQ's",
            "B2B 尾货与 RFQ 市场平台",
        ),
        "email_label": t("E-Mail", "البريد الإلكتروني", "E-posta", "ایمیل", "Email", "Correo electronico", "Email", "E-mail", "电子邮箱"),
        "list_stock": t("Bestand listen", "إدراج المخزون", "Stok listele", "ثبت موجودی", "Lister du stock", "Publicar stock", "Listar stock", "Voorraad plaatsen", "发布库存"),
        "listing_admin_approved": t("Admin-geprüft", "معتمد من الإدارة", "Yonetici onayli", "تایید شده توسط ادمین", "Approuve par l'admin", "Aprobado por admin", "Aprovado pelo admin", "Door admin goedgekeurd", "管理员已批准"),
        "listing_no_preview": t("Keine Vorschau", "لا توجد معاينة", "Onizleme yok", "بدون پیش نمایش", "Aucun apercu", "Sin vista previa", "Sem pre-visualizacao", "Geen voorbeeld", "无预览"),
        "listing_verified_user": t("Verifizierter Nutzer", "مستخدم موثّق", "Dogrulanmis kullanici", "کاربر تاییدشده", "Utilisateur verifie", "Usuario verificado", "Utilizador verificado", "Geverifieerde gebruiker", "已验证用户"),
        "logout": t("Abmelden", "تسجيل الخروج", "Cikis yap", "خروج", "Se deconnecter", "Cerrar sesion", "Terminar sessao", "Uitloggen", "退出登录"),
        "message_label": t("Nachricht", "الرسالة", "Mesaj", "پیام", "Message", "Mensaje", "Mensagem", "Bericht", "消息"),
        "my_listings": t("Meine Listings", "عروضي", "Ilanlarim", "آگهی های من", "Mes annonces", "Mis listados", "As minhas listagens", "Mijn vermeldingen", "我的列表"),
        "my_rfqs": t("Meine RFQs", "طلبات الشراء الخاصة بي", "RFQ'larim", "RFQهای من", "Mes RFQ", "Mis RFQ", "Os meus RFQs", "Mijn RFQ's", "我的 RFQ"),
        "name_label": t("Name", "الاسم", "Ad", "نام", "Nom", "Nombre", "Nome", "Naam", "姓名"),
        "nav_machinery": t("Maschinen", "الآلات", "Makine", "ماشین آلات", "Machines", "Maquinaria", "Maquinaria", "Machines", "机械"),
        "nav_marketplace": t("Marktplatz", "السوق", "Pazaryeri", "بازار", "Marketplace", "Marketplace", "Marketplace", "Marketplace", "市场"),
        "nav_rfqs": t("RFQs durchsuchen", "تصفح طلبات الشراء", "RFQ'lara goz at", "مرور RFQها", "Parcourir les RFQ", "Explorar RFQ", "Explorar RFQs", "RFQ's bekijken", "浏览 RFQ"),
        "nav_services": t("Services", "الخدمات", "Hizmetler", "خدمات", "Services", "Servicios", "Servicos", "Diensten", "服务"),
        "nav_supplier_database": t("Lieferantendatenbank", "قاعدة بيانات الموردين", "Tedarikci veritabani", "پایگاه داده تامین کنندگان", "Base fournisseurs", "Base de proveedores", "Base de fornecedores", "Leveranciersdatabase", "供应商数据库"),
        "notifications": t("Benachrichtigungen", "الإشعارات", "Bildirimler", "اعلان ها", "Notifications", "Notificaciones", "Notificacoes", "Meldingen", "通知"),
        "pagination_next": t("Weiter", "التالي", "Sonraki", "بعدی", "Suivant", "Siguiente", "Seguinte", "Volgende", "下一页"),
        "pagination_of": t("von", "من", " / ", "از", "sur", "de", "de", "van", "共"),
        "pagination_page": t("Seite", "الصفحة", "Sayfa", "صفحه", "Page", "Pagina", "Pagina", "Pagina", "页"),
        "pagination_previous": t("Zurück", "السابق", "Onceki", "قبلی", "Precedent", "Anterior", "Anterior", "Vorige", "上一页"),
        "rfq_target_label": t("Ziel:", "الهدف:", "Hedef:", "هدف:", "Cible :", "Objetivo:", "Alvo:", "Doel:", "目标："),
        "saved_items": t("Gespeicherte Elemente", "العناصر المحفوظة", "Kaydedilenler", "موارد ذخیره شده", "Elements sauvegardes", "Elementos guardados", "Itens guardados", "Opgeslagen items", "已保存项目"),
        "search_button": t("Suchen", "بحث", "Ara", "جستجو", "Rechercher", "Buscar", "Pesquisar", "Zoeken", "搜索"),
        "search_placeholder": t(
            "Listings, Kategorien, Produkte suchen...",
            "ابحث في العروض والفئات والمنتجات...",
            "Ilanlari, kategorileri, urunleri ara...",
            "جستجوی فهرست ها، دسته ها، محصولات...",
            "Rechercher des annonces, categories, produits...",
            "Buscar listados, categorias, productos...",
            "Pesquisar listagens, categorias, produtos...",
            "Zoek in vermeldingen, categorieen, producten...",
            "搜索列表、分类、产品……",
        ),
        "settings": t("Einstellungen", "الإعدادات", "Ayarlar", "تنظیمات", "Parametres", "Configuracion", "Definicoes", "Instellingen", "设置"),
        "sign_in": t("Anmelden", "تسجيل الدخول", "Giris yap", "ورود", "Se connecter", "Iniciar sesion", "Iniciar sessao", "Inloggen", "登录"),
        "subject_label": t("Betreff", "الموضوع", "Konu", "موضوع", "Objet", "Asunto", "Assunto", "Onderwerp", "主题"),
        "submit_button": t("Nachricht senden", "إرسال الرسالة", "Mesaj gonder", "ارسال پیام", "Envoyer le message", "Enviar mensaje", "Enviar mensagem", "Bericht verzenden", "发送消息"),
        "support": t("Support", "الدعم", "Destek", "پشتیبانی", "Support", "Soporte", "Suporte", "Support", "支持"),
        "view_listing_details": t("Details ansehen", "عرض التفاصيل", "Detaylari gor", "مشاهده جزئیات", "Voir les details", "Ver detalles", "Ver detalhes", "Details bekijken", "查看详情"),
        "view_rfq_details": t("RFQ ansehen", "عرض طلب الشراء", "RFQ'yu gor", "مشاهده RFQ", "Voir le RFQ", "Ver RFQ", "Ver RFQ", "RFQ bekijken", "查看 RFQ"),
    },
    "terms": {},
}


def flatten_translations():
    flattened = {}
    for page_code, blocks in CMS_TRANSLATIONS.items():
        for slot, values in blocks.items():
            flattened[f"{page_code}.{slot}"] = values
    return flattened


def fill_cms_translations(apps, schema_editor):
    CMSBlock = apps.get_model("core", "CMSBlock")

    translations = flatten_translations()
    for block in CMSBlock.objects.all():
        values = translations.get(block.key)
        if not values:
            continue
        for field_name, value in values.items():
            setattr(block, field_name, value)
        block.save(update_fields=[*LANGUAGE_FIELDS, "updated_at"])


def noop(apps, schema_editor):
    return None


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0016_cms_page_structure"),
    ]

    operations = [
        migrations.RunPython(fill_cms_translations, noop),
    ]
