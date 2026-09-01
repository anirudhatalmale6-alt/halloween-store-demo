#!/usr/bin/env python3
"""
Hollow & Hex - demo Halloween storefront generator.

Run:  python3 build.py
Emits index.html plus the product artwork in assets/products/.

Everything a client normally wants to change lives in PRODUCTS / CATEGORIES /
REVIEWS below. Add a dict, re-run, done.
"""

import os
import html

HERE = os.path.dirname(os.path.abspath(__file__))
ART_DIR = os.path.join(HERE, "assets", "products")

BRAND = "Hollow & Hex"
TAGLINE = "Haunt Your House. Ship It Free."

# --------------------------------------------------------------------------
# Product artwork. Hand-drawn SVG rather than stock photography so the demo
# is entirely ours - no licensing questions, and it stays on-palette.
# --------------------------------------------------------------------------

ORANGE = "#ff7518"
GREEN = "#7bff6a"
BONE = "#f4efe6"
PURPLE = "#a06bff"


# A bat silhouette centred on 0,0 - spans roughly 120 wide, 40 tall.
# Built from primitives rather than one clever path: each wing is a triangle
# whose bottom edge curves back up twice, which is what makes it read as a bat.
# Reused at several scales; place it with a <g transform="translate(x y) scale(s)">.
BAT = ("""<path d="M7-8 58-18 50 12Q40-2 30 6 18-4 7 4Z"/>"""
       """<path d="M-7-8-58-18-50 12Q-40-2-30 6-18-4-7 4Z"/>"""
       """<ellipse cy="-2" rx="9" ry="14"/>"""
       """<path d="M-6-14-8-24 0-18Z"/><path d="M6-14 8-24 0-18Z"/>""")


# A handprint centred on 0,0 - palm plus four fingers and a thumb, each swung
# around the palm centre so the splay looks natural rather than combed.
HAND = ("""<ellipse cy="8" rx="46" ry="52"/>"""
        """<rect x="-8" y="-108" width="18" height="74" rx="9" transform="rotate(-26)"/>"""
        """<rect x="-9" y="-120" width="19" height="84" rx="9.5" transform="rotate(-9)"/>"""
        """<rect x="-9" y="-116" width="19" height="80" rx="9.5" transform="rotate(8)"/>"""
        """<rect x="-8" y="-102" width="18" height="68" rx="9" transform="rotate(24)"/>"""
        """<rect x="-10" y="-98" width="20" height="56" rx="10" transform="rotate(-64)"/>""")


def art(label, glow, body):
    """Hold a piece of artwork as data so it can be re-staged three ways.

    Returns the raw parts rather than finished SVG - the product landing pages
    need a gallery, and a gallery of the same picture three times is a lie. The
    renderers below put the SAME body on three different stages instead.
    """
    return (label, glow, body)


def render_main(label, glow, body):
    """The catalogue shot: subject centred on a soft radial glow."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" role="img" aria-label="{label}">
<defs>
<radialGradient id="g" cx="50%" cy="46%" r="52%">
<stop offset="0%" stop-color="{glow}" stop-opacity=".55"/>
<stop offset="55%" stop-color="{glow}" stop-opacity=".14"/>
<stop offset="100%" stop-color="{glow}" stop-opacity="0"/>
</radialGradient>
</defs>
<rect width="600" height="600" fill="none"/>
<circle cx="300" cy="280" r="250" fill="url(#g)"/>
{body}
</svg>
"""


def render_detail(label, glow, body):
    """The close-up: same subject scaled about the centre, so the viewBox crops
    it. Genuinely a different view - you can read detail here that the catalogue
    shot is too small to show."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" role="img" aria-label="{label} detail">
<defs>
<radialGradient id="g" cx="50%" cy="42%" r="58%">
<stop offset="0%" stop-color="{glow}" stop-opacity=".6"/>
<stop offset="60%" stop-color="{glow}" stop-opacity=".16"/>
<stop offset="100%" stop-color="{glow}" stop-opacity="0"/>
</radialGradient>
</defs>
<circle cx="300" cy="260" r="290" fill="url(#g)"/>
<!-- 1.34, not 1.6. A harder zoom cropped the legs off the spider and the head
     off the dog, and a close-up you cannot identify is worse than no close-up -->
<g transform="translate(300 262) scale(1.34) translate(-300 -280)">
{body}
</g>
</svg>
"""


def render_scene(label, glow, body):
    """The in-situ shot: same subject on a night porch - moon, fence, ground.
    Scaled down and lifted so the fence reads as behind it."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" role="img" aria-label="{label} in use">
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#191233"/>
<stop offset="100%" stop-color="#0b0810"/>
</linearGradient>
<radialGradient id="moon" cx="50%" cy="50%" r="50%">
<stop offset="0%" stop-color="#fff6d8" stop-opacity=".5"/>
<stop offset="100%" stop-color="#fff6d8" stop-opacity="0"/>
</radialGradient>
<radialGradient id="g" cx="50%" cy="50%" r="50%">
<stop offset="0%" stop-color="{glow}" stop-opacity=".5"/>
<stop offset="100%" stop-color="{glow}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="back" cx="50%" cy="50%" r="50%">
<stop offset="0%" stop-color="{glow}" stop-opacity=".3"/>
<stop offset="55%" stop-color="{glow}" stop-opacity=".12"/>
<stop offset="100%" stop-color="{glow}" stop-opacity="0"/>
</radialGradient>
</defs>
<rect width="600" height="600" fill="url(#sky)"/>
<circle cx="472" cy="118" r="120" fill="url(#moon)"/>
<circle cx="472" cy="118" r="44" fill="#f6eecd"/>
<circle cx="458" cy="104" r="9" fill="#e4d9b0"/>
<circle cx="488" cy="132" r="6" fill="#e4d9b0"/>
<g fill="#f4efe6" opacity=".55">
<circle cx="86" cy="86" r="2.6"/><circle cx="168" cy="52" r="2"/><circle cx="252" cy="106" r="2.4"/>
<circle cx="54" cy="182" r="2"/><circle cx="340" cy="64" r="2.2"/><circle cx="562" cy="228" r="2"/>
</g>
<path d="M0 214 62 214 62 150 108 118 154 150 154 214 236 214 236 260 0 260Z" fill="#0a0713"/>
<g stroke="#0a0713" stroke-width="13" stroke-linecap="round">
<path d="M-4 344v112M40 330v126M84 344v112M128 330v126"/>
<path d="M472 330v126M516 344v112M560 330v126M604 344v112"/>
</g>
<path d="M-10 386h180M-10 424h180M430 386h180M430 424h180" stroke="#0a0713" stroke-width="11"/>
<!-- a soft light behind the subject, in the product's own glow colour. Several
     pieces are drawn as dark silhouettes (the spider's legs, the reaper's arms)
     and vanish against a night sky with nothing behind them. It has to be a
     gradient - a flat ellipse at low opacity renders as a visible grey disc -->
<ellipse cx="300" cy="336" rx="270" ry="248" fill="url(#back)"/>
<ellipse cx="300" cy="512" rx="215" ry="46" fill="url(#g)"/>
<g transform="translate(300 356) scale(.74) translate(-300 -300)">
{body}
</g>
<path d="M0 508h600v92H0z" fill="#08060e"/>
<path d="M0 508q150-18 300 0t300-14v14H0z" fill="#0d0a18"/>
<g fill="#08060e">
<path d="M92 508q10-30 22-30t20 30z"/><path d="M486 508q9-26 19-26t18 26z"/>
</g>
</svg>
"""


