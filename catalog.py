#!/usr/bin/env python3
"""The real product catalogue.

Where this came from
--------------------
The client sent 57 links: 55 TikTok Shop short links, one Walmart product page
and one Shopify store. TikTok Shop product pages are region-locked and bounce a
non-US request to the TikTok homepage, so following the redirects to the end
gives you nothing.

The product data is in the FIRST redirect hop. The short link 301s to
shop.tiktok.com/us/pdp/<id> with an `og_info` query parameter carrying the
product title and its catalogue photo, and only then does the geo-check fire.
Capturing hop one instead of following the chain recovered 54 of the 55 links -
50 unique products, since four were sent twice.

`pid` is TikTok's product id. It is kept so a link can always be traced back to
the row it produced, and because it is what caught the four duplicates.

What is real and what is not
----------------------------
name, blurb  - written here from the supplier title AND the photo. Several
               supplier titles are keyword soup; two of them are actively
               misleading, so every photo was looked at before its copy was
               written. #1732512695746007279 arrived titled "Party Decor
               Supplies Party Decor Design Party Atmosphere Props Scene
               Decorations" and is, from the photo, a motion-activated musical
               witch's broom.
image        - the supplier's own catalogue photo, saved locally. The TikTok CDN
               URLs carry expiring signatures, so linking to them directly would
               have produced a store full of broken images within days.
price, was   - DELIBERATELY EMPTY. TikTok puts the price behind a captcha, and
               the selling price is the client's margin decision anyway, not a
               number to be copied. Fill in prices.csv and re-run the build.
rating       - DELIBERATELY ABSENT. Star ratings and review counts are not
               invented for real products going in front of real customers.
               The rating block hides itself until a review source exists.
"""

# Category -> the tile shown on the homepage. The slug names the product whose
# photo fronts that category.
CATEGORIES = [
    ("LED Masks", "Light-up masks and gloves, the ones that sell on video",
     "led-purge-mask-glow"),
    ("Lights & Candles", "Floating candles, fairy lights, lamps and flames",
     "floating-candles-20pc"),
    ("Yard & Outdoor", "Ghosts, cobwebs, cauldrons and projectors",
     "hanging-ghosts-3pack"),
    # Home & Decor and Accessories used to be fronted by the bat wall stickers
    # and the Ghostface phone case. Both turned out to be products the supplier
    # has stopped listing, and a category tile is the last place to advertise
    # something nobody can buy. Repointed to items that are in stock and priced.
    ("Home & Decor", "Bats, rugs, bathroom sets and skeleton ornaments",
     "boo-kitchen-rug-set"),
    ("Apparel", "Sweaters, cardigans, overalls and slippers",
     "skeleton-cardigan-black"),
    ("Accessories", "Phone cases, magnets, pet collars and car decor",
     "trick-or-treat-phone-case"),
]


def p(slug, name, cat, blurb, images, pid=None, source=None,
      price=None, was=None, note=None):
    return dict(slug=slug, name=name, cat=cat, blurb=blurb, images=images,
                pid=pid, source=source, price=price, was=was, note=note,
                badge=None)


TT = "https://www.tiktok.com/t/"

