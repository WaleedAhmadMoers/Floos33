from django.db import migrations, models


LEGACY_KEY_MAP = {
    "hero_title": "home.hero_title",
    "hero_subtitle": "home.hero_subtitle",
    "hero_description": "home.hero_description",
    "hero_cta_primary": "home.hero_cta_primary",
    "hero_cta_secondary": "home.hero_cta_secondary",
    "hero_cta_primary_guest": "home.hero_cta_primary_guest",
    "hero_cta_secondary_guest": "home.hero_cta_secondary_guest",
    "hero_badge_verified_users": "home.hero_badge_verified_users",
    "hero_badge_admin_approved": "home.hero_badge_admin_approved",
    "hero_badge_identity_protection": "home.hero_badge_identity_protection",
    "hero_badge_controlled_deal_flow": "home.hero_badge_controlled_deal_flow",
    "market_snapshot_title": "home.market_snapshot_title",
    "market_snapshot_active_suffix": "home.market_snapshot_active_suffix",
    "market_snapshot_item_1_eyebrow": "home.market_snapshot_item_1_eyebrow",
    "market_snapshot_item_1_title": "home.market_snapshot_item_1_title",
    "market_snapshot_item_1_description": "home.market_snapshot_item_1_description",
    "market_snapshot_item_1_tag": "home.market_snapshot_item_1_tag",
    "market_snapshot_item_2_eyebrow": "home.market_snapshot_item_2_eyebrow",
    "market_snapshot_item_2_title": "home.market_snapshot_item_2_title",
    "market_snapshot_item_2_description": "home.market_snapshot_item_2_description",
    "market_snapshot_item_2_tag": "home.market_snapshot_item_2_tag",
    "market_snapshot_item_3_eyebrow": "home.market_snapshot_item_3_eyebrow",
    "market_snapshot_item_3_title": "home.market_snapshot_item_3_title",
    "market_snapshot_item_3_description": "home.market_snapshot_item_3_description",
    "market_snapshot_item_3_tag": "home.market_snapshot_item_3_tag",
    "market_snapshot_view_all": "home.market_snapshot_view_all",
    "marketplace_section_title": "home.marketplace_section_title",
    "marketplace_section_description": "home.marketplace_section_description",
    "marketplace_filters_title": "home.marketplace_filters_title",
    "marketplace_reset": "home.marketplace_reset",
    "marketplace_categories_title": "home.marketplace_categories_title",
    "marketplace_all": "home.marketplace_all",
    "marketplace_condition_title": "home.marketplace_condition_title",
    "marketplace_shortcuts_title": "home.marketplace_shortcuts_title",
    "marketplace_open_full": "home.marketplace_open_full",
    "marketplace_saved_listings": "home.marketplace_saved_listings",
    "marketplace_sign_in_to_save": "home.marketplace_sign_in_to_save",
    "marketplace_empty_state": "home.marketplace_empty_state",
    "rfq_section_title": "home.rfq_section_title",
    "rfq_section_description": "home.rfq_section_description",
    "rfq_cta_primary": "home.rfq_cta_primary",
    "rfq_cta_secondary": "home.rfq_cta_secondary",
    "how_section_eyebrow": "home.how_section_eyebrow",
    "how_section_title": "home.how_section_title",
    "how_section_description": "home.how_section_description",
    "how_step_1_title": "home.how_step_1_title",
    "how_step_1_description": "home.how_step_1_description",
    "how_step_2_title": "home.how_step_2_title",
    "how_step_2_description": "home.how_step_2_description",
    "how_step_3_title": "home.how_step_3_title",
    "how_step_3_description": "home.how_step_3_description",
    "how_step_4_title": "home.how_step_4_title",
    "how_step_4_description": "home.how_step_4_description",
    "trust_section_eyebrow": "home.trust_section_eyebrow",
    "trust_section_title": "home.trust_section_title",
    "trust_point_1_title": "home.trust_point_1_title",
    "trust_point_1_description": "home.trust_point_1_description",
    "trust_point_2_title": "home.trust_point_2_title",
    "trust_point_2_description": "home.trust_point_2_description",
    "trust_point_3_title": "home.trust_point_3_title",
    "trust_point_3_description": "home.trust_point_3_description",
    "trust_point_4_title": "home.trust_point_4_title",
    "trust_point_4_description": "home.trust_point_4_description",
    "cta_section_title": "home.cta_section_title",
    "cta_section_description": "home.cta_section_description",
    "cta_section_primary": "home.cta_section_primary",
    "cta_section_secondary": "home.cta_section_secondary",
    "listing_no_preview": "shared.listing_no_preview",
    "listing_admin_approved": "shared.listing_admin_approved",
    "listing_verified_user": "shared.listing_verified_user",
    "listing_view_details": "shared.view_listing_details",
    "rfq_target_label": "shared.rfq_target_label",
    "rfq_view_details": "shared.view_rfq_details",
    "pagination_previous": "shared.pagination_previous",
    "pagination_next": "shared.pagination_next",
    "pagination_page": "shared.pagination_page",
    "pagination_of": "shared.pagination_of",
    "footer_description": "footer.about_text",
}