VIEWS = (("", render_main), ("-detail", render_detail), ("-scene", render_scene))


ARTWORK = {

"animatronic-reaper": art("Animatronic reaper", PURPLE, f"""
<path d="M470 92 404 500" stroke="#6b5540" stroke-width="15" stroke-linecap="round"/>
<path d="M470 92c60 8 98 46 106 100-56-44-96-52-124-38z" fill="{BONE}"/>
<path d="M196 268 118 350M404 268l78 82" stroke="#241a33" stroke-width="34" stroke-linecap="round"/>
<path d="M300 96c-66 0-108 44-108 106 0 26 6 44 6 62l-48 236 32-38 28 38 28-38 28 38 28-38 28 38 28-38 32 38-48-236c0-18 6-36 6-62 0-62-42-106-108-106z"
      fill="#241a33" stroke="{PURPLE}" stroke-width="7" stroke-linejoin="round"/>
<ellipse cx="300" cy="200" rx="66" ry="76" fill="#05040a"/>
<path d="M300 150c-31 0-51 22-51 53 0 18 8 31 18 39v20c0 8 6 13 14 13h38c8 0 14-5 14-13v-20c10-8 18-21 18-39 0-31-20-53-51-53z" fill="{BONE}"/>
<ellipse cx="282" cy="201" rx="13" ry="15" fill="{GREEN}"/>
<ellipse cx="318" cy="201" rx="13" ry="15" fill="{GREEN}"/>
<path d="M300 216l-8 15h16z" fill="#05040a"/>
<g stroke="#05040a" stroke-width="3.5"><path d="M288 244v14M300 244v14M312 244v14"/></g>
"""),

"fog-machine": art("Fog machine", GREEN, f"""
<defs><filter id="fb" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="22"/></filter></defs>
<g fill="{GREEN}" filter="url(#fb)">
<g opacity=".2"><circle cx="150" cy="296" r="58"/><circle cx="452" cy="292" r="60"/><circle cx="300" cy="316" r="80"/></g>
<g opacity=".26"><circle cx="202" cy="252" r="70"/><circle cx="294" cy="222" r="92"/><circle cx="394" cy="250" r="74"/><circle cx="246" cy="292" r="60"/><circle cx="352" cy="290" r="62"/></g>
<g opacity=".3"><circle cx="256" cy="180" r="42"/><circle cx="348" cy="188" r="34"/><circle cx="300" cy="152" r="30"/></g>
</g>
<rect x="164" y="352" width="272" height="140" rx="18" fill="#191324" stroke="{GREEN}" stroke-width="8"/>
<rect x="196" y="384" width="112" height="44" rx="8" fill="#07060a"/>
<circle cx="352" cy="406" r="20" fill="{ORANGE}"/>
<circle cx="404" cy="406" r="20" fill="{GREEN}"/>
<rect x="196" y="446" width="208" height="12" rx="6" fill="{GREEN}" opacity=".45"/>
<path d="M436 400h74a20 20 0 0 1 20 20v34" stroke="#4b4160" stroke-width="12" fill="none" stroke-linecap="round"/>
"""),

"hanging-ghost": art("Hanging ghost", BONE, f"""
<path d="M300 60v72" stroke="#584a6b" stroke-width="7"/>
<path d="M300 128c-84 0-136 62-136 148v242l40-46 38 46 38-46 40 46 38-46 40 46 38-46V276c0-86-52-148-136-148z"
      fill="{BONE}" opacity=".93"/>
<ellipse cx="256" cy="276" rx="21" ry="27" fill="#0b0810"/>
<ellipse cx="344" cy="276" rx="21" ry="27" fill="#0b0810"/>
<ellipse cx="300" cy="352" rx="29" ry="37" fill="#0b0810"/>
"""),

"pet-costume": art("Pet skeleton costume", ORANGE, f"""
<g fill="{ORANGE}">
<path d="M174 322q-56-14-50-74 4-30 30-28 18 2 14 26-6 34 28 44z"/>
<rect x="200" y="378" width="30" height="100" rx="15"/>
<rect x="252" y="378" width="30" height="100" rx="15"/>
<rect x="336" y="378" width="30" height="100" rx="15"/>
<rect x="388" y="378" width="30" height="100" rx="15"/>
<rect x="168" y="264" width="256" height="134" rx="63"/>
<ellipse cx="452" cy="282" rx="70" ry="66"/>
<path d="M496 260h58a22 22 0 0 1 0 44h-58z"/>
<path d="M416 226q-30-46 2-64t50 38z"/>
</g>
<circle cx="556" cy="282" r="11" fill="#2a1405"/>
<circle cx="466" cy="264" r="11" fill="#2a1405"/>
<g stroke="{BONE}" stroke-width="11" stroke-linecap="round" fill="none">
<!-- ribs bow, they do not run straight down. Straight bars read as a picket
     fence at any size above a thumbnail - the curve is what makes it a ribcage -->
<path d="M206 292q-15 42 0 82M244 286q-16 45 0 88M282 284q-17 47 0 92M320 284q-17 47 0 92M358 286q-16 45 0 88M394 292q-15 42 0 82"/>
<path d="M190 330q108-15 216 0"/>
</g>
"""),

"projector-lamp": art("Halloween projector lamp", PURPLE, f"""
<path d="M206 262 540 130v340L206 338z" fill="{PURPLE}" opacity=".2"/>
<rect x="86" y="238" width="132" height="124" rx="24" fill="#191324" stroke="{PURPLE}" stroke-width="8"/>
<circle cx="216" cy="300" r="34" fill="#07060a" stroke="{PURPLE}" stroke-width="7"/>
<circle cx="216" cy="300" r="14" fill="{GREEN}"/>
<path d="M152 362v56h-40M152 418h80" stroke="#4b4160" stroke-width="12" fill="none" stroke-linecap="round"/>
<g fill="{BONE}" opacity=".88">
<g transform="translate(408 200) scale(.85)">{BAT}</g>
<g transform="translate(468 306) scale(1.15)">{BAT}</g>
<g transform="translate(414 408) scale(.7)">{BAT}</g>
</g>
"""),

"window-clings": art("Bloody handprint clings", "#e02c2c", f"""
<rect x="120" y="96" width="360" height="408" rx="12" fill="#0d0a14" stroke="#4b4160" stroke-width="10"/>
<path d="M300 96v408M120 300h360" stroke="#4b4160" stroke-width="8"/>
<g fill="#c81f1f" transform="translate(310 356)">{HAND}</g>
<g fill="#c81f1f" opacity=".5" transform="translate(196 214) rotate(-18) scale(.5)">{HAND}</g>
"""),

"pumpkin-lights": art("LED pumpkin string lights", ORANGE, f"""
<path d="M40 150q140 120 260 0t260 120" stroke="#4b4160" stroke-width="9" fill="none"/>
<g>
<g transform="translate(112 208)">
<ellipse rx="52" ry="46" fill="{ORANGE}"/>
<path d="M-4-46v-22h8v22z" fill="#4c7a2a"/>
<path d="M-26-6 -14 12h-24zM26-6 38 12H14zM-24 22q24 20 48 0z" fill="#2a1405"/>
</g>
<g transform="translate(300 300)">
<ellipse rx="62" ry="54" fill="{ORANGE}"/>
<path d="M-5-54v-26h10v26z" fill="#4c7a2a"/>
<path d="M-31-8-17 14h-28zM31-8 45 14H17zM-28 26q28 24 56 0z" fill="#2a1405"/>
</g>
<g transform="translate(492 366)">
<ellipse rx="52" ry="46" fill="{ORANGE}"/>
<path d="M-4-46v-22h8v22z" fill="#4c7a2a"/>
<path d="M-26-6-14 12h-24zM26-6 38 12H14zM-24 22q24 20 48 0z" fill="#2a1405"/>
</g>
</g>
"""),

"reaper-costume": art("Grim reaper costume", GREEN, f"""
<path d="M300 70c-15 0-26 11-26 24 0 9 5 14 12 18l14 8" stroke="#8a7f96" stroke-width="8" fill="none" stroke-linecap="round"/>
<path d="M160 158 300 112l140 46" stroke="#8a7f96" stroke-width="10" fill="none" stroke-linejoin="round" stroke-linecap="round"/>
<path d="M212 226 124 306M388 226l88 80" stroke="#221a30" stroke-width="32" stroke-linecap="round"/>
<path d="M300 124c-58 0-96 34-96 90 0 24 6 40 6 58l-42 226 30-34 26 34 26-34 24 34 24-34 26 34 26-34 30 34-42-226c0-18 6-34 6-58 0-56-38-90-96-90z"
      fill="#221a30" stroke="{GREEN}" stroke-width="8" stroke-linejoin="round"/>
<ellipse cx="300" cy="196" rx="56" ry="62" fill="#05040a"/>
<ellipse cx="282" cy="196" rx="12" ry="15" fill="{GREEN}" opacity=".9"/>
<ellipse cx="318" cy="196" rx="12" ry="15" fill="{GREEN}" opacity=".9"/>
<path d="M232 316q68 26 136 0" stroke="{GREEN}" stroke-width="6" fill="none" opacity=".5"/>
"""),

"inflatable-spider": art("8ft inflatable spider", "#8b5cf6", f"""
<g stroke="#1b1425" stroke-width="20" fill="none" stroke-linecap="round">
<path d="M228 300 116 216 68 300M228 336 96 348 70 420M372 300l112-84 48 84M372 336l132 12 26 72"/>
<path d="M252 258 178 150l-70 26M348 258l74-108 70 26"/>
</g>
<ellipse cx="300" cy="352" rx="118" ry="98" fill="#241a36" stroke="#8b5cf6" stroke-width="8"/>
<ellipse cx="300" cy="242" rx="76" ry="64" fill="#2f2247" stroke="#8b5cf6" stroke-width="8"/>
<circle cx="272" cy="230" r="17" fill="{ORANGE}"/>
<circle cx="328" cy="230" r="17" fill="{ORANGE}"/>
<circle cx="250" cy="262" r="10" fill="{ORANGE}"/>
<circle cx="350" cy="262" r="10" fill="{ORANGE}"/>
"""),

"witch-cauldron": art("Bubbling witch cauldron", GREEN, f"""
<g fill="{GREEN}" opacity=".65">
<circle cx="262" cy="176" r="26"/><circle cx="336" cy="128" r="18"/>
<circle cx="316" cy="200" r="13"/><circle cx="222" cy="128" r="12"/>
</g>
<path d="M148 262h304c0 118-56 190-152 190s-152-72-152-190z" fill="#171021" stroke="{GREEN}" stroke-width="8"/>
<ellipse cx="300" cy="262" rx="152" ry="38" fill="#0d0a14" stroke="{GREEN}" stroke-width="8"/>
<ellipse cx="300" cy="266" rx="118" ry="26" fill="{GREEN}" opacity=".75"/>
<path d="M126 300a26 26 0 0 0 0 52M474 300a26 26 0 0 1 0 52" stroke="{GREEN}" stroke-width="10" fill="none"/>
<path d="M196 468h208" stroke="{ORANGE}" stroke-width="14" stroke-linecap="round"/>
<path d="M216 452q14-30 34 0M300 452q14-34 34 0" stroke="{ORANGE}" stroke-width="9" fill="none" stroke-linecap="round"/>
"""),
}