PRODUCTS = [

    # ---- LED Masks -------------------------------------------------------
    # The first four are Marvel character masks. They are listed here under
    # descriptive names on purpose - see the trademark note in the README.
    p("hero-mask-remote-ring",
      "Light-Up Hero Mask with Remote Ring",
      "LED Masks",
      "Moulded plastic mask with lenses that blink and glow on command. The ring "
      "on your finger does it, so nobody sees you trigger it.",
      ["1732418533687791722"], pid="1732418533687791722"),

    p("hero-helmet-11-scale",
      "1:1 Scale Spider Hero Helmet",
      "LED Masks",
      "Full-size wearable helmet with motorised expressive lenses and a "
      "rechargeable wireless control ring. The one people film.",
      ["1732473836252467306"], pid="1732473836252467306"),

    p("led-purge-mask-glow",
      "LED Skeleton Purge Mask",
      "LED Masks",
      "Glow-wire skeleton face that lights up the whole mask in the dark. "
      "The single most photographed thing at any Halloween party.",
      ["1731424671015342961"], pid="1731424671015342961"),

    p("white-hero-mask-remote",
      "White Spider Hero Mask with Remote Ring",
      "LED Masks",
      "The white and pink version, with the same remote-controlled moving "
      "lenses. Comes boxed, which makes it an easy gift.",
      ["1732489858479984746"], pid="1732489858479984746"),

    p("led-mask-gloves-set",
      "LED Mask & Gloves Set",
      "LED Masks",
      "Mask plus light-up gloves in one box, three glow modes. The gloves are "
      "what turn a costume into a video.",
      ["1732481492091375623"], pid="1732481492091375623"),

    p("led-mask-4-modes",
      "LED Halloween Mask, 4 Lighting Modes",
      "LED Masks",
      "Steady, slow flash, fast flash and sound-reactive, in a run of colours. "
      "Battery powered, adjustable strap, fits adults and teens.",
      ["1731630241751863458"], pid="1731630241751863458"),

    # ---- Lights & Candles ------------------------------------------------
    p("floating-candles-20pc",
      "20-Piece Floating Candles with Magic Wand Remote",
      "Lights & Candles",
      "Twenty candles that hang in mid-air and light up when you wave the wand. "
      "Flickering warm light, two modes and a timer.",
      ["1732390825505951751"], pid="1732390825505951751"),

    p("floating-candles-12pc",
      "12-Pack Floating Candles, Enchanted Set",
      "Lights & Candles",
      "The smaller set for a hallway or a single room, same wand remote. "
      "Boxed as a gift set.",
      ["1731727668536578928"], pid="1731727668536578928"),

    p("floating-candles-kidsafe",
      "Kid-Safe Floating LED Candles with Wand",
      "Lights & Candles",
      "No flame, no wax, no heat - safe to hang in a child's room. Wand "
      "remote and battery operated, so they work anywhere.",
      ["1730358444410442599"], pid="1730358444410442599"),

    p("pillar-candles-remote-3",
      "Flameless LED Pillar Candles, Set of 3",
      "Lights & Candles",
      "Orange pillars with witch and haunted-house cut-outs that throw a "
      "silhouette on the wall. Remote, timers, and waterproof for the porch.",
      ["1731402583668855258"], pid="1731402583668855258"),

    p("pumpkin-candle-holders-2",
      "Pumpkin Candle Holder Set with Remote",
      "Lights & Candles",
      "Two amber jack-o'-lanterns on black metal stands with flameless candles "
      "inside. A centrepiece that works on a mantel or a dinner table.",
      ["1732479239883821952"], pid="1732479239883821952"),

    p("solar-fairy-lights-80ft",
      "80ft Solar Fairy Lights, 2 Pack",
      "Lights & Candles",
      "240 LEDs across two 80ft runs, solar charged and waterproof, with 8 "
      "modes. No plug and no batteries to replace.",
      ["1732323770676646372"], pid="1732323770676646372"),

    p("halloween-tree-lights-black",
      "24in Black Halloween Tree Lights, 2 Pack",
      "Lights & Candles",
      "A pair of bare black trees strung with orange and purple lights. "
      "Battery or USB, so they sit anywhere indoors.",
      ["1731779035205046680"], pid="1731779035205046680"),

    p("halloween-tree-lights-24led",
      "24in Orange & Purple LED Tree, 2 Pack",
      "Lights & Candles",
      "24 LEDs per tree on a mantel, entryway or TV console. Warm orange "
      "with a purple wash.",
      ["1731319962524553624"], pid="1731319962524553624",
      note="Very close to halloween-tree-lights-black - check they are not the "
           "same item listed twice before you import both."),

    p("under-cabinet-rgb-bars",
      "RGB Under-Cabinet Light Bars",
      "Lights & Candles",
      "Magnetic rechargeable bars that stick under a shelf and wash the whole "
      "surface in colour. Remote and touch control, dimmable.",
      ["1729419464377733355"], pid="1729419464377733355"),

    p("retro-pumpkin-desk-lamp",
      "Retro Pumpkin & Bat Stained-Glass Desk Lamp",
      "Lights & Candles",
      "A Tiffany-style lamp with a pumpkin and bat shade. Reads as a real "
      "piece of decor rather than a decoration you put away in November.",
      ["1732468405322420678"], pid="1732468405322420678"),

    p("pumpkin-night-light-mini",
      "Mini Pumpkin Bedside Night Light",
      "Lights & Candles",
      "Soft silicone pumpkin with three brightness levels, rechargeable and "
      "touch controlled. Safe for a nursery.",
      ["1731541214379741272"], pid="1731541214379741272"),

    p("ghost-campfire-nightlight",
      "Ghost Campfire Plug-In Night Light",
      "Lights & Candles",
      "Two little ghosts toasting marshmallows over a flickering 3D flame. "
      "Plugs straight into the wall.",
      ["1732526605363679471"], pid="1732526605363679471"),

    # ---- Yard & Outdoor --------------------------------------------------
    p("hanging-ghosts-3pack",
      "Pre-Assembled Hanging Ghosts, 3 Pack",
      "Yard & Outdoor",
      "Three full-size ghosts that come out of the box ready to hang. No "
      "assembly, no frame to build - straight onto a tree or a porch.",
      ["1732479123041653632"], pid="1732479123041653632"),

    p("ghost-swing-5ft-remote",
      "5ft Hanging Ghost Swing with Remote Lights",
      "Yard & Outdoor",
      "Five feet of ghost with built-in string lights on a remote. Big enough "
      "to read from the street, which is the whole point.",
      ["1731498685935031168"], pid="1731498685935031168"),

    p("spider-web-kit-lights",
      "Spider Web Kit with 32ft String Lights",
      "Yard & Outdoor",
      "300 square feet of stretch cobweb, black creepy cloth, fake spiders and "
      "bats, plus 32ft of lights. Covers a whole porch in one go.",
      ["1732380853842055760"], pid="1732380853842055760"),

    p("glow-cobwebs-spiders",
      "Glow Stretch Cobwebs with Spiders & Bats",
      "Yard & Outdoor",
      "Fluorescent webbing in white, green, orange and purple that lifts under "
      "any blacklight. Indoor or outdoor.",
      ["1732380839248171600"], pid="1732380839248171600"),

    p("cauldron-fog-potion",
      "Glow Cauldron with Fog Diffuser & Potion Bottles",
      "Yard & Outdoor",
      "A cauldron that actually smokes. Glow-in-the-dark plastic, reusable "
      "floating bottles and a dense fog diffuser in the box.",
      ["1731405992869598011"], pid="1731405992869598011"),

    p("tripod-cauldron-fog",
      "Large Tripod Cauldron with Fog Maker",
      "Yard & Outdoor",
      "The big one, on a tripod, with a skeleton climbing out and a fog maker "
      "included. Built to sit on a patio or a porch step.",
      ["1732433818444534656"], pid="1732433818444534656"),

    p("laser-swamp-projector",
      "Waterproof Laser Swamp Light Projector",
      "Yard & Outdoor",
      "Throws a shifting green laser field across a lawn, and turns into a "
      "swamp when it catches low fog. IP67, so it stays out in the rain.",
      ["1729507617061443354"], pid="1729507617061443354",
      note="The listing states the fog machine is not included."),

    p("witch-broom-light-music",
      "Light-Up Musical Witch Broom",
      "Yard & Outdoor",
      "Motion-activated broom that lights up and plays when someone walks "
      "past. Hangs on a door or leans in a corner.",
      ["1732512695746007279"], pid="1732512695746007279",
      note="The supplier title for this one is pure keyword filler. Name and "
           "description were written from the photo."),

    # ---- Home & Decor ----------------------------------------------------
    p("bat-wall-stickers-160",
      "160-Piece 3D Bat Wall Stickers",
      "Home & Decor",
      "Seven sizes of removable PVC bats that peel off clean. The cheapest way "
      "to make a whole room look done.",
      ["1731565309586150122"], pid="1731565309586150122"),

    p("led-bats-purple-36",
      "36-Piece Purple LED 3D Bats",
      "Home & Decor",
      "Five sizes, four shapes, lit from within in purple. Waterproof, so they "
      "work on an outside window as well as a wall.",
      ["1731639820942611173"], pid="1731639820942611173"),

    p("bat-decals-lightup",
      "Light-Up 3D Bat Wall Decals",
      "Home & Decor",
      "Bendable bat, spider and butterfly shapes that stick bubble-free and "
      "light up. Battery powered, 12 or 24 to a set.",
      ["1731504941141823963"], pid="1731504941141823963"),

    p("garage-door-bat-magnets",
      "Glow Bat Garage Door Magnet Set",
      "Home & Decor",
      "Magnetic bats that turn a plain garage door into the front of a haunted "
      "house, and glow once it gets dark. Peel off in seconds afterwards.",
      ["1732380419069678160"], pid="1732380419069678160"),

    p("witch-bat-magnet-set",
      "Witch & Bat Car and Fridge Magnet Set",
      "Home & Decor",
      "Witches, cats, pumpkins and bats for a car door, a fridge or a garage. "
      "Glows in the dark. Made for trunk-or-treat.",
      ["1732380829367898704"], pid="1732380829367898704"),

    p("advent-calendar-31-nights",
      "31 Nights of Fright Advent Calendar",
      "Home & Decor",
      "A blind bag for every night of October - collectible mini figures, "
      "hanging charms and small decorations. Sells itself to anyone with kids.",
      ["1732568841926578908"], pid="1732568841926578908"),

    p("bathroom-set-vintage",
      "Vintage Halloween Bathroom Set",
      "Home & Decor",
      "Shower curtain with hooks, non-slip rugs and a toilet lid cover in one "
      "set. Turns the room people always end up in anyway.",
      ["1732380304815002394"], pid="1732380304815002394"),

    p("skeleton-vortex-rug",
      "Skeleton Vortex Illusion Round Rug",
      "Home & Decor",
      "A flat rug that reads as a hole in the floor. Soft polyester with a "
      "non-slip back, 16 inches.",
      ["1732569130693005832"], pid="1732569130693005832"),

    p("boo-kitchen-rug-set",
      "BOO! Kitchen Runner Rug Set, 2 Piece",
      "Home & Decor",
      "Two non-slip runners for a kitchen, hallway or laundry. Washable, and "
      "they sit flat rather than curling at the corners.",
      ["1732396566131610436"], pid="1732396566131610436"),

    p("ghost-candy-bowl-glow",
      "Glow Ghost Candy Bowl with Lights",
      "Home & Decor",
      "A draped ghost with a bowl in its middle and a lit interior on a timer "
      "and remote. Works on a porch step for trick-or-treaters.",
      ["1731587529111016320"], pid="1731587529111016320"),

    p("led-candy-totes",
      "LED Trick-or-Treat Candy Totes",
      "Home & Decor",
      "Reusable light-up buckets in pumpkin, ghost and skull faces. They glow, "
      "so a child stays visible after dark.",
      ["1731477056663163626"], pid="1731477056663163626"),

    p("skeleton-pumpkin-figures-3",
      "Skeleton Pumpkin Table Figures, Set of 3",
      "Home & Decor",
      "Three 5.75in skeletons with pumpkin heads. Small enough for a shelf, "
      "detailed enough to be worth looking at.",
      ["1731288742073832391"], pid="1731288742073832391"),

    p("resin-skeleton-ornament",
      "Sitting Skeleton Resin Ornament",
      "Home & Decor",
      "A resin skeleton that sits on a shelf edge with its legs hanging. Sold "
      "singly or as a set of three.",
      ["1731275150973047553"], pid="1731275150973047553"),

    p("dragon-book-corner-light",
      "3D Dragon Book Corner Light",
      "Home & Decor",
      "A fire-breathing dragon that clamps to a bookshelf, with a glowing "
      "simulated flame. Gothic rather than seasonal, so it stays up all year.",
      ["1732575108380004778"], pid="1732575108380004778"),

    p("splatmat-bloody-bath-mat",
      "SplatMat - Colour-Changing Bloody Bath Mat",
      "Home & Decor",
      "A plain white mat until it gets wet, then deep red splatters bloom "
      "across it and fade again as it dries. Reusable, every single time.",
      ["splatmat-1", "splatmat-3", "splatmat-4", "splatmat-5"],
      source="https://splatmatofficial.com/products/splatmat",
      price=21.99, was=34.99,
      note="The only product with a verified price, taken from its own store. "
           "Its fifth asset is an animated GIF whose still frame is 260px "
           "wide - too small for the gallery, so it is left out."),

    # ---- Apparel ---------------------------------------------------------
    p("skeleton-cardigan-black",
      "Black Skeleton Print Cardigan",
      "Apparel",
      "Button-front V-neck knit with a ribcage down the front and bones along "
      "the sleeves. Loose drop-shoulder fit.",
      ["1731455840876597258"], pid="1731455840876597258"),

    p("skeleton-cardigan-colours",
      "Skeleton Print Knit Cardigan",
      "Apparel",
      "The same ribcage knit in green, pink, cream and black. Long line, "
      "drop shoulder, worn open.",
      ["1731551826348642314"], pid="1731551826348642314",
      note="Very close to skeleton-cardigan-black - confirm these are two "
           "different listings before importing both."),

    p("skull-drop-shoulder-sweater",
      "Distressed Skull Drop-Shoulder Sweater",
      "Apparel",
      "Heavy black knit with a worn skull graphic and deliberate distressing. "
      "Streetwear first, Halloween second, so it sells past October.",
      ["1729445174659486539"], pid="1729445174659486539"),

    p("toddler-ghost-overalls",
      "Toddler Ghost & Pumpkin Corduroy Overalls",
      "Apparel",
      "Thick-wale corduroy dungarees with a ghost or a pumpkin on the bib, "
      "adjustable straps and real pockets. A costume they can actually wear.",
      ["1732511676532494495"], pid="1732511676532494495"),

    p("toddler-spooky-goose-sweater",
      "Toddler 'Spooky Goose' Knit Sweater",
      "Apparel",
      "Embroidered witch, pumpkin and ghost on a soft cream knit, 0-7 years. "
      "The kind of thing parents photograph.",
      ["1732456978943021928"], pid="1732456978943021928"),

    p("pumpkin-blanket-hoodie",
      "Oversized Pumpkin Blanket Hoodie",
      "Apparel",
      "Wearable fleece blanket covered in pumpkins and ghosts, one size over "
      "everything. The comfort buy of the season.",
      ["1729751715804254493"], pid="1729751715804254493"),

    p("pumpkin-skull-slippers",
      "Pumpkin & Skull Plush Slippers",
      "Apparel",
      "Faux fur slides with an embroidered pumpkin on the toe and a proper "
      "anti-slip rubber sole. Unisex.",
      ["1731084638623011296"], pid="1731084638623011296"),

    # ---- Accessories -----------------------------------------------------
    p("ghostface-phone-case",
      "Dripping Ghostface Phone Case",
      "Accessories",
      "Horror-film artwork on shockproof silicone with raised corners. Fits "
      "the iPhone 11 through 17 range.",
      ["1732303908418065098"], pid="1732303908418065098"),

    p("trick-or-treat-phone-case",
      "Trick-or-Treat Glitter Phone Case with Strap",
      "Accessories",
      "Clear glitter case with pumpkins, ghosts and cats behind the shine, "
      "plus a wrist strap. Four-corner drop protection, iPhone and Galaxy.",
      ["1732548582082187772"], pid="1732548582082187772"),

    p("pumpkin-dog-collar",
      "Pumpkin & Sunflower Dog Collar",
      "Accessories",
      "Adjustable autumn collar with a little pumpkin charm, in sizes for "
      "small through large dogs. The seasonal buy people make for the photo.",
      ["1731703860004098594"], pid="1731703860004098594"),

    p("scary-face-headrest-covers",
      "Scary Face Car Headrest Covers, 2 Pack",
      "Accessories",
      "Slip-on headrest covers with a printed scary face, sold as a pair. "
      "The face is 25cm / 9.84 inches, and the elastic hem stretches over the "
      "headrests in most cars, trucks and SUVs.",
      # Walmart's own four usable photos, in the order they are shown: fitted
      # in a dark car, the gag shot with the driver, the plain white-background
      # product shot, then the dimensioned diagram. Walmart's fifth image is a
      # marketing collage with headline text baked into it, so it is left out.
      ["2-Pack-Car-Headrest-Cover-Scary-Face",
       "111a815d-0764-471f-98bf-7f9d22db9dbb",
       "f7880027-0315-4d63-bd5a-66d580235d67",
       "a5c24527-924e-4201-8c1a-2294e06d06ac"],
      source="https://www.walmart.com/ip/2-Pack-Car-Headrest-Cover-Scary-Face-"
             "Printing-Car-Seat-Headrest-Cover-9-84in-2026-Funny-Face-Masque-"
             "Head-Rest-Protector-for-Auto-Vehicle-Truck/20212966534",
      note="Walmart refuses an ordinary browser request but answers a crawler, "
           "so this now has its four real photos and a verified source price."),
]