SITEWIDE_DEFAULTS = {
    "home.hero_title": "The marketplace for EU overstock and MENA demand.",
    "home.hero_subtitle": "EU to MENA overstock and liquidation marketplace",
    "home.hero_description": "Browse approved listings, post RFQs, negotiate privately, and progress every deal under platform oversight with identity protection and verification.",
    "home.hero_cta_primary": "Browse marketplace",
    "home.hero_cta_secondary": "Browse RFQs",
    "home.hero_cta_primary_guest": "Create account",
    "home.hero_cta_secondary_guest": "Browse marketplace",
    "home.hero_badge_verified_users": "Verified users",
    "home.hero_badge_admin_approved": "Admin-approved listings",
    "home.hero_badge_identity_protection": "Identity protection",
    "home.hero_badge_controlled_deal_flow": "Controlled deal flow",
    "home.market_snapshot_title": "Market snapshot",
    "home.market_snapshot_active_suffix": "active",
    "home.market_snapshot_item_1_eyebrow": "Trending surplus",
    "home.market_snapshot_item_1_title": "Industrial tools and mixed pallets",
    "home.market_snapshot_item_1_description": "High-volume clearance inventory from verified EU suppliers.",
    "home.market_snapshot_item_1_tag": "MOQ flexible",
    "home.market_snapshot_item_2_eyebrow": "New liquidation",
    "home.market_snapshot_item_2_title": "Home and kitchen returns",
    "home.market_snapshot_item_2_description": "Fresh mixed-brand stock prepared for faster cross-border deals.",
    "home.market_snapshot_item_2_tag": "Fast moving",
    "home.market_snapshot_item_3_eyebrow": "Active RFQs",
    "home.market_snapshot_item_3_title": "Electronics clearance lots",
    "home.market_snapshot_item_3_description": "Buyers in MENA are actively looking for approved EU stock.",
    "home.market_snapshot_item_3_tag": "Respond now",
    "home.market_snapshot_view_all": "View all listings",
    "home.marketplace_section_title": "Marketplace",
    "home.marketplace_section_description": "Browse approved public listings that match your selected language.",
    "home.marketplace_filters_title": "Filters",
    "home.marketplace_reset": "Reset",
    "home.marketplace_categories_title": "Categories",
    "home.marketplace_all": "All",
    "home.marketplace_condition_title": "Condition",
    "home.marketplace_shortcuts_title": "Shortcuts",
    "home.marketplace_open_full": "Open full marketplace",
    "home.marketplace_saved_listings": "Saved listings",
    "home.marketplace_sign_in_to_save": "Sign in to save",
    "home.marketplace_empty_state": "No listings yet.",
    "home.rfq_section_title": "Need something specific?",
    "home.rfq_section_description": "Post an RFQ and invite verified sellers to respond privately.",
    "home.rfq_cta_primary": "Post an RFQ",
    "home.rfq_cta_secondary": "Explore RFQs",
    "home.how_section_eyebrow": "Simple process",
    "home.how_section_title": "How the marketplace works",
    "home.how_section_description": "Four steps to start trading",
    "home.how_step_1_title": "Browse or post",
    "home.how_step_1_description": "Search approved stocklots or post an RFQ when you need specific specs or volume.",
    "home.how_step_2_title": "Connect privately",
    "home.how_step_2_description": "Chat with verified users while identities stay masked until reveal is approved.",
    "home.how_step_3_title": "Negotiate with oversight",
    "home.how_step_3_description": "Conversations and identity reveals are moderated before key trade steps move forward.",
    "home.how_step_4_title": "Confirm the deal",
    "home.how_step_4_description": "Both sides accept, admin approves, and progress is tracked with status and history.",
    "home.trust_section_eyebrow": "Trust and safety",
    "home.trust_section_title": "Verification and oversight built in",
    "home.trust_point_1_title": "Verified users",
    "home.trust_point_1_description": "Admin-verified accounts plus buyer and seller checks before sensitive actions.",
    "home.trust_point_2_title": "Approved listings and RFQs",
    "home.trust_point_2_description": "Only approved, active public content is visible to the right language audience.",
    "home.trust_point_3_title": "Identity protection",
    "home.trust_point_3_description": "Buyer and seller identities stay masked until reveal requests are approved.",
    "home.trust_point_4_title": "Controlled deal flow",
    "home.trust_point_4_description": "Deals move in stages with admin oversight, history, and notifications.",
    "home.cta_section_title": "Ready to start?",
    "home.cta_section_description": "Browse the marketplace or create your account to trade with verification and oversight.",
    "home.cta_section_primary": "Start browsing",
    "home.cta_section_secondary": "Create account",
    "shared.default_site_title": "B2B Stocklots and RFQ Marketplace",
    "shared.default_meta_description": "floos33 is a B2B marketplace for EU stocklots, liquidation inventory, and buyer RFQs connecting EU sellers with MENA buyers.",
    "shared.nav_marketplace": "Marketplace",
    "shared.nav_rfqs": "Browse RFQs",
    "shared.nav_services": "Services",
    "shared.nav_machinery": "Machinery",
    "shared.nav_supplier_database": "Supplier Database",
    "shared.contact_button": "Contact",
    "shared.saved_items": "Saved items",
    "shared.dashboard": "Dashboard",
    "shared.my_rfqs": "My RFQs",
    "shared.my_listings": "My listings",
    "shared.settings": "Settings",
    "shared.support": "Support",
    "shared.notifications": "Notifications",
    "shared.logout": "Logout",
    "shared.list_stock": "List stock",
    "shared.sign_in": "Sign in",
    "shared.create_account": "Create account",
    "shared.search_placeholder": "Search listings, categories, products...",
    "shared.search_button": "Search",
    "shared.listing_no_preview": "No preview",
    "shared.listing_admin_approved": "Admin approved",
    "shared.listing_verified_user": "Verified user",
    "shared.view_listing_details": "View details",
    "shared.rfq_target_label": "Target:",
    "shared.view_rfq_details": "View RFQ",
    "shared.pagination_previous": "Previous",
    "shared.pagination_next": "Next",
    "shared.pagination_page": "Page",
    "shared.pagination_of": "of",
    "shared.submit_button": "Send message",
    "shared.name_label": "Name",
    "shared.email_label": "Email",
    "shared.subject_label": "Subject",
    "shared.message_label": "Message",
    "footer.live_platform_eyebrow": "Live platform",
    "footer.live_platform_title": "Connecting EU sellers with MENA buyers.",
    "footer.live_platform_description": "floos33 helps verified businesses move surplus inventory, answer demand faster, and manage trade conversations in one platform.",
    "footer.stats_businesses_label": "Businesses",
    "footer.stats_businesses_value": "3,800+",
    "footer.stats_businesses_body": "Active buyers and sellers across cross-border trade flows.",
    "footer.stats_listings_label": "Listings",
    "footer.stats_listings_value": "1,200+",
    "footer.stats_listings_body": "Overstock, liquidation, pallets, and mixed commercial lots.",
    "footer.stats_trades_label": "Trades",
    "footer.stats_trades_value": "Active daily",
    "footer.stats_trades_body": "RFQs, inquiries, and moderated deal progress happening every day.",
    "footer.platform_subtitle": "EU to MENA trade platform",
    "footer.about_text": "A B2B marketplace for browsing stocklots, posting RFQs, and moving deals forward with stronger trust and structure.",
    "footer.marketplace_title": "Marketplace",
    "footer.marketplace_browse_listings": "Browse listings",
    "footer.marketplace_categories": "Categories",
    "footer.marketplace_services": "Services",
    "footer.marketplace_machinery": "Machinery",
    "footer.marketplace_supplier_database": "Supplier Database",
    "footer.rfq_title": "RFQs",
    "footer.rfq_browse": "Browse RFQs",
    "footer.rfq_post": "Post RFQ",
    "footer.rfq_my": "My RFQs",
    "footer.rfq_support": "RFQ support",
    "footer.account_title": "Account",
    "footer.account_profile": "Profile",
    "footer.account_saved": "Saved",
    "footer.account_settings": "Settings",
    "footer.account_about": "About floos33",
    "footer.legal_title": "Legal & Support",
    "footer.about_label": "About",
    "footer.contact_label": "Contact",
    "footer.privacy_label": "Privacy Policy",
    "footer.terms_label": "Terms of Service",
    "footer.impressum_label": "Impressum",
    "footer.sitemap_label": "Sitemap",
    "footer.help_label": "Help",
    "about.meta_title": "About floos33",
    "about.meta_description": "Learn about floos33, the B2B platform for approved stocklots, RFQs, and structured cross-border trade workflows.",
    "about.eyebrow": "About",
    "about.title": "About floos33",
    "about.intro": "floos33 is a B2B marketplace designed to connect approved stocklots, buyer demand, and moderated deal workflows across cross-border trade.",
    "about.section_1_title": "What the platform does",
    "about.section_1_body": "The platform helps sellers publish approved liquidation and overstock lots while buyers discover supply, post RFQs, and connect through structured workflows.",
    "about.section_2_title": "How trust is handled",
    "about.section_2_body": "Verification, moderation, identity controls, and approval checkpoints are built into the product so trade conversations can move with better oversight.",
    "about.section_3_title": "Current product direction",
    "about.section_3_body": "The current product focuses on marketplace browsing, RFQs, controlled communication, and multilingual visibility so public content stays relevant to each audience.",
    "contact.meta_title": "Contact / Support",
    "contact.meta_description": "Contact floos33 support for account help, marketplace questions, RFQ issues, and general platform assistance.",
    "contact.eyebrow": "Contact / Support",
    "contact.title": "Need help? Contact our support team and we will get back to you.",
    "contact.intro": "Use the form below for account questions, marketplace issues, RFQ help, or general support. We keep it simple so you can reach us quickly.",
    "contact.support_email_label": "Support email",
    "contact.support_email_text": "Direct fallback contact for urgent support.",
    "contact.phone_label": "Phone",
    "contact.phone_text": "Reachable through the platform support line already used in the project.",
    "contact.form_title": "Send a message",
    "contact.form_intro": "Tell us what you need help with and we will follow up by email.",
    "contact.direct_email_hint": "Or email us directly at:",
    "contact.help_title": "Need help with",
    "contact.help_item_1": "Account access and verification",
    "contact.help_item_2": "Marketplace listings and inquiries",
    "contact.help_item_3": "RFQs and seller responses",
    "contact.help_item_4": "General platform support",
    "contact.direct_title": "Direct email",
    "contact.direct_text": "If you prefer, you can contact us directly and include your company name and issue in the email.",
    "contact.email_subject_fallback": "Support request from floos33",
    "contact.success_message": "Your message has been sent. We will respond shortly.",
    "privacy.meta_title": "Privacy Policy",
    "privacy.meta_description": "Read how floos33 handles account information, platform data, communication records, and support requests.",
    "privacy.eyebrow": "Privacy",
    "privacy.title": "Privacy Policy",
    "privacy.intro": "This page explains how platform-owned data and account activity are handled on floos33. Update the final legal wording before production launch.",
    "privacy.section_1_title": "Data we collect",
    "privacy.section_1_body": "We collect account details, company details, marketplace submissions, RFQs, contact messages, and platform activity needed to operate the service.",
    "privacy.section_2_title": "Why we use it",
    "privacy.section_2_body": "Data is used to run the marketplace, verify accounts, moderate listings and RFQs, respond to support requests, and improve platform operations.",
    "privacy.section_3_title": "Who can access it",
    "privacy.section_3_body": "Authorized platform administrators can access data needed for moderation, support, compliance, and security reviews. Public visitors only see approved public content.",
    "privacy.section_4_title": "Retention and control",
    "privacy.section_4_body": "We retain platform data as long as needed for service operation, legal obligations, or dispute handling. Contact the platform operator for account or data requests.",
    "terms.meta_title": "Terms of Service",
    "terms.meta_description": "Review the main platform terms for using floos33, including marketplace rules, moderation, and account responsibilities.",
    "terms.eyebrow": "Terms",
    "terms.title": "Terms of Service",
    "terms.intro": "These starter terms describe the basic platform rules for accessing floos33. Replace them with production legal wording before launch.",
    "terms.section_1_title": "Platform access",
    "terms.section_1_body": "Users must provide accurate account information and keep their login credentials secure. Platform access can be limited or revoked for misuse or policy breaches.",
    "terms.section_2_title": "Listings and RFQs",
    "terms.section_2_body": "Sellers and buyers remain responsible for the content they submit. floos33 may review, approve, reject, or remove submissions to maintain marketplace quality and safety.",
    "terms.section_3_title": "Moderation and communication",
    "terms.section_3_body": "Platform conversations, reveal requests, and deal milestones may be moderated. Users must avoid fraud, abuse, spam, unlawful trade activity, and misleading information.",
    "terms.section_4_title": "Liability and updates",
    "terms.section_4_body": "The platform may evolve over time. Terms, workflows, and feature access can be updated when needed to improve compliance, security, and operational stability.",
    "impressum.meta_title": "Impressum",
    "impressum.meta_description": "Platform operator and legal notice for floos33.",
    "impressum.eyebrow": "Impressum",
    "impressum.title": "Impressum / Imprint",
    "impressum.intro": "This page provides the platform operator details and legal notice structure for floos33. Replace these starter details with your final registered information before launch.",
    "impressum.company_name_label": "Company name",
    "impressum.company_name": "floos33",
    "impressum.address_label": "Registered address",
    "impressum.address": "Berlin, Germany\nPlease update this block with your final registered company address before production launch.",
    "impressum.contact_label": "Contact",
    "impressum.contact_body": "Email: support@floos33.de\nPhone: +49 1575 4967414",
    "impressum.representative_label": "Authorized representative",
    "impressum.representative": "Please update this block with the responsible legal representative.",
    "impressum.registration_label": "Commercial register",
    "impressum.registration": "Please update this block with the commercial register court and number, if applicable.",
    "impressum.vat_label": "VAT ID",
    "impressum.vat": "Please update this block with the VAT identification number, if applicable.",
    "impressum.legal_title": "Legal notice",
    "impressum.legal_body": "This starter legal notice is provided to keep the page structurally complete during development. Replace it with jurisdiction-specific legal wording and final company details before going live.",
}