# --------------------------------------------------------------------------
# Catalogue
# --------------------------------------------------------------------------

PRODUCTS = [
    dict(slug="animatronic-reaper", name="Life-Size Animatronic Reaper",
         price=89.99, was=149.99, rating=4.8, reviews=412,
         badge="Best Seller",
         blurb="5ft 8in, motion-activated. Head turns, eyes light up, and it screams. The one the neighbours talk about."),
    dict(slug="fog-machine", name="1000W Fog Machine + LED Lights",
         price=49.99, was=79.99, rating=4.7, reviews=1284,
         badge="Best Seller",
         blurb="Fills a driveway in under a minute. Wireless remote, 12 colour LEDs, 1L tank."),
    dict(slug="hanging-ghost", name="Motion-Sensor Hanging Ghost",
         price=24.99, was=39.99, rating=4.6, reviews=903,
         badge=None,
         blurb="Drops, glows and shrieks when anyone walks under it. Hangs from any porch hook."),
    dict(slug="pet-costume", name="Glow Skeleton Dog Costume",
         price=18.99, was=29.99, rating=4.9, reviews=2107,
         badge="Viral on TikTok",
         blurb="Glow-in-the-dark ribcage, machine washable, sizes XS to XXL. Cats too."),
    dict(slug="projector-lamp", name="Halloween Projector Lamp",
         price=34.99, was=59.99, rating=4.5, reviews=658,
         badge=None,
         blurb="16 sliding scenes - bats, ghosts, spiders. Covers a whole house wall. Indoor or outdoor."),
    dict(slug="window-clings", name="Bloody Handprint Clings (24pc)",
         price=12.99, was=21.99, rating=4.4, reviews=531,
         badge="Under $15",
         blurb="Peel, stick, terrify. Leaves no residue and reuses year after year."),
    dict(slug="pumpkin-lights", name="LED Pumpkin String Lights (30ft)",
         price=19.99, was=32.99, rating=4.8, reviews=1749,
         badge=None,
         blurb="50 warm pumpkins, 8 lighting modes, USB or battery. Weatherproof."),
    dict(slug="reaper-costume", name="Hooded Grim Reaper Costume",
         price=44.99, was=74.99, rating=4.6, reviews=387,
         badge=None,
         blurb="Floor-length tattered robe, oversized hood, glowing eye insert included."),
    dict(slug="inflatable-spider", name="8ft Inflatable Yard Spider",
         price=59.99, was=99.99, rating=4.7, reviews=612,
         badge="Low Stock",
         blurb="Self-inflates in 40 seconds, lights from within, stakes and tethers included."),
    dict(slug="witch-cauldron", name="Bubbling Witch's Cauldron",
         price=29.99, was=49.99, rating=4.5, reviews=274,
         badge=None,
         blurb="Colour-changing mist bowl for the porch or the punch table. Just add water."),
]