# What the SOURCE charges a shopper today. Not the client's cost, and not his
# selling price - a reference point, recorded so nobody has to take a number on
# trust. Every figure here was read off the seller's own page.
#
# For TikTok the figure is NOT from that product's own page. A TikTok product
# page masks its own price ("3*" instead of "31.99") and its JSON-LD repeats the
# masked value truncated to a bare integer, so a page priced at $31.99 reports
# "price": 3. Reading that as three dollars would have understated ten products
# by a factor of ten. The unmasked figure comes from the recommendation widgets
# on OTHER products' pages, parsed out of __MODERN_ROUTER_DATA__ as JSON so each
# price stays attached to the product it belongs to.
#
#   slug -> (price, was_price or None, where it was read)
# Every TikTok figure below was checked against an independent oracle before it
# was allowed in. Two families of source disagreed - prices read off the
# recommendation widgets of other products' pages, and prices read off the
# seller's own store page - and they disagreed on fifteen products, sometimes
# by a factor of three. The tie-break is the mask itself: a product page hides
# its price as "3*", which is useless for pricing and decisive for refuting, so
# a $54.99 claim against a "3*" mask is simply thrown out. That killed fifteen
# wrong figures, including one case where the widgets agreed with each other
# and were still wrong ($9.11 against a "1*" mask; the real price is $19.09).
# Six more products had two candidates that both fit the mask and are left
# unpriced rather than guessed.
SOURCE_PRICES = {
    "white-hero-mask-remote":      (49.00, None,  "tiktok"),
    "hero-mask-remote-ring":       (45.99, None,  "tiktok"),
    "ghost-swing-5ft-remote":      (35.99, 85.99, "tiktok"),
    "tripod-cauldron-fog":         (31.99, 71.99, "tiktok"),
    "pumpkin-blanket-hoodie":      (30.99, 49.99, "tiktok"),
    "led-candy-totes":             (28.04, 50.99, "tiktok"),
    "skeleton-cardigan-colours":   (25.99, 39.98, "tiktok"),
    "skull-drop-shoulder-sweater": (24.27, 47.59, "tiktok"),
    "hanging-ghosts-3pack":        (23.99, None,  "tiktok"),
    "witch-broom-light-music":     (23.88, 49.99, "tiktok"),
    "pillar-candles-remote-3":     (23.14, 39.90, "tiktok"),
    "ghost-candy-bowl-glow":       (19.99, 49.99, "tiktok"),
    "advent-calendar-31-nights":   (19.49, 39.00, "tiktok"),
    "resin-skeleton-ornament":     (19.09, None,  "tiktok"),
    "toddler-ghost-overalls":      (17.03, None,  "tiktok"),
    "trick-or-treat-phone-case":   (16.87, 33.75, "tiktok"),
    "boo-kitchen-rug-set":         (16.84, None,  "tiktok"),
    "ghost-campfire-nightlight":   (12.99, 25.99, "tiktok"),
    "witch-bat-magnet-set":        (12.86, 23.39, "tiktok"),
    "bat-decals-lightup":          (10.99, 15.99, "tiktok"),
    "scary-face-headrest-covers":  (1.99,   2.99, "walmart"),
    # 21.99/34.99, re-read from splatmatofficial.com/products/splatmat.js.
    # This entry first went in as 49.99/79.99, which was not from anywhere -
    # it was a number I remembered rather than one I fetched. The build caught
    # it only because the figure disagreed with the price already in the
    # product below, and a was_price under the sale price is a hard error here.
    # A remembered number is not a source.
    "splatmat-bloody-bath-mat":    (21.99, 34.99, "splatmatofficial.com"),
}