def page_from_key(key):
    if "." in key:
        return key.split(".", 1)[0]
    return "shared"


def forward(apps, schema_editor):
    CMSBlock = apps.get_model("core", "CMSBlock")
    text_fields = [field.name for field in CMSBlock._meta.get_fields() if field.name.startswith("text_")]

    for old_key, new_key in LEGACY_KEY_MAP.items():
        try:
            block = CMSBlock.objects.get(key=old_key)
        except CMSBlock.DoesNotExist:
            continue

        existing_target = CMSBlock.objects.filter(key=new_key).exclude(pk=block.pk).first()
        if existing_target:
            changed_fields = ["page"]
            existing_target.page = page_from_key(new_key)
            for text_field in text_fields:
                if not getattr(existing_target, text_field, "").strip() and getattr(block, text_field, "").strip():
                    setattr(existing_target, text_field, getattr(block, text_field))
                    changed_fields.append(text_field)
            existing_target.save(update_fields=changed_fields)
            block.delete()
            continue

        block.key = new_key
        block.page = page_from_key(new_key)
        block.save(update_fields=["key", "page"])

    for block in CMSBlock.objects.all():
        derived_page = page_from_key(block.key)
        if block.page != derived_page:
            block.page = derived_page
            block.save(update_fields=["page"])

    for key, text_en in SITEWIDE_DEFAULTS.items():
        page = page_from_key(key)
        block, created = CMSBlock.objects.get_or_create(
            key=key,
            defaults={"page": page, "text_en": text_en, "is_active": True},
        )
        if created:
            continue

        changed_fields = []
        if block.page != page:
            block.page = page
            changed_fields.append("page")
        if not getattr(block, "text_en", "").strip():
            block.text_en = text_en
            changed_fields.append("text_en")
        if changed_fields:
            block.save(update_fields=changed_fields)


def backward(apps, schema_editor):
    CMSBlock = apps.get_model("core", "CMSBlock")
    for new_key, old_key in {value: key for key, value in LEGACY_KEY_MAP.items()}.items():
        try:
            block = CMSBlock.objects.get(key=new_key)
        except CMSBlock.DoesNotExist:
            continue
        block.key = old_key
        block.page = "shared"
        block.save(update_fields=["key", "page"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_expand_cms_languages"),
    ]

    operations = [
        migrations.AddField(
            model_name="cmsblock",
            name="page",
            field=models.CharField(
                choices=[
                    ("home", "Homepage"),
                    ("about", "About"),
                    ("contact", "Contact"),
                    ("privacy", "Privacy"),
                    ("terms", "Terms"),
                    ("impressum", "Impressum"),
                    ("footer", "Footer"),
                    ("shared", "Shared / Global"),
                ],
                default="shared",
                max_length=20,
                verbose_name="page",
            ),
        ),
        migrations.AlterModelOptions(
            name="cmsblock",
            options={"ordering": ["page", "key"], "verbose_name": "CMS block", "verbose_name_plural": "CMS blocks"},
        ),
        migrations.RunPython(forward, backward),
    ]