# --------------------------------------------------------------------------
# Per-product landing page content.
#
# Everything here is optional. A product with no DETAILS entry still gets a
# complete landing page from the fallbacks in detail_for() - which matters,
# because when the real product list arrives I want name + price + photo to be
# enough to ship a page, and the rest to be an upgrade rather than a blocker.
# --------------------------------------------------------------------------

DETAILS = {

"animatronic-reaper": dict(
    hook="Your porch, but people cross the street to avoid it.",
    bullets=[
        "5ft 8in tall - reads as a person from the sidewalk, which is the whole trick",
        "Motion sensor triggers at up to 15ft, adjustable down to 3ft",
        "Head turns, arms raise, eyes glow red, and it screams",
        "Three volume levels including silent, for the neighbours you like",
    ],
    features=[
        ("It moves before they see it", "The sensor fires while they're still on the path, so the turn happens in their peripheral vision. That's what makes people jump - not the noise."),
        ("Weatherproof where it counts", "Sealed motor housing and a covered battery bay. It sits out through rain and a Philadelphia October without complaint."),
        ("Up in four minutes", "Two-piece pole into a weighted base, drape the robe, drop in 4 D-cells. No tools, no stakes, no assembly instructions you'll need to squint at."),
    ],
    specs=[("Height", "5ft 8in (173cm)"), ("Power", "4 x D battery or 5V adapter (both included)"),
           ("Trigger", "PIR motion, 3-15ft adjustable"), ("Sound", "3 levels + silent, 88dB max"),
           ("Material", "Polyester robe, ABS frame, latex skull"), ("Weather", "IPX4 - rain safe, not submersible")],
    box=["Animatronic reaper", "Weighted base + 2-piece pole", "5V power adapter", "Scythe prop", "Quick-start card"],
    reviews=[("Marisa T.", "Philadelphia, PA", 5, "Ordered Tuesday, had it Friday. My street has a group chat and it is entirely about my front yard now."),
             ("Ken A.", "Toledo, OH", 5, "Set the sensor to 15ft and it catches people at the mailbox. Worth it for the video I got of my brother-in-law alone."),
             ("Dana W.", "Sacramento, CA", 4, "Genuinely scary and easy to set up. Knocked one star because the scythe is lighter than it looks in photos.")],
),

"fog-machine": dict(
    hook="One minute to a driveway nobody can see the end of.",
    bullets=[
        "1000W - fills a two-car driveway in under 60 seconds",
        "12 colour LEDs wash the fog from underneath",
        "Wireless remote plus a wired timer controller, both included",
        "1 litre tank runs roughly 45 minutes of intermittent bursts",
    ],
    features=[
        ("Low-lying fog, not a cloud", "The output is cooled on the way out so it hugs the ground instead of drifting up and vanishing. That's the look people are actually buying."),
        ("Two ways to control it", "Wireless remote for manual bursts on the night, or the wired timer to set interval, duration and intensity and then forget about it."),
        ("Water-based and non-staining", "Standard fog fluid, safe around kids and pets, leaves no residue on a porch or a car. Do not use oil-based fluid in it."),
    ],
    specs=[("Power", "1000W, 110V"), ("Tank", "1 litre"), ("Warm-up", "3-4 minutes from cold"),
           ("Output", "Approx 8,000 cu ft/min"), ("LEDs", "12 x RGB, remote selectable"),
           ("Controls", "Wireless remote + wired timer")],
    box=["Fog machine", "Wireless remote", "Wired timer remote", "Hanging bracket", "250ml starter fluid"],
    reviews=[("Devon R.", "Austin, TX", 5, "Genuinely too powerful for my porch and I could not be happier about that."),
             ("Lucia M.", "Queens, NY", 5, "The LEDs are the part I didn't expect to care about. Green fog through a fence is unreal."),
             ("Tom B.", "Denver, CO", 4, "Great machine. Buy a gallon of fluid with it, the starter bottle goes fast.")],
),

"pet-costume": dict(
    hook="The reason your dog ends up on somebody's story.",
    bullets=[
        "Glow-in-the-dark ribcage - charges under any light, glows for hours",
        "Machine washable, XS to XXL, cats included",
        "Steps in and velcros - no over-the-head struggle",
        "Leaves legs and tail completely free",
    ],
    features=[
        ("It actually glows", "Phosphorescent print, not a light-grey print that photographs as glowing. Ten minutes under a lamp gets you a full evening."),
        ("Sized off real measurements", "The chart is chest girth and back length, not S/M/L guesswork. Measure your dog once and the fit is right first time."),
        ("Survives the wash", "Cold cycle, hang dry, and the print stays put. It's meant to come back out next October, not go in the bin on November 1st."),
    ],
    specs=[("Sizes", "XS, S, M, L, XL, XXL"), ("Fit", "Chest 11in - 34in"), ("Material", "Polyester / spandex blend"),
           ("Glow", "Phosphorescent, approx 4hr after 10min charge"), ("Closure", "Velcro belly panel"),
           ("Care", "Machine wash cold, hang dry")],
    box=["Skeleton pet costume", "Size + measuring guide"],
    reviews=[("Priya K.", "Chicago, IL", 5, "Arrived in two days, fits my beagle perfectly, and the glow is real glow not a printed-on gimmick."),
             ("Erin S.", "Portland, OR", 5, "Bought XS for a cat fully expecting a disaster. She wore it for an hour. I have never been more surprised."),
             ("Marcus D.", "Atlanta, GA", 5, "Third Halloween on the same costume, washed every year, still glows.")],
),

"inflatable-spider": dict(
    hook="Eight feet of yard that your neighbours have to look at.",
    bullets=[
        "8ft across, self-inflates in about 40 seconds",
        "Lights from inside - visible from down the block",
        "Stakes and tethers included, holds in real wind",
        "Deflates and folds into a bag the size of a pillow",
    ],
    features=[
        ("Big enough to read from the road", "Most yard inflatables are 4-5ft and disappear from the sidewalk. Eight feet is the size where drivers slow down."),
        ("Tied down properly", "Four ground stakes and three guy-line tethers, not the two flimsy pegs these usually ship with. It stays where you put it."),
        ("Packs away small", "Fan pulls out, air pushes out, folds into the included bag. Stores on a shelf, not in half your garage."),
    ],
    specs=[("Size", "8ft wide x 5ft tall inflated"), ("Power", "Mains adapter, 30ft outdoor cord"),
           ("Lighting", "4 internal LEDs, always-on"), ("Inflate", "Approx 40 seconds"),
           ("Material", "Polyester, weather-treated"), ("Anchors", "4 stakes + 3 tethers")],
    box=["Inflatable spider", "Internal fan + adapter", "4 ground stakes", "3 tethers", "Storage bag", "Patch kit"],
    reviews=[("Ray H.", "Cherry Hill, NJ", 5, "Went up in five minutes and survived a genuinely windy week. The tethers are the difference."),
             ("Nadia P.", "Tampa, FL", 5, "Kids on the block have named it. That's the review."),
             ("Stephen L.", "Boise, ID", 4, "Bright, big, easy. The cord is long but you'll still probably want an extension.")],
),
}