# Products whose TikTok page no longer loads AND which appear nowhere else.
#
# Not a guess from one failed request. Each of these returns {"code":100000} to
# every URL form - bare id and slug alike - in three separate runs hours apart,
# while other products served normally from the same browser seconds later. On
# top of that, none of them appears even once across 99 fetched pages: not in a
# single recommendation widget, not in their own seller's store listing, not in
# a category page.
#
# The sixteenth product that refuses its own page, white-hero-mask-remote, is
# NOT here: its seller lists it three times at $49.00, so it exists and only
# its product page is broken. That is the difference this list is careful to
# preserve.
#
# They are deliberately left on the site. All fifteen are unpriced, so the buy
# button is already switched off on every one of them - nothing can be ordered
# that cannot be fulfilled - and dropping a client's products because a scrape
# came back empty is his call to make, not mine.
UNAVAILABLE = {
    "floating-candles-kidsafe",
    "pumpkin-skull-slippers",
    "skeleton-pumpkin-figures-3",
    "pumpkin-night-light-mini",
    "bat-wall-stickers-160",
    "led-mask-4-modes",
    "pumpkin-dog-collar",
    "floating-candles-12pc",
    "halloween-tree-lights-black",
    "ghostface-phone-case",
    "garage-door-bat-magnets",
    "glow-cobwebs-spiders",
    "spider-web-kit-lights",
    "toddler-spooky-goose-sweater",
    "led-mask-gloves-set",
}


