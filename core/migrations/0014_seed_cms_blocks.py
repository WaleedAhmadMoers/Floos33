from django.db import migrations


CMS_DEFAULTS = {
    "hero_title": "The marketplace for EU overstock and MENA demand.",
    "hero_subtitle": "EU to MENA overstock and liquidation marketplace",
    "hero_description": "Browse approved listings, post RFQs, negotiate privately, and progress every deal under platform oversight with identity protection and verification.",
    "hero_cta_primary": "Browse marketplace",
    "hero_cta_secondary": "Browse RFQs",
    "hero_cta_primary_guest": "Create account",
    "hero_cta_secondary_guest": "Browse marketplace",
    "hero_badge_verified_users": "Verified users",
    "hero_badge_admin_approved": "Admin-approved listings",
    "hero_badge_identity_protection": "Identity protection",
    "hero_badge_controlled_deal_flow": "Controlled deal flow",
    "market_snapshot_title": "Market snapshot",
    "market_snapshot_active_suffix": "active",
    "market_snapshot_item_1_eyebrow": "Trending surplus",
    "market_snapshot_item_1_title": "Industrial tools and mixed pallets",
    "market_snapshot_item_1_description": "High-volume clearance inventory from verified EU suppliers.",
    "market_snapshot_item_1_tag": "MOQ flexible",
    "market_snapshot_item_2_eyebrow": "New liquidation",
    "market_snapshot_item_2_title": "Home and kitchen returns",
    "market_snapshot_item_2_description": "Fresh mixed-brand stock prepared for faster cross-border deals.",
    "market_snapshot_item_2_tag": "Fast moving",
    "market_snapshot_item_3_eyebrow": "Active RFQs",
    "market_snapshot_item_3_title": "Electronics clearance lots",
    "market_snapshot_item_3_description": "Buyers in MENA are actively looking for approved EU stock.",
    "market_snapshot_item_3_tag": "Respond now",
    "market_snapshot_view_all": "View all listings",
    "marketplace_section_title": "Marketplace",
    "marketplace_section_description": "Browse approved public listings that match your selected language.",
    "marketplace_filters_title": "Filters",
    "marketplace_reset": "Reset",
    "marketplace_categories_title": "Categories",
    "marketplace_all": "All",
    "marketplace_condition_title": "Condition",
    "marketplace_shortcuts_title": "Shortcuts",
    "marketplace_open_full": "Open full marketplace",
    "marketplace_saved_listings": "Saved listings",
    "marketplace_sign_in_to_save": "Sign in to save",
    "listing_no_preview": "No preview",
    "listing_admin_approved": "Admin approved",
    "listing_verified_user": "Verified user",
    "listing_view_details": "View details",
    "pagination_previous": "Previous",
    "pagination_next": "Next",
    "pagination_page": "Page",
    "pagination_of": "of",
    "marketplace_empty_state": "No listings yet.",
    "rfq_section_title": "Need something specific?",
    "rfq_section_description": "Post an RFQ and invite verified sellers to respond privately.",
    "rfq_cta_primary": "Post an RFQ",
    "rfq_cta_secondary": "Explore RFQs",
    "rfq_target_label": "Target:",
    "rfq_view_details": "View RFQ",
    "how_section_eyebrow": "Simple process",
    "how_section_title": "How the marketplace works",
    "how_section_description": "Four steps to start trading",
    "how_step_1_title": "Browse or post",
    "how_step_1_description": "Search approved stocklots or post an RFQ when you need specific specs or volume.",
    "how_step_2_title": "Connect privately",
    "how_step_2_description": "Chat with verified users while identities stay masked until reveal is approved.",
    "how_step_3_title": "Negotiate with oversight",
    "how_step_3_description": "Conversations and identity reveals are moderated before key trade steps move forward.",
    "how_step_4_title": "Confirm the deal",
    "how_step_4_description": "Both sides accept, admin approves, and progress is tracked with status and history.",
    "trust_section_eyebrow": "Trust and safety",
    "trust_section_title": "Verification and oversight built in",
    "trust_point_1_title": "Verified users",
    "trust_point_1_description": "Admin-verified accounts plus buyer and seller checks before sensitive actions.",
    "trust_point_2_title": "Approved listings and RFQs",
    "trust_point_2_description": "Only approved, active public content is visible to the right language audience.",
    "trust_point_3_title": "Identity protection",
    "trust_point_3_description": "Buyer and seller identities stay masked until reveal requests are approved.",
    "trust_point_4_title": "Controlled deal flow",
    "trust_point_4_description": "Deals move in stages with admin oversight, history, and notifications.",
    "cta_section_title": "Ready to start?",
    "cta_section_description": "Browse the marketplace or create your account to trade with verification and oversight.",
    "cta_section_primary": "Start browsing",
    "cta_section_secondary": "Create account",
    "footer_description": "A B2B marketplace for browsing stocklots, posting RFQs, and moving deals forward with stronger trust and structure.",
}


def seed_cms_blocks(apps, schema_editor):
    CMSBlock = apps.get_model("core", "CMSBlock")

    for key, text_en in CMS_DEFAULTS.items():
        CMSBlock.objects.update_or_create(
            key=key,
            defaults={
                "text_en": text_en,
                "is_active": True,
            },
        )


def unseed_cms_blocks(apps, schema_editor):
    CMSBlock = apps.get_model("core", "CMSBlock")
    CMSBlock.objects.filter(key__in=CMS_DEFAULTS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_cmsblock"),
    ]

    operations = [
        migrations.RunPython(seed_cms_blocks, unseed_cms_blocks),
    ]