CATEGORIES = [
    ("Animatronics", "The ones that move, scream and ruin trick-or-treaters", "animatronic-reaper"),
    ("Yard & Decor", "Inflatables, tombstones, fog and lighting", "inflatable-spider"),
    ("Costumes", "Adults, kids and everything in between", "reaper-costume"),
    ("Pet Costumes", "The category that sells itself on video", "pet-costume"),
]

REVIEWS = [
    ("Marisa T.", "Philadelphia, PA", 5,
     "Ordered the reaper on a Tuesday, had it Friday. My street has a group chat and it is entirely about my front yard now."),
    ("Devon R.", "Austin, TX", 5,
     "The fog machine is genuinely too powerful for my porch and I could not be happier about that."),
    ("Priya K.", "Chicago, IL", 5,
     "Dog costume arrived in two days, fits my beagle perfectly, and the glow is real glow not a printed-on gimmick."),
]

TRUST = [
    ("Free US Shipping", "On every order, no minimum"),
    ("Ships in 24 Hours", "Order by 3pm, out the same day"),
    ("Delivered Before Oct 31", "Guaranteed or it's free"),
    ("30-Day Returns", "Unopened, no questions asked"),
]

FAQ = [
    ("Will it arrive before Halloween?",
     "Yes. Every order placed before October 20th is guaranteed to land on your doorstep by October 30th, or we refund you in full and you keep the item."),
    ("How much is shipping?",
     "Nothing. Shipping is free on every order in the continental US, with no minimum spend. Alaska, Hawaii and Canada are a flat $7.95."),
    ("Can I return something?",
     "Anything unopened can come back within 30 days for a full refund. If a item arrives damaged, send us a photo and we ship a replacement the same day - no return needed."),
    ("Are the animatronics loud?",
     "The reaper and the hanging ghost both have a three-level volume switch, including silent. Motion sensitivity is adjustable from 3ft to about 15ft."),
    ("Do you ship outside the US?",
     "We ship to Canada, the UK, Ireland and Australia. Delivery runs 6-10 days, so international orders should go in before October 15th."),
]


# --------------------------------------------------------------------------
# Rendering helpers
# --------------------------------------------------------------------------

def stars(rating):
    """Render a 5-star row, half-star aware."""
    out = []
    for i in range(1, 6):
        if rating >= i:
            out.append('<span class="star star--on">&#9733;</span>')
        elif rating >= i - .5:
            out.append('<span class="star star--half">&#9733;</span>')
        else:
            out.append('<span class="star">&#9733;</span>')
    return "".join(out)


def money(v):
    return f"${v:,.2f}"


def product_card(p, base="", href=None):
    """A grid card. `href` is the product's landing page; `base` prefixes assets.

    The image and the title are links, the Add button is not - a button nested
    inside an anchor is both invalid and ambiguous to click.
    """
    off = round((1 - p["price"] / p["was"]) * 100)
    badge = f'<span class="badge">{html.escape(p["badge"])}</span>' if p["badge"] else ""
    href = href if href is not None else f"p/{p['slug']}/"
    name = html.escape(p["name"])
    return f"""      <article class="card" data-slug="{p['slug']}">
        <a class="card__media" href="{href}">
          {badge}
          <span class="card__off">-{off}%</span>
          <img src="{base}assets/products/{p['slug']}.svg" alt="{name}" loading="lazy" width="600" height="600" />
        </a>
        <div class="card__body">
          <div class="card__rating">{stars(p['rating'])}<span class="card__rcount">{p['rating']} ({p['reviews']:,})</span></div>
          <h3 class="card__name"><a href="{href}">{name}</a></h3>
          <p class="card__blurb">{html.escape(p['blurb'])}</p>
          <div class="card__foot">
            <div class="card__price"><span class="price">{money(p['price'])}</span><span class="was">{money(p['was'])}</span></div>
            <button class="btn btn--add" type="button"
                    data-add="{p['slug']}" data-name="{html.escape(p['name'], quote=True)}" data-price="{p['price']}">
              Add to Cart
            </button>
          </div>
        </div>
      </article>
"""