def check():
    """Fail loudly on a duplicate slug or a product with no name."""
    seen = set()
    for x in PRODUCTS:
        assert x["slug"] not in seen, f"duplicate slug {x['slug']}"
        assert x["name"] and x["blurb"], f"incomplete product {x['slug']}"
        seen.add(x["slug"])
    cats = {c[0] for c in CATEGORIES}
    for x in PRODUCTS:
        assert x["cat"] in cats, f"{x['slug']} has unknown category {x['cat']}"
    fronts = {c[2] for c in CATEGORIES}
    assert fronts <= seen, f"category tile points at a missing product: {fronts - seen}"

    # A typo in either table would silently do nothing - a price that never
    # reaches a product, or an unavailable flag on a slug that does not exist.
    stray = set(SOURCE_PRICES) - seen
    assert not stray, f"SOURCE_PRICES names products that do not exist: {stray}"
    stray = UNAVAILABLE - seen
    assert not stray, f"UNAVAILABLE names products that do not exist: {stray}"

    # Two category tiles are fronted by products the supplier has stopped
    # listing. The photo is saved locally so the tile still renders, but the
    # client should know he is advertising a section with a dead item on it.
    for name, _, front in CATEGORIES:
        if front in UNAVAILABLE:
            print(f"  ! category '{name}' is fronted by {front}, "
                  f"which the supplier no longer lists")
    return len(PRODUCTS)


