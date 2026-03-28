from django.db import migrations


CATEGORY_TREE = [
    (
        "automobile",
        "Automobile",
        [
            ("car-care-accessories", "Car care & accessories"),
            ("tires", "Tires"),
            ("auto-parts-accessories", "Auto parts & accessories"),
            ("car-audio", "Car audio"),
            ("trucks", "Trucks"),
            ("motorcycles-quads", "Motorcycles / Quads"),
            ("passenger-cars", "Passenger cars"),
        ],
    ),
    (
        "baby-kids",
        "Baby & Kids",
        [
            ("baby-products", "Baby products"),
            ("toys", "Toys"),
        ],
    ),
    (
        "construction-industry",
        "Construction & Industry",
        [
            ("construction-machinery", "Construction & industrial machinery"),
            ("diy-decoration", "DIY / decoration"),
            ("building-materials", "Building materials"),
            ("workwear-safety", "Workwear / safety"),
            ("fuels", "Fuels"),
            ("power-tools", "Power tools"),
            ("photovoltaics", "Photovoltaics"),
            ("sanitary-fittings", "Sanitary fittings"),
            ("generators", "Generators"),
            ("tools", "Tools"),
        ],
    ),
    (
        "clothing",
        "Clothing",
        [
            ("accessories", "Accessories"),
            ("baby-kids-clothing", "Baby & kids clothing"),
            ("swimwear", "Swimwear"),
            ("mixed-clothing-lots", "Mixed clothing lots"),
            ("womens-clothing", "Women's clothing"),
            ("used-clothing", "Used clothing"),
            ("handbags", "Handbags"),
            ("mens-clothing", "Men's clothing"),
            ("sunglasses", "Sunglasses"),
            ("underwear-nightwear", "Underwear / nightwear"),
        ],
    ),
    (
        "large-home-appliances",
        "Large Home Appliances",
        [
            ("ovens-cookers", "Ovens / cookers"),
            ("dishwashers", "Dishwashers"),
            ("fridges-freezers", "Fridges / freezers"),
            ("other-large-appliances", "Other large appliances"),
            ("washing-machines-dryers", "Washing machines / dryers"),
        ],
    ),
    (
        "small-home-appliances",
        "Small Home Appliances",
        [
            ("irons", "Irons"),
            ("coffee-machines", "Coffee machines"),
            ("microwaves", "Microwaves"),
            ("other-small-appliances", "Other small appliances"),
            ("vacuum-cleaners", "Vacuum cleaners"),
            ("toasters-sandwich-makers", "Toasters / sandwich makers"),
        ],
    ),
    (
        "phones-telephony",
        "Phones / Smartphones / Telephony",
        [
            ("landline-phones", "Landline phones"),
            ("phone-accessories", "Phone accessories"),
            ("smartphones-mobile-phones", "Smartphones / mobile phones"),
        ],
    ),
    (
        "home-garden-office",
        "Home / Garden / Office",
        [
            ("bathroom-accessories", "Bathroom accessories"),
            ("office-school-supplies", "Office & school supplies"),
            ("decoration-gifts-seasonal", "Decoration / gifts / seasonal goods"),
            ("garden-supplies", "Garden supplies"),
            ("home-textiles", "Home textiles"),
            ("kitchen-accessories", "Kitchen accessories"),
            ("lamps-lighting", "Lamps & lighting"),
            ("cleaning-products", "Cleaning products"),
            ("pet-supplies", "Pet supplies"),
        ],
    ),
    (
        "bankruptcy-liquidation",
        "Bankruptcy / Liquidation / Store Closure",
        [
            ("hotel-gastronomy-supplies", "Hotel / gastronomy supplies"),
            ("misc-liquidation-stock", "Misc liquidation stock"),
            ("insolvency-auctions", "Insolvency auctions"),
            ("store-equipment", "Store equipment"),
            ("warehouse-auctions", "Warehouse auctions"),
        ],
    ),
    (
        "food-beverage",
        "Food & Beverage",
        [
            ("drinks", "Drinks"),
            ("short-dated-products", "Short-dated products"),
            ("food", "Food"),
        ],
    ),
    (
        "multimedia-electronics",
        "Multimedia & Electronics",
        [
            ("computers", "Computers"),
            ("computer-parts", "Computer parts"),
            ("computer-accessories", "Computer accessories"),
            ("cameras-camcorders", "Cameras / camcorders"),
            ("printers", "Printers"),
            ("tvs", "TVs"),
            ("hifi-audio", "HiFi / audio"),
            ("monitors", "Monitors"),
            ("multimedia", "Multimedia"),
            ("navigation", "Navigation"),
            ("laptops-tablets", "Laptops / tablets"),
            ("electronics-pallets", "Electronics pallets"),
            ("game-consoles-games", "Game consoles / games"),
        ],
    ),
    (
        "furniture",
        "Furniture",
        [
            ("office-furniture", "Office furniture"),
            ("garden-furniture", "Garden furniture"),
            ("living-bedroom-kitchen-bathroom", "Living room / bedroom / kitchen / bathroom"),
        ],
    ),
    (
        "shoes",
        "Shoes",
        [
            ("womens-shoes", "Women's shoes"),
            ("mens-shoes", "Men's shoes"),
            ("childrens-shoes", "Children's shoes"),
            ("mixed-shoe-lots", "Mixed shoe lots"),
        ],
    ),
    (
        "sports-leisure",
        "Sports & Leisure",
        [
            ("bikes-scooters-accessories", "Bikes / scooters / accessories"),
            ("misc-sports-products", "Misc sports products"),
            ("sports-accessories", "Sports accessories"),
            ("sports-clothing", "Sports clothing"),
            ("fitness-equipment", "Fitness equipment"),
            ("sports-shoes", "Sports shoes"),
            ("beach-swimming-accessories", "Beach / swimming accessories"),
        ],
    ),
    (
        "watches-jewelry",
        "Watches & Jewelry",
        [
            ("jewelry", "Jewelry"),
            ("smartwatches", "Smartwatches"),
            ("watches", "Watches"),
        ],
    ),
    (
        "wellness-beauty",
        "Wellness & Beauty",
        [
            ("haircare", "Haircare"),
            ("hygiene-products", "Hygiene products"),
            ("cosmetic-accessories", "Cosmetic accessories"),
            ("cosmetics-makeup", "Cosmetics / makeup"),
            ("personal-care", "Personal care"),
            ("perfume", "Perfume"),
            ("ppe", "PPE"),
            ("wellness", "Wellness"),
        ],
    ),
    (
        "bazar",
        "Bazar",
        [],
    ),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("stocklots", "Category")

    Category.objects.all().update(is_active=False)

    for parent_slug, parent_name, children in CATEGORY_TREE:
        parent, _created = Category.objects.update_or_create(
            slug=parent_slug,
            defaults={"name": parent_name, "parent": None, "is_active": True},
        )
        for child_slug, child_name in children:
            Category.objects.update_or_create(
                slug=child_slug,
                defaults={"name": child_name, "parent": parent, "is_active": True},
            )


def reverse_seed_categories(apps, schema_editor):
    Category = apps.get_model("stocklots", "Category")
    slugs = []
    for parent_slug, _parent_name, children in CATEGORY_TREE:
        slugs.append(parent_slug)
        slugs.extend(child_slug for child_slug, _child_name in children)
    Category.objects.filter(slug__in=slugs).update(is_active=False)


class Migration(migrations.Migration):
    dependencies = [
        ("stocklots", "0003_alter_stocklot_price"),
    ]

    operations = [
        migrations.RunPython(seed_categories, reverse_seed_categories),
    ]