def category_card(title, sub, slug):
    return f"""      <a class="cat" href="#shop">
        <img src="assets/products/{slug}.svg" alt="" aria-hidden="true" loading="lazy" width="600" height="600" />
        <div class="cat__txt"><h3>{html.escape(title)}</h3><p>{html.escape(sub)}</p></div>
      </a>
"""


def review_card(name, place, rate, text):
    return f"""      <figure class="rev">
        <div class="rev__stars">{stars(rate)}</div>
        <blockquote>{html.escape(text)}</blockquote>
        <figcaption><strong>{html.escape(name)}</strong><span>{html.escape(place)}</span><span class="rev__v">Verified buyer</span></figcaption>
      </figure>
"""


def faq_item(q, a):
    return f"""      <details class="faq__item">
        <summary>{html.escape(q)}<span class="faq__sign" aria-hidden="true"></span></summary>
        <div class="faq__a"><p>{html.escape(a)}</p></div>
      </details>
"""


LOGO = """<svg class="logo__mark" viewBox="0 0 64 64" aria-hidden="true">
  <path d="M30 12h5l-1 9h-4z" fill="#4c7a2a"/>
  <path d="M35 14c6-5 13-5 15 0-6 0-11 2-13 5z" fill="#4c7a2a"/>
  <ellipse cx="32" cy="39" rx="27" ry="23" fill="#ff7518"/>
  <path d="M15 30h13l-6.5 12z" fill="#0c0810"/>
  <path d="M36 30h13l-6.5 12z" fill="#0c0810"/>
  <path d="M32 38l-4.5 8h9z" fill="#0c0810"/>
  <path d="M15 46q17 15 34 0-3 12-17 12t-17-12z" fill="#0c0810"/>
  <g fill="#ff7518"><path d="M24 50l3 5h-6z"/><path d="M32 51l3 6h-6z"/><path d="M40 50l3 5h-6z"/></g>
</svg>"""


# --------------------------------------------------------------------------
# Shared chrome. The header, footer and cart drawer are generated once and
# used by the homepage and all ten landing pages, so they cannot drift apart.
# `base` prefixes asset paths, `home` prefixes in-page anchors.
# --------------------------------------------------------------------------

NAV = [("shop", "Shop All"), ("cats", "Categories"), ("why", "Why Us"),
       ("reviews", "Reviews"), ("faq", "FAQ")]


def announce_html():
    return """<div class="ann">
  <p>FREE US SHIPPING ON EVERYTHING &nbsp;&middot;&nbsp; Order by Oct 20 and it lands before Halloween &nbsp;&middot;&nbsp; <strong id="ann-count">&nbsp;</strong></p>
</div>
"""


def header_html(base, home):
    links = "".join(f'      <a href="{home}#{a}">{html.escape(t)}</a>\n' for a, t in NAV)
    return f"""<header class="hdr" id="hdr">
  <div class="wrap hdr__in">
    <a class="logo" href="{home or '#top'}">{LOGO}<span class="logo__txt">Hollow<em>&amp;</em>Hex</span></a>
    <nav class="nav" id="nav">
{links}    </nav>
    <div class="hdr__act">
      <button class="cartbtn" id="cartbtn" type="button" aria-label="Open cart">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6h15l-1.6 9.2a2 2 0 0 1-2 1.8H9.3a2 2 0 0 1-2-1.7L5.4 3.7A1 1 0 0 0 4.4 3H2" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/><circle cx="10" cy="20" r="1.6" fill="currentColor"/><circle cx="18" cy="20" r="1.6" fill="currentColor"/></svg>
        <span class="cartbtn__n" id="cartn">0</span>
      </button>
      <button class="burger" id="burger" type="button" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
"""


def footer_html(base, home):
    return f"""<footer class="ftr">
  <div class="wrap ftr__in">
    <div class="ftr__brand">
      <a class="logo" href="{home or '#top'}">{LOGO}<span class="logo__txt">Hollow<em>&amp;</em>Hex</span></a>
      <p>Animatronics, fog and yard decor, shipped free across the US and guaranteed before October 31st.</p>
    </div>
    <div class="ftr__col"><h4>Shop</h4><a href="{home}#shop">Best Sellers</a><a href="{home}#cats">Animatronics</a><a href="{home}#cats">Yard &amp; Decor</a><a href="{home}#cats">Costumes</a><a href="{home}#cats">Pet Costumes</a></div>
    <div class="ftr__col"><h4>Help</h4><a href="{home}#faq">Shipping</a><a href="{home}#faq">Returns</a><a href="{home}#faq">Track My Order</a><a href="{home}#faq">Contact</a></div>
    <div class="ftr__col"><h4>Company</h4><a href="{home}#why">About</a><a href="{home}#reviews">Reviews</a><a href="{home}#faq">Privacy</a><a href="{home}#faq">Terms</a></div>
  </div>
  <div class="wrap ftr__base">
    <p>&copy; 2026 {BRAND}. Demo storefront built for review &mdash; not a live shop.</p>
    <p class="ftr__pay"><span>VISA</span><span>MC</span><span>AMEX</span><span>PayPal</span><span>Shop&nbsp;Pay</span></p>
  </div>
</footer>
"""


def cart_html():
    return """<div class="scrim" id="scrim" hidden></div>
<aside class="cart" id="cart" aria-label="Shopping cart" aria-hidden="true">
  <div class="cart__hd">
    <h2>Your Cart</h2>
    <button class="cart__x" id="cartx" type="button" aria-label="Close cart">&times;</button>
  </div>
  <div class="cart__body" id="cartbody"></div>
  <div class="cart__ft">
    <div class="cart__row"><span>Subtotal</span><b id="carttot">$0.00</b></div>
    <div class="cart__row cart__row--ship"><span>Shipping</span><b>FREE</b></div>
    <button class="btn btn--gold btn--wide" type="button" id="checkout">Checkout</button>
    <p class="cart__note">Demo storefront &mdash; checkout is not connected to a payment provider.</p>
  </div>
</aside>

<div class="toast" id="toast" role="status"></div>
"""


# --------------------------------------------------------------------------
# Product landing pages - one per product, its own URL, built to convert ad
# traffic that lands on it cold.
# --------------------------------------------------------------------------