if __name__ == "__main__":
    print(f"{check()} products, {len(CATEGORIES)} categories")
    for c in CATEGORIES:
        n = sum(1 for x in PRODUCTS if x["cat"] == c[0])
        print(f"  {c[0]:20} {n}")
    print(f"  no image: {sum(1 for x in PRODUCTS if not x['images'])}")
    print(f"  priced:   {sum(1 for x in PRODUCTS if x['price'])}")


# --------------------------------------------------------------------------
# Benefit bullets, per product.
#
# Written from the supplier listing and its photo. Every claim here appears in
# the source listing - sizes, counts, modes, materials, power. Nothing is
# extrapolated, and where a listing was vague the bullet stays vague too.
#
# Optional, like everything else: a product with no entry falls back to the
# sentences of its blurb, so this list can be extended one product at a time.
# --------------------------------------------------------------------------

BULLETS = {

"hero-mask-remote-ring": [
    "Lenses light up red and blue, and blink on command",
    "Controlled by a ring on your finger, not a switch on the mask",
    "Skin-friendly moulded plastic, 26 x 19 x 11cm",
],
"hero-helmet-11-scale": [
    "1:1 scale - a full-size wearable helmet, not a face mask",
    "Motorised lenses with dynamic eyeball and shutter control",
    "USB-C rechargeable, with a one-touch wireless control ring",
],
"led-purge-mask-glow": [
    "Glow wire outlines the whole skeleton face in the dark",
    "Lightweight with an adjustable strap - fits over a hood",
    "The single most filmed thing at any Halloween party",
],
"white-hero-mask-remote": [
    "The white and pink colourway, with the same moving lenses",
    "Wireless ring control, several lighting modes",
    "Arrives boxed, which makes it an easy gift",
],
"led-mask-gloves-set": [
    "Mask and light-up gloves together in one box",
    "Three glow modes, and the gloves are what make it read on video",
    "Sized for boys, girls and adults",
],
"led-mask-4-modes": [
    "Four modes: steady, slow flash, fast flash and sound-reactive",
    "Battery powered, so there is no cable to hide",
    "Adjustable strap, fits adults and teens",
],

"floating-candles-20pc": [
    "20 candles that hang in mid-air on clear line",
    "Wave the wand and they light - no reaching, no switches",
    "Flickering warm light, two modes and a built-in timer",
],
"floating-candles-12pc": [
    "12 candles - the right size for a hallway or a single room",
    "Same magic wand remote as the larger set",
    "Boxed as a gift set",
],
"floating-candles-kidsafe": [
    "No flame, no wax and no heat - safe in a child's room",
    "Wand remote controlled, battery operated",
    "Works for Christmas as well, so it is not a one-month buy",
],
"pillar-candles-remote-3": [
    "Set of three orange pillars with cut-out silhouettes",
    "Throws witch and haunted-house shapes onto the wall behind",
    "Remote, timer and waterproof, so they can go outside",
],
"pumpkin-candle-holders-2": [
    "Two amber jack-o'-lanterns on black metal stands",
    "Flameless candles inside, on a remote",
    "Made as a centrepiece - mantel, table or entryway",
],
"solar-fairy-lights-80ft": [
    "Two 80ft runs, 240 LEDs in total",
    "Solar charged and waterproof - no plug, no batteries",
    "8 lighting modes",
],
"halloween-tree-lights-black": [
    "A pair of bare black trees strung with orange and purple",
    "24 inches tall - sits on a console or a mantel",
    "Battery or USB powered",
],
"halloween-tree-lights-24led": [
    "24 LEDs per tree, warm orange with a purple wash",
    "24 inches tall, two to a set",
    "USB or battery, for indoor use",
],
"under-cabinet-rgb-bars": [
    "Magnetic bars that stick under a shelf and wash it in colour",
    "Rechargeable and dimmable, with remote and touch control",
    "Sold in packs of 4, 5 or 6",
],
"retro-pumpkin-desk-lamp": [
    "Stained-glass style shade with a pumpkin and bat pattern",
    "Reads as a real lamp, not a decoration you box up in November",
    "Warm vintage glow for a bedroom or living room",
],
"pumpkin-night-light-mini": [
    "Soft silicone pumpkin - squeezable and safe for a nursery",
    "Three brightness levels, touch controlled",
    "Rechargeable, so it can be carried around the house",
],
"ghost-campfire-nightlight": [
    "Two ghosts toasting marshmallows over a 3D flickering flame",
    "Plugs straight into the wall - no batteries",
    "Hand-painted resin, works through Christmas too",
],

"hanging-ghosts-3pack": [
    "Three full-size ghosts, pre-assembled out of the box",
    "No frame to build - straight onto a tree or a porch",
    "Larger than the usual pack, so they read from the street",
],
"ghost-swing-5ft-remote": [
    "Five feet of ghost - big enough to see from the road",
    "Built-in string lights on a remote control",
    "For a tree, porch, yard or garden",
],
"spider-web-kit-lights": [
    "300 square feet of stretch cobweb plus black creepy cloth",
    "32ft of string lights, fake spiders and bats included",
    "Covers a whole porch or doorway in one go",
],
"glow-cobwebs-spiders": [
    "Fluorescent webbing in white, green, orange and purple",
    "Lifts under any blacklight",
    "Fake spiders and bats included, indoor or outdoor",
],
"cauldron-fog-potion": [
    "A cauldron that actually smokes, using the fog diffuser inside",
    "Glow-in-the-dark plastic",
    "Reusable floating potion bottles and stickers in the box",
],
"tripod-cauldron-fog": [
    "The large one, standing on its own tripod",
    "Fog maker included - it makes the mist itself",
    "Built for a patio, porch step or driveway",
],
"laser-swamp-projector": [
    "Throws a shifting green laser field right across a lawn",
    "Turns into a swamp when it catches low-lying fog",
    "IP67 waterproof and 360-degree adjustable, so it stays out",
],
"witch-broom-light-music": [
    "Motion activated - it lights up and plays as someone walks past",
    "Hangs on a door or leans in a corner",
    "Lights, music and motion in one piece",
],

"bat-wall-stickers-160": [
    "160 bats across seven sizes",
    "Removable PVC that peels off without marking the wall",
    "The cheapest way to make a whole room look finished",
],
"led-bats-purple-36": [
    "36 bats in five sizes and four shapes, lit from within",
    "Purple LED glow",
    "Waterproof, so they work on an outside window too",
],
"bat-decals-lightup": [
    "Bendable bat, spider and butterfly shapes",
    "Stick bubble-free on walls, windows and doors",
    "Battery powered, 12 or 24 to a set",
],
"garage-door-bat-magnets": [
    "Magnets, so the whole set peels off in seconds afterwards",
    "Turns a plain garage door into the front of a haunted house",
    "Glows once it gets dark",
],
"witch-bat-magnet-set": [
    "Witches, cats, pumpkins and bats",
    "For a car door, a fridge or a garage door",
    "Glow-in-the-dark - made for trunk-or-treat",
],
"advent-calendar-31-nights": [
    "A blind bag for every night of October, 31 in total",
    "Collectible mini figures, hanging charms and small decorations",
    "Sells itself to anyone with children",
],
"bathroom-set-vintage": [
    "Shower curtain with hooks, non-slip rugs and a lid cover",
    "One set does the whole room",
    "Vintage skeleton, pumpkin, witch and ghost print",
],
"skeleton-vortex-rug": [
    "A flat rug that reads as a hole in the floor",
    "16 inches across, soft polyester",
    "Non-slip backing, for indoor use",
],
"boo-kitchen-rug-set": [
    "Two non-slip runners - kitchen, hallway or laundry",
    "Machine washable",
    "They lie flat rather than curling at the corners",
],
"ghost-candy-bowl-glow": [
    "A draped ghost with the candy bowl in its middle",
    "Lights inside, on a timer and a remote",
    "Sits on a porch step for trick-or-treaters",
],
"led-candy-totes": [
    "Reusable light-up totes - pumpkin, ghost and skull faces",
    "They glow, so a child stays visible after dark",
    "Non-woven and washable, 3 or 4 to a pack",
],
"skeleton-pumpkin-figures-3": [
    "Three figures, 5.75 inches tall",
    "Skeleton bodies with pumpkin heads",
    "Small enough for a shelf, detailed enough to look at",
],
"resin-skeleton-ornament": [
    "Sits on a shelf edge with its legs hanging over",
    "Cast resin, hand finished",
    "Sold singly or as a set of three",
],
"dragon-book-corner-light": [
    "Clamps onto the corner of a bookshelf",
    "Glowing simulated flame from the dragon's mouth",
    "Gothic rather than seasonal - it stays up all year",
],
"splatmat-bloody-bath-mat": [
    "Plain white when dry, blood-spattered the moment it gets wet",
    "The effect comes back every single time it dries out",
    "Non-slip backing and machine washable",
],

"skeleton-cardigan-black": [
    "Ribcage down the front, bones along both sleeves",
    "Button-front V-neck in a loose drop-shoulder fit",
    "Soft knit, multiple sizes",
],
"skeleton-cardigan-colours": [
    "The same ribcage knit in green, pink, cream and black",
    "Long line, drop shoulder, made to be worn open",
    "Unisex sizing",
],
"skull-drop-shoulder-sweater": [
    "Heavy black knit with a worn skull graphic",
    "Deliberate distressing and a drop-shoulder cut",
    "Streetwear first - it sells well past October",
],
"toddler-ghost-overalls": [
    "Thick-wale corduroy with a ghost or a pumpkin on the bib",
    "Adjustable straps and real pockets",
    "A costume they can wear all autumn, not just once",
],
"toddler-spooky-goose-sweater": [
    "Embroidered witch, pumpkin and ghost, not a printed transfer",
    "Soft cream knit, sizes 0 to 7 years",
    "The kind of thing parents photograph",
],
"pumpkin-blanket-hoodie": [
    "A wearable fleece blanket covered in pumpkins and ghosts",
    "One size, goes on over everything",
    "Plus size friendly - the comfort buy of the season",
],
"pumpkin-skull-slippers": [
    "Faux fur slides with an embroidered pumpkin on the toe",
    "Proper anti-slip rubber sole, not fabric",
    "Unisex, for indoors or a quick trip outside",
],

"ghostface-phone-case": [
    "Horror-film dripping artwork on shockproof silicone",
    "Raised corners and a raised camera lip",
    "Fits the iPhone 11 through 17 range, Pro and Pro Max",
],
"trick-or-treat-phone-case": [
    "Clear glitter case with pumpkins, ghosts and cats behind it",
    "Four-corner drop protection and a non-yellowing shell",
    "iPhone and Samsung Galaxy, plus a wrist strap",
],
"pumpkin-dog-collar": [
    "Adjustable autumn print with a small pumpkin charm",
    "Sizes for small, medium and large dogs",
    "The seasonal buy people make just for the photo",
],
"scary-face-headrest-covers": [
    "Sold as a pair - both front headrests",
    "Roughly 9.84 inches, fits most cars, trucks and SUVs",
    "Slips straight on, no tools",
],
}