def detail_for(p):
    """Landing page content for a product, with a full set of fallbacks.

    A product that has no DETAILS entry still produces a complete page. This is
    deliberate: when the real product list lands, name + price + photo has to be
    enough to ship, with the written detail an upgrade rather than a blocker.
    """
    d = dict(DETAILS.get(p["slug"], {}))
    d.setdefault("hook", p["blurb"])
    d.setdefault("bullets", [s.strip() for s in p["blurb"].split(".") if s.strip()][:4] or
                            ["Ships free anywhere in the US"])
    d.setdefault("features", [
        ("Ships free, ships fast", "Out of a US warehouse within 24 hours of your order, tracked the whole way. No six-week wait from overseas."),
        ("Guaranteed before Halloween", "Order by October 20th and it is on your doorstep by the 30th, or you do not pay for it."),
        ("30 days to change your mind", "Unopened returns for a full refund. Damaged in transit, send a photo and we reship the same day."),
    ])
    d.setdefault("specs", [("Ships from", "United States"), ("Shipping", "Free, 2-5 business days"),
                           ("Returns", "30 days, unopened"), ("Stock", "In stock now")])
    d.setdefault("box", [p["name"]])
    d.setdefault("reviews", REVIEWS)
    return d


def landing_page(p, others):
    d = detail_for(p)
    off = round((1 - p["price"] / p["was"]) * 100)
    save = p["was"] - p["price"]
    base = "../../"
    home = "../../index.html"
    img = f"{base}assets/products/{p['slug']}"
    esc = html.escape

    thumbs = "".join(
        f'''        <button class="pdp__thumb{' on' if i == 0 else ''}" type="button" data-view="{img}{suf}.svg" aria-label="View {i + 1}">
          <img src="{img}{suf}.svg" alt="" width="600" height="600" loading="lazy" />
        </button>
'''
        for i, (suf, _) in enumerate(VIEWS))

    bullets = "".join(f"        <li>{esc(b)}</li>\n" for b in d["bullets"])

    features = "".join(f"""      <article class="feat">
        <h3>{esc(t)}</h3>
        <p>{esc(x)}</p>
      </article>
""" for t, x in d["features"])

    specs = "".join(f"          <tr><th scope=\"row\">{esc(k)}</th><td>{esc(v)}</td></tr>\n"
                    for k, v in d["specs"])

    box = "".join(f"          <li>{esc(b)}</li>\n" for b in d["box"])

    revs = "".join(review_card(*r) for r in d["reviews"])

    rel = "".join(product_card(o, base=base, href=f"../{o['slug']}/") for o in others)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(p['name'])} &mdash; {BRAND}</title>
<meta name="description" content="{esc(d['hook'])} {money(p['price'])} with free US shipping, guaranteed on your doorstep before October 31st." />
<meta name="robots" content="noindex" />
<meta property="og:title" content="{esc(p['name'])} &mdash; {money(p['price'])}" />
<meta property="og:description" content="{esc(d['hook'])}" />
<meta property="og:type" content="product" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="{base}styles.css" />
</head>
<body class="pdp-page" data-base="{base}">

{announce_html()}
{header_html(base, home)}

<main id="top">

<!-- buy box -->
<section class="pdp">
  <div class="wrap pdp__in">

    <div class="pdp__gal">
      <div class="pdp__stage">
        <span class="pdp__off">-{off}%</span>
        <img id="pdpimg" src="{img}.svg" alt="{esc(p['name'])}" width="600" height="600" />
      </div>
      <div class="pdp__thumbs">
{thumbs}      </div>
    </div>

    <div class="pdp__buy">
      <p class="pdp__crumb"><a href="{home}#shop">Shop</a> <span>/</span> {esc(p['name'])}</p>
      <h1 class="pdp__h">{esc(p['name'])}</h1>
      <div class="pdp__rate">{stars(p['rating'])}<span class="pdp__rc">{p['rating']} &middot; {p['reviews']:,} reviews</span></div>
      <p class="pdp__hook">{esc(d['hook'])}</p>

      <div class="pdp__price">
        <span class="price">{money(p['price'])}</span>
        <span class="was">{money(p['was'])}</span>
        <span class="pdp__save">You save {money(save)}</span>
      </div>

      <ul class="pdp__bul">
{bullets}      </ul>

      <div class="pdp__stock">
        <div class="pdp__bar"><i style="width:22%"></i></div>
        <p>Selling fast &mdash; limited stock left at this price</p>
      </div>

      <div class="pdp__act">
        <div class="qty" id="qty">
          <button type="button" data-q="-1" aria-label="Decrease quantity">&minus;</button>
          <b id="qtyn">1</b>
          <button type="button" data-q="1" aria-label="Increase quantity">+</button>
        </div>
        <button class="btn btn--gold btn--wide btn--add" type="button"
                data-add="{p['slug']}" data-name="{esc(p['name'], quote=True)}" data-price="{p['price']}" data-qty="qty">
          Add to Cart &mdash; {money(p['price'])}
        </button>
      </div>

      <ul class="pdp__trust">
        <li>Free US shipping, no minimum</li>
        <li>Guaranteed delivered before Oct 31 or it's free</li>
        <li>Ships within 24 hours from a US warehouse</li>
        <li>30-day returns, no questions asked</li>
      </ul>
    </div>

  </div>
</section>

<!-- features -->
<section class="sec sec--alt">
  <div class="wrap">
    <p class="sec__k">Why this one</p>
    <h2 class="sec__h">What makes it worth it</h2>
    <div class="feats">
{features}    </div>
  </div>
</section>

<!-- specs + box -->
<section class="sec">
  <div class="wrap spec">
    <div class="spec__tbl">
      <h2 class="sec__h">Specifications</h2>
      <table>
        <tbody>
{specs}        </tbody>
      </table>
    </div>
    <div class="spec__box">
      <h2 class="sec__h">In the box</h2>
      <ul class="ticks">
{box}      </ul>
      <img class="spec__art" src="{img}-detail.svg" alt="" aria-hidden="true" width="600" height="600" />
    </div>
  </div>
</section>

<!-- reviews -->
<section class="sec sec--alt" id="reviews">
  <div class="wrap">
    <p class="sec__k">{p['rating']} average from {p['reviews']:,} orders</p>
    <h2 class="sec__h">What buyers say</h2>
    <div class="revs">
{revs}    </div>
  </div>
</section>

<!-- faq -->
<section class="sec" id="faq">
  <div class="wrap wrap--narrow">
    <p class="sec__k">Before you ask</p>
    <h2 class="sec__h">Questions</h2>
    <div class="faq">
{"".join(faq_item(*f) for f in FAQ)}    </div>
  </div>
</section>

<!-- related -->
<section class="sec sec--alt">
  <div class="wrap">
    <p class="sec__k">Goes with it</p>
    <h2 class="sec__h">People also bought</h2>
    <div class="grid">
{rel}    </div>
  </div>
</section>

</main>

{footer_html(base, home)}
{cart_html()}

<!-- sticky mobile buy bar -->
<div class="stick" id="stick" aria-hidden="true">
  <img src="{img}.svg" alt="" width="600" height="600" />
  <div class="stick__m">
    <p>{esc(p['name'])}</p>
    <span><b>{money(p['price'])}</b> <s>{money(p['was'])}</s></span>
  </div>
  <button class="btn btn--gold btn--add" type="button"
          data-add="{p['slug']}" data-name="{esc(p['name'], quote=True)}" data-price="{p['price']}">
    Add
  </button>
</div>

<script src="{base}script.js"></script>
</body>
</html>
"""


def build():
    os.makedirs(ART_DIR, exist_ok=True)
    n_art = 0
    for slug, (label, glow, body) in ARTWORK.items():
        for suffix, render in VIEWS:
            with open(os.path.join(ART_DIR, f"{slug}{suffix}.svg"), "w", encoding="utf-8") as f:
                f.write(render(label, glow, body))
            n_art += 1

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{BRAND} &mdash; {TAGLINE}</title>
<meta name="description" content="Animatronics, fog, yard decor and costumes shipped free across the US and guaranteed to land before October 31st." />
<meta name="robots" content="noindex" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="styles.css" />
</head>
<body>

{announce_html()}
{header_html("", "")}
<!-- hero -->
<section class="hero" id="top">
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="wrap hero__in">
    <p class="hero__k">Halloween 2026 Collection</p>
    <h1 class="hero__h">Haunt Your House.<br /><span>Ship It Free.</span></h1>
    <p class="hero__p">Animatronics, fog, yard giants and costumes &mdash; shipped free anywhere in the US and guaranteed on your doorstep before October 31st.</p>
    <div class="hero__cta">
      <a class="btn btn--gold" href="#shop">Shop the Collection</a>
      <a class="btn btn--ghost" href="#cats">Browse Categories</a>
    </div>
    <div class="cdown" id="cdown" aria-label="Countdown to Halloween">
      <div class="cdown__cell"><b id="cd-d">--</b><span>Days</span></div>
      <div class="cdown__cell"><b id="cd-h">--</b><span>Hours</span></div>
      <div class="cdown__cell"><b id="cd-m">--</b><span>Minutes</span></div>
      <div class="cdown__cell"><b id="cd-s">--</b><span>Seconds</span></div>
      <p class="cdown__lbl">until Halloween</p>
    </div>
  </div>
</section>

<!-- trust -->
<section class="trust">
  <div class="wrap trust__in">
{"".join(f'''    <div class="trust__i"><b>{html.escape(t)}</b><span>{html.escape(s)}</span></div>
''' for t, s in TRUST)}  </div>
</section>

<!-- categories -->
<section class="sec" id="cats">
  <div class="wrap">
    <p class="sec__k">Shop by</p>
    <h2 class="sec__h">Categories</h2>
    <div class="cats">
{"".join(category_card(*c) for c in CATEGORIES)}    </div>
  </div>
</section>

<!-- products -->
<section class="sec sec--alt" id="shop">
  <div class="wrap">
    <p class="sec__k">Selling fast</p>
    <h2 class="sec__h">This Season's Best Sellers</h2>
    <p class="sec__sub">Every item ships free and is in stock right now. Prices hold until October 31st.</p>
    <div class="grid">
{"".join(product_card(p) for p in PRODUCTS)}    </div>
  </div>
</section>

<!-- why -->
<section class="sec" id="why">
  <div class="wrap why">
    <div class="why__txt">
      <p class="sec__k">Why us</p>
      <h2 class="sec__h">Halloween has a deadline.<br />We're built around it.</h2>
      <p>Most stores treat October like any other month. We don't. Every order is picked and out the door within 24 hours, tracked end to end, and backed by a written guarantee: if it isn't on your doorstep by October 30th, you don't pay for it.</p>
      <ul class="ticks">
        <li>US warehouse stock &mdash; not a 6-week boat from overseas</li>
        <li>Live tracking from the moment your label is printed</li>
        <li>Damaged in transit? Photo it, we reship the same day</li>
        <li>Real humans on chat 7 days a week through October</li>
      </ul>
      <a class="btn btn--gold" href="#shop">Start Shopping</a>
    </div>
    <div class="why__art">
      <img src="assets/products/witch-cauldron.svg" alt="" aria-hidden="true" width="600" height="600" />
    </div>
  </div>
</section>

<!-- reviews -->
<section class="sec sec--alt" id="reviews">
  <div class="wrap">
    <p class="sec__k">4.8 average from 8,900+ orders</p>
    <h2 class="sec__h">What Buyers Say</h2>
    <div class="revs">
{"".join(review_card(*r) for r in REVIEWS)}    </div>
  </div>
</section>

<!-- email capture -->
<section class="cap">
  <div class="wrap cap__in">
    <h2>Get 10% off your first order</h2>
    <p>One email when the new drops land. Nothing else, and you can leave any time.</p>
    <form class="cap__f" id="capform" novalidate>
      <input type="email" id="capmail" placeholder="you@email.com" aria-label="Email address" required />
      <button class="btn btn--gold" type="submit">Send My Code</button>
    </form>
    <p class="cap__msg" id="capmsg" role="status"></p>
  </div>
</section>

<!-- faq -->
<section class="sec" id="faq">
  <div class="wrap wrap--narrow">
    <p class="sec__k">Before you ask</p>
    <h2 class="sec__h">Questions</h2>
    <div class="faq">
{"".join(faq_item(*f) for f in FAQ)}    </div>
  </div>
</section>

{footer_html("", "")}
{cart_html()}
<script src="script.js"></script>
</body>
</html>
"""

    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)

    # One landing page per product, each at its own URL: /p/<slug>/
    total = 0
    for i, p in enumerate(PRODUCTS):
        # rotate the "people also bought" row so it isn't the same three items
        # on every page - it should look like a shop, not a template
        rotated = PRODUCTS[i + 1:] + PRODUCTS[:i]
        others = rotated[:3]
        out_dir = os.path.join(HERE, "p", p["slug"])
        os.makedirs(out_dir, exist_ok=True)
        doc = landing_page(p, others)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(doc)
        total += len(doc)

    print(f"index.html written ({len(page):,} bytes)")
    print(f"{len(PRODUCTS)} landing pages written to p/<slug>/index.html ({total:,} bytes)")
    print(f"{n_art} product SVGs written to assets/products/ "
          f"({len(ARTWORK)} products x {len(VIEWS)} views)")


if __name__ == "__main__":
    build()
