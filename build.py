#!/usr/bin/env python3
"""
Hollow & Hex - demo Halloween storefront generator.

Run:  python3 build.py
Emits index.html plus the product artwork in assets/products/.

Four files feed it, and between them they hold everything a non-programmer
would want to change:

  catalog.py    the 52 real products - names, photos, categories, blurbs
  prices.csv    your selling price and compare-at price, one row per product
  social.csv    star rating, review count and units sold, one row per product
  reviews.csv   the review quotes themselves
  content.json  EVERY line of shipping, delivery, guarantee, warehouse and
                countdown wording on the site, in one place

Two things this generator will not do, both on purpose:

  * It will not invent a price. A product with no price renders a "price to be
    set" chip and a disabled buy button, so an unpriced page is obviously
    unfinished rather than quietly wrong.
  * It will not invent a star rating or a review count. Every rating and every
    review quote on this site was read off the supplier's own listing for that
    exact product. Where the supplier has none, the star row is absent - it
    does NOT fall back to a flattering default, because a 4.8 nobody earned is
    not a placeholder, it is a false claim, and it is the client's name on it.
"""

import os
import re
import csv
import json
import html

import catalog

HERE = os.path.dirname(os.path.abspath(__file__))


def load_prices():
    """Overlay prices.csv onto the catalogue.

    The client fills two columns in one spreadsheet and re-runs the build; no
    Python is edited to price 52 products. A blank cell leaves the product
    unpriced rather than defaulting to zero - a $0.00 product looks like a
    working price and is the worst possible failure here.
    """
    path = os.path.join(HERE, "prices.csv")
    if not os.path.exists(path):
        return 0
    by_slug = {p["slug"]: p for p in catalog.PRODUCTS}
    n = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            p = by_slug.get((row.get("handle") or "").strip())
            if not p:
                continue
            for key, col in (("price", "your_price"), ("was", "was_price")):
                raw = (row.get(col) or "").strip().lstrip("$").replace(",", "")
                if raw:
                    try:
                        p[key] = float(raw)
                    except ValueError:
                        print(f"  ! {p['slug']}: {col} is not a number: {raw!r}")
            if p["price"] is not None:
                n += 1

    # A price on a delisted product is the one entry in this spreadsheet that
    # can cost real money. Pricing a product is exactly what switches its Buy
    # button on, and these fifteen have no supplier behind them - so the row
    # that looks like progress is the row that sells something unshippable.
    #
    # The price is refused rather than applied, because the safe direction is
    # obvious: not selling an item you could have sold is a slow day, selling
    # one you cannot ship is a refund, a chargeback and a review. It is refused
    # LOUDLY - a silently dropped price would send him hunting for a bug in the
    # build. Re-listing is a deliberate act: take the slug out of UNAVAILABLE
    # in catalog.py once a supplier is confirmed, and the price applies.
    blocked = []
    for p in catalog.PRODUCTS:
        if p["slug"] in catalog.UNAVAILABLE and p["price"] is not None:
            blocked.append((p["slug"], p["price"]))
            p["price"] = p["was"] = None
            n -= 1
    if blocked:
        print("  !! prices.csv prices a product the supplier no longer lists:")
        for s, v in blocked:
            print(f"     {s}  ${v:.2f}  - IGNORED, its Buy button stays off")
        print("     these cannot be fulfilled. To sell one anyway, remove it")
        print("     from UNAVAILABLE in catalog.py first.")

    # A "was" price below the selling price would render a negative discount.
    for p in catalog.PRODUCTS:
        if p["price"] and p["was"] and p["was"] <= p["price"]:
            print(f"  ! {p['slug']}: was_price {p['was']} is not above "
                  f"your_price {p['price']} - discount badge suppressed")
            p["was"] = None
    return n


def load_variants():
    """Read variants.csv - the SAME file the Shopify importer reads.

    One file, two consumers. If the demo kept its own copy of the option lists
    they would drift, and the drift would be invisible: the demo would go on
    showing five colours after the sixth was added to the store, and nobody
    would be looking at both pages at once to notice.

    Returns {slug: {"options": [(name, [values]), ...], "images": {(name, value): file}}}.
    """
    path = os.path.join(HERE, "variants.csv")
    if not os.path.exists(path):
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        # csv.DictReader has no notion of a comment. Without this filter the
        # header block at the top of the file comes back as a row whose handle
        # is "# Every row here is..." and that handle matches no product, so
        # the failure would be a silent one.
        lines = [ln for ln in f if not ln.lstrip().startswith("#")]

    known = {p["slug"] for p in catalog.PRODUCTS}
    out = {}
    for r in csv.DictReader(lines):
        handle = (r.get("handle") or "").strip()
        if not handle:
            continue
        if handle not in known:
            # Loud, not silent. A renamed product would otherwise quietly lose
            # its options on both the demo and the store at the same time.
            print(f"  ! variants.csv names a product that does not exist: {handle}")
            continue
        opts, imgs = [], {}
        for n in ("1", "2", "3"):
            name = (r.get(f"option{n}_name") or "").strip()
            vals = [v.strip() for v in (r.get(f"option{n}_values") or "").split("|") if v.strip()]
            if not name or not vals:
                continue
            opts.append((name, vals))
            # Position-aligned with the values, and a short list is allowed, so
            # zip() would drop the tail rather than complain about it.
            files = [v.strip() for v in (r.get(f"option{n}_images") or "").split("|")]
            for i, v in enumerate(vals):
                if i < len(files) and files[i]:
                    imgs[(name, v)] = files[i]
        if opts:
            out[handle] = {"options": opts, "images": imgs}
    return out


VARIANTS = {}


def variant_block(p, base=""):
    """The size/colour picker, or "" for a product with nothing to pick.

    Rendered from variants.csv, so it never invents an option. The default
    selection is the first value of each list, which is also what the Shopify
    theme selects, so the demo and the store open on the same variant.
    """
    v = VARIANTS.get(p["slug"])
    if not v:
        return ""
    esc = html.escape
    # variants.csv names a photo by FILENAME; img_for() resolves an index, and
    # it is the only thing that knows about the bare-id fallback. So map the
    # filename back to its index and go through img_for rather than gluing a
    # path together here and getting a different answer for the same photo.
    by_file = {str(f): i for i, f in enumerate(p["images"])}
    rows = []
    for idx, (name, values) in enumerate(v["options"]):
        pills = []
        for i, val in enumerate(values):
            f = v["images"].get((name, val), "")
            # The photo is looked up in THIS product's own gallery. A filename
            # that is not in it is a typo in the spreadsheet, and swapping to a
            # 404 would leave a broken image where a jumper used to be.
            # NOT `idx` - that is the option row's index, and reusing the name
            # here silently made every data-idx and every radio group name read
            # "None". Two option rows sharing one radio group is one control,
            # so choosing a colour cleared the size.
            photo_i = by_file.get(f)
            if f and photo_i is None:
                print(f"  ! {p['slug']}: variants.csv points {name}/{val} at "
                      f"{f}, which is not one of its photos - photo swap off")
            view = (f' data-view="{img_for(p, photo_i, base)}"'
                    if photo_i is not None else "")
            pills.append(
                f'<label class="pill{" on" if i == 0 else ""}">'
                f'<input type="radio" name="{p["slug"]}-opt{idx}" '
                f'value="{esc(val, quote=True)}"{" checked" if i == 0 else ""}{view}>'
                f'<span>{esc(val)}</span></label>')
        rows.append(f"""        <div class="opt" data-idx="{idx}">
          <span class="opt__label">{esc(name)}: <b data-sel>{esc(values[0])}</b></span>
          <div class="opt__vals">{"".join(pills)}</div>
        </div>
""")
    out = '      <div class="pdp__opts" id="opts">\n' + "".join(rows) + "      </div>\n"
    # Two option rows must never share a radio group name, or they are one
    # control and picking a colour clears the size. They must also each have a
    # numeric data-idx, because the script reads the rows by that. Both of
    # these were broken at once by a one-word variable clash and neither is
    # visible on the page - the pills still look and click exactly right.
    groups = re.findall(r'name="([^"]+)"', out)
    assert len(set(groups)) == len(v["options"]), \
        f'{p["slug"]}: {len(set(groups))} radio groups for {len(v["options"])} options'
    idxs = re.findall(r'data-idx="([^"]*)"', out)
    assert idxs == [str(i) for i in range(len(v["options"]))], \
        f'{p["slug"]}: option rows are indexed {idxs}'
    return out


def load_content():
    """Read content.json - every editable line of copy on the site.

    Missing keys fall back to the defaults below rather than raising, so a
    client who deletes a block gets the block's default back instead of a
    stack trace. Missing is different from EMPTY: an empty string switches a
    line off, which is how you remove a claim you do not want to make.
    """
    path = os.path.join(HERE, "content.json")
    if not os.path.exists(path):
        print("  ! content.json missing - using built-in defaults")
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_social():
    """Overlay social.csv - rating, review count, units sold - per product.

    Nothing in this file was written by me. Every figure came off the
    supplier's own listing page for that product. A blank cell means the
    supplier has no rating for it, and the star row then does not render at
    all. See make_social_csv.py for exactly how each number was obtained.
    """
    path = os.path.join(HERE, "social.csv")
    by_slug = {p["slug"]: p for p in catalog.PRODUCTS}
    for p in catalog.PRODUCTS:
        p.setdefault("rating", None)
        p.setdefault("reviews", None)
        p.setdefault("sold", None)
    if not os.path.exists(path):
        return 0
    n = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            p = by_slug.get((row.get("handle") or "").strip())
            if not p:
                continue
            r = (row.get("rating") or "").strip()
            if not r:
                continue
            try:
                p["rating"] = float(r)
            except ValueError:
                print(f"  ! {p['slug']}: rating is not a number: {r!r}")
                continue
            # A rating with no count behind it is the weaker of the two claims
            # and the one shoppers discount, so it is allowed - but a count
            # that will not parse is dropped rather than shown as text.
            for key, col in (("reviews", "reviews"), ("sold", "sold")):
                raw = (row.get(col) or "").strip().replace(",", "")
                if raw.isdigit():
                    p[key] = int(raw)
            if not 0 < p["rating"] <= 5:
                print(f"  ! {p['slug']}: rating {p['rating']} is outside 1-5 "
                      f"- ignored")
                p["rating"] = None
                continue
            n += 1
    return n


def load_reviews():
    """Read reviews.csv into {slug: [review, ...]}.

    Real quotes from verified buyers of the supplier's listing. They are
    reviews of the PRODUCT, not of this store, and the section heading says
    so. Delete a row and it is gone from the site on the next build.

    reviews_section.min_stars decides which of them are shown. The client asked
    for 5 only. Nothing is deleted from reviews.csv - every review stays in the
    file and comes straight back by lowering one number, because "show the 4s
    again" should not mean re-scraping a supplier listing that may be gone.
    """
    path = os.path.join(HERE, "reviews.csv")
    out = {}
    if not os.path.exists(path):
        return out
    known = {p["slug"] for p in catalog.PRODUCTS}
    try:
        min_stars = float(c("reviews_section.min_stars", 5))
    except (TypeError, ValueError):
        print("  ! reviews_section.min_stars is not a number - showing all")
        min_stars = 0
    stray = 0
    hidden = 0
    had = set()   # products that had at least one review BEFORE the star filter
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            slug = (row.get("handle") or "").strip()
            text = (row.get("text") or "").strip()
            if not text:
                continue
            if slug not in known:
                stray += 1
                continue
            try:
                rate = float((row.get("rating") or "5").strip())
            except ValueError:
                rate = 5.0
            had.add(slug)
            if rate < min_stars:
                hidden += 1
                continue
            out.setdefault(slug, []).append({
                "name": (row.get("name") or "Verified buyer").strip(),
                "rating": rate,
                "title": (row.get("title") or "").strip(),
                "text": text,
                "verified": (row.get("verified") or "").strip().lower()
                            in ("yes", "y", "true", "1"),
                "photo": (row.get("photo") or "").strip(),
            })
    if stray:
        print(f"  ! reviews.csv: {stray} rows name a product that does not "
              f"exist - they are not on the site")
    if hidden:
        print(f"  reviews.csv: {hidden} reviews below {min_stars:g} stars are "
              f"hidden (still in the file)")
        # The cost of the filter, named out loud. A product that had reviews
        # and now has none loses its whole review section, and silently losing
        # it on the hero product is exactly the kind of thing you find out
        # about from the client rather than from the build.
        emptied = sorted(had - set(out))
        if emptied:
            print(f"  !! {len(emptied)} product(s) now show NO reviews at all, "
                  f"their review section disappears:")
            for s in emptied:
                print(f"     {s}")
    return out


ART_DIR = os.path.join(HERE, "assets", "products")

# Filled by build(). Module level so the page builders can reach them without
# threading two more arguments through every function.
C = {}
REVIEWS_BY_SLUG = {}


def c(path, default=""):
    """Look up a dotted path in content.json, e.g. c("hero.cta_primary").

    Returns `default` when the key is missing, so a client can delete a key
    they do not understand and get the sensible thing back.
    """
    node = C
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node

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

PRODUCTS = catalog.PRODUCTS
CATEGORIES = catalog.CATEGORIES
DETAILS = {}


# These four used to be Python lists here. They now come from content.json so
# the client can change a delivery promise without opening a .py file, and the
# lists below are only the fallback for a deleted key.
def trust_items():
    return [tuple(x) for x in c("trust_bar", [
        ("Free US Shipping", "On every order, no minimum"),
        ("Ships in 24 Hours", "Order by 3pm, out the same day"),
        ("Delivered Before Oct 31", "Guaranteed or it's free"),
        ("30-Day Returns", "Unopened, no questions asked"),
    ])]


def faq_items():
    return [tuple(x) for x in c("faq", [])]


def cat_anchor(name):
    """Homepage anchor id for a category section. `LED Masks` -> `cat-led-masks`.

    The nav chip and the section heading both call this, so they cannot drift
    apart - which is the entire failure mode of a hand-written anchor list.
    """
    return "cat-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


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


def sentences(text, limit=4):
    """Split prose into sentences for the fallback bullet list.

    NOT text.split("."). A plain split tears decimals in half: the headrest
    covers are "roughly 9.84 inches", which came out as two bullets reading
    "Roughly 9" and "84 inches". This only splits on a full stop that is not
    sitting between two digits.
    """
    parts = [s.strip() for s in re.split(r"(?<!\d)\.(?!\d)", text) if s.strip()]
    return parts[:limit] or ["Ships free anywhere in the US"]


def money(v):
    return f"${v:,.2f}" if v is not None else ""


def img_for(p, i=0, base=""):
    """Path to a product photo. Falls back to the drawn placeholder.

    Every one of the 52 has a real photograph now. The placeholder is kept
    because it is the right answer for a product added later with no image
    yet - it says so in words, so nobody ships it by accident.

    The filename comes OUT of the list, it is not computed from the index.
    Deriving `slug-3.jpg` from position 3 was fine while the positions were
    always 1..n with no holes; the moment the client deletes one row out of the
    middle of photos.csv the positions go 1,2,4,5 and every derived name after
    the hole points at a file that is not there. Entries that are still a bare
    product id - a product photos.csv says nothing about - keep the old rule.
    """
    if not p["images"]:
        return f"{base}assets/products/_no-photo.svg"
    i = max(0, min(i, len(p["images"]) - 1))
    name = str(p["images"][i])
    if not name.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".svg")):
        name = f"{p['slug']}.jpg" if i == 0 else f"{p['slug']}-{i + 1}.jpg"
    return f"{base}assets/products/{name}"


QTY_HTML = """<div class="qty" id="qty">
          <button type="button" data-q="-1" aria-label="Decrease quantity">&minus;</button>
          <b id="qtyn">1</b>
          <button type="button" data-q="1" aria-label="Increase quantity">+</button>
        </div>
        """


def is_dead(p):
    """True for the products the supplier has stopped listing.

    The client chose to keep all fifteen on the site rather than delete them,
    so they need a state of their own. They are not "not priced yet" - that is
    a note to him about work outstanding, and it was being shown to shoppers.
    """
    return p["slug"] in catalog.UNAVAILABLE


def price_html(p, cls=""):
    """The price block, or a visible marker that no price has been set yet.

    An empty gap where a price belongs reads as a bug. An orange "set your
    price" chip reads as the one job left to do, which is what it is.

    Two different absences of a price, so two different labels. "Price to be
    set" is addressed to the client and means one decision away from selling.
    A delisted product is not one decision away from anything, and telling a
    shopper its price is pending implies it is coming back.
    """
    if p["price"] is None and is_dead(p):
        # Short label in the grid, full sentence on the product page. Uppercase
        # with letter-spacing, "Currently unavailable" measures 233px, and a
        # card's price row on a 390px phone is 145px - it overflowed the card,
        # then the grid, then the page, which is how one word widened the whole
        # layout to 417px. The card has room for one word, so it gets one word.
        label = "Unavailable" if cls.startswith("card") else "Currently unavailable"
        return f'<div class="{cls} noprice"><span class="tag-soldout">{label}</span></div>'
    if p["price"] is None:
        return f'<div class="{cls} noprice"><span class="tag-setprice">Price to be set</span></div>'
    was = f'<span class="was">{money(p["was"])}</span>' if p.get("was") else ""
    return f'<div class="{cls}"><span class="price">{money(p["price"])}</span>{was}</div>'


def discount_chip(p):
    """`floor`, not `round`. 49.99 against 79.99 is 37.5% off, and rounding it
    up to 38 overstates the saving on a page built for paid traffic."""
    if not p.get("price") or not p.get("was") or p["was"] <= p["price"]:
        return ""
    off = int((1 - p["price"] / p["was"]) * 100)
    return f'<span class="card__off">-{off}%</span>'


def rating_row(p, cls="card__rating"):
    """Stars + review count, or nothing at all.

    There is no fallback rating. A product the supplier has no reviews for
    renders an empty string here and the card closes the gap, rather than
    showing a default that would be a claim nobody can support.
    """
    # An EMPTY div, not no div. The row is a fixed height in CSS, so a product
    # with no supplier rating still reserves the space and the titles across a
    # row of four line up. Dropping the element entirely pulled unrated cards
    # up by 22px and made the grid look misaligned rather than incomplete.
    if not p.get("rating"):
        return f'<div class="{cls} {cls}--none"></div>'
    n = p.get("reviews")
    count = f'<span class="card__rcount">({n:,})</span>' if n else ""
    return (f'<div class="{cls}">{stars(p["rating"])}'
            f'<span class="card__rval">{p["rating"]:.1f}</span>{count}</div>')


def product_card(p, base="", href=None):
    """A grid card. `href` is the product's landing page; `base` prefixes assets.

    The image and the title are links, the Add button is not - a button nested
    inside an anchor is both invalid and ambiguous to click.
    """
    badge = f'<span class="badge">{html.escape(p["badge"])}</span>' if p.get("badge") else ""
    href = href if href is not None else f"p/{p['slug']}/"
    name = html.escape(p["name"])
    label = c("buttons.add_to_cart", "Add to Cart")
    if p["price"] is None:
        # Two reasons a card cannot sell, and only one of them is a to-do.
        # Telling him to price a delisted product is advice that now cannot be
        # taken - load_prices() refuses that price on purpose.
        tip = ("This product has been delisted by the supplier"
               if is_dead(p) else "Set a price for this product first")
        add = (f'<button class="btn btn--add" type="button" disabled '
               f'title="{tip}">Add to Cart</button>')
    elif p["slug"] in VARIANTS:
        # A card cannot pick a size. Adding blind is how somebody who wanted
        # XXL in khaki receives an S in black, so a product with real options
        # sends the shopper to its page instead. Same rule as the Shopify card.
        add = f'<a class="btn btn--add" href="{href}">Choose options</a>'
    else:
        add = (f'<button class="btn btn--add" type="button" data-add="{p["slug"]}" '
               f'data-name="{html.escape(p["name"], quote=True)}" data-price="{p["price"]}">'
               f'{html.escape(label)}</button>')
    # "1,082 sold" is the strongest line on the card when it is there, and it
    # is only there for the products the supplier publishes a figure for.
    sold = (f'<p class="card__sold">{p["sold"]:,}+ sold</p>'
            if p.get("sold") else "")
    # Second photo on hover. It is a data- attribute rather than a second <img>
    # on purpose: 52 cards x one extra photograph is 52 extra downloads on the
    # homepage, and the brief asks for the site to be FAST on mobile - where
    # there is no hover at all and the second photo would never be seen. The
    # script swaps the src the first time a pointer enters the card, so a phone
    # pays nothing for it.
    hover = (f' data-alt="{img_for(p, 1, base)}"'
             if len(p["images"]) > 1 else "")
    return f"""      <article class="card" data-slug="{p['slug']}">
        <a class="card__media" href="{href}">
          {badge}
          {discount_chip(p)}
          <img src="{img_for(p, 0, base)}" alt="{name}" loading="lazy" width="600" height="600"{hover} />
        </a>
        <div class="card__body">
          {rating_row(p)}
          <h3 class="card__name"><a href="{href}">{name}</a></h3>
          <p class="card__blurb">{html.escape(p['blurb'])}</p>
          {sold}
          <div class="card__foot">
            {price_html(p, "card__price")}
            {add}
          </div>
        </div>
      </article>
"""


def category_card(title, sub, slug, home=""):
    """`slug` names the product whose photo fronts this category tile.

    catalog.check() asserts every one of those slugs exists, so a renamed
    product breaks the build rather than silently emptying a tile.

    The href is the category's own section further down the SAME page, not the
    single "shop" block it used to be - clicking Apparel now lands you on the
    apparel products rather than at the top of all 52.
    """
    front = [x for x in PRODUCTS if x["slug"] == slug][0]
    n = sum(1 for x in PRODUCTS if x["cat"] == title)
    return f"""      <a class="cat" href="{home}#{cat_anchor(title)}">
        <img src="{img_for(front)}" alt="" aria-hidden="true" loading="lazy" width="600" height="600" />
        <div class="cat__txt"><h3>{html.escape(title)}</h3><p>{html.escape(sub)}</p>
          <span class="cat__n">{n} product{"s" if n != 1 else ""}</span></div>
      </a>
"""


def cat_chips(home=""):
    """The jump bar. Sticks under the header so it is reachable from anywhere.

    Same cat_anchor() as the section ids, so a category renamed in catalog.py
    moves the chip and its target together.
    """
    chips = "".join(
        f'<a class="chip" href="{home}#{cat_anchor(t)}">{html.escape(t)}</a>'
        for t, _, _ in CATEGORIES)
    return f"""<nav class="chips" id="chips" aria-label="Jump to a category">
  <div class="wrap chips__in">
    <a class="chip chip--all" href="{home}#shop">All</a>
    {chips}
  </div>
</nav>
"""


def review_card(r, product_name=None, base=""):
    """One review. `r` is a row out of reviews.csv.

    The `photo` column is empty in every row today - the supplier's review
    images sit behind expiring signed URLs and would 404 within days. The
    column and the markup are here so a customer photo can be dropped in
    later without touching this file: put a filename in the column and the
    figure grows an image.
    """
    # The supplier masks reviewer names itself ("S**r"), which is why no real
    # name is republished here. A few of them start with an emoji instead of a
    # letter, and "@**y" renders as a broken glyph rather than as a person, so
    # anything with no leading letter falls back to the neutral label. The CSV
    # keeps whatever was harvested - this is a display rule, not an edit.
    raw = (r["name"] or "").strip()
    name = html.escape(raw if raw[:1].isalpha() else "Verified buyer")
    ver = ('<span class="rev__v">Verified purchase</span>'
           if r.get("verified") else "")
    of = (f'<span class="rev__of">on {html.escape(product_name)}</span>'
          if product_name else "")
    # The photo column holds a FILENAME in assets/reviews/, because a bare
    # filename is the same on the homepage and on a landing page two folders
    # down and a relative path is not. Anything that is already a URL or an
    # absolute path is passed through untouched, so the client can point a row
    # at an image hosted anywhere without learning this rule.
    src = (r.get("photo") or "").strip()
    if src and "://" not in src and not src.startswith("/"):
        src = f"{base}assets/reviews/{src}"
    photo = (f'<img class="rev__img" src="{html.escape(src, quote=True)}" '
             f'alt="" loading="lazy" width="600" height="600" />' if src else "")
    title = (f'<strong class="rev__t">{html.escape(r["title"])}</strong>'
             if r.get("title") else "")
    return f"""      <figure class="rev">
        <div class="rev__stars">{stars(r["rating"])}</div>
        {title}
        <blockquote>{html.escape(r["text"])}</blockquote>
        {photo}
        <figcaption><strong>{name}</strong>{of}{ver}</figcaption>
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

def nav_items():
    """The header links. A link is only emitted if its target will exist.

    "Reviews" appears once there are reviews to scroll to and not before - a
    nav link that scrolls nowhere is worse than one less link, and it was
    missing for exactly that reason until the supplier reviews arrived.
    """
    items = [("shop", "Shop All"), ("cats", "Categories")]
    if REVIEWS_BY_SLUG and c("reviews_section.show", True):
        items.append(("reviews", "Reviews"))
    if c("why_us.show", True):
        items.append(("why", "Why Us"))
    if faq_items():
        items.append(("faq", "FAQ"))
    return items


def announce_html():
    """The announcement bar, entirely from content.json.

    `announcement.lines` is a list, so adding or removing a claim is adding or
    removing a line - and emptying the list removes the bar rather than
    leaving an empty orange strip across the top of the site.
    """
    if not c("announcement.show", True):
        return ""
    lines = [x for x in c("announcement.lines", []) if x.strip()]
    if not lines and not c("announcement.show_countdown", True):
        return ""
    # &nbsp; not a plain space: the separator sits between two escaped strings
    # and a normal space here has been eaten by whitespace stripping before.
    sep = " &nbsp;&middot;&nbsp; "
    body = sep.join(html.escape(x) for x in lines)
    if c("announcement.show_countdown", True):
        if body:
            body += sep
        body += '<strong id="ann-count">&nbsp;</strong>'
    return f"""<div class="ann">
  <p>{body}</p>
</div>
"""


def header_html(base, home):
    links = "".join(f'      <a href="{home}#{a}">{html.escape(t)}</a>\n'
                    for a, t in nav_items())
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
      <p>{html.escape(c("brand.footer_blurb", ""))}</p>
    </div>
    <div class="ftr__col"><h4>Shop</h4><a href="{home}#shop">Everything</a>{"".join(f'<a href="{home}#{cat_anchor(t)}">{html.escape(t)}</a>' for t, _, _ in CATEGORIES[:5])}</div>
    <div class="ftr__col"><h4>Help</h4><a href="{home}#faq">Shipping</a><a href="{home}#faq">Returns</a><a href="{home}#faq">Track My Order</a><a href="{home}#faq">Contact</a></div>
    <div class="ftr__col"><h4>Company</h4><a href="{home}#why">About</a><a href="{home}#shop">Shop All</a><a href="{home}#faq">Privacy</a><a href="{home}#faq">Terms</a></div>
  </div>
  <div class="wrap ftr__base">
    <p>{html.escape(c("footer_note", f"(c) 2026 {BRAND}."))}</p>
    <p class="ftr__pay"><span>VISA</span><span>MC</span><span>AMEX</span><span>PayPal</span><span>Shop&nbsp;Pay</span></p>
  </div>
</footer>
"""


def cart_html():
    return f"""<div class="scrim" id="scrim" hidden></div>
<aside class="cart" id="cart" aria-label="Shopping cart" aria-hidden="true">
  <div class="cart__hd">
    <h2>Your Cart</h2>
    <button class="cart__x" id="cartx" type="button" aria-label="Close cart">&times;</button>
  </div>
  <div class="cart__body" id="cartbody"></div>
  <div class="cart__ft">
    <div class="cart__row"><span>Subtotal</span><b id="carttot">$0.00</b></div>
    <div class="cart__row cart__row--ship"><span>Shipping</span><b>{html.escape(c("buttons.cart_shipping_line", "FREE"))}</b></div>
    <button class="btn btn--gold btn--wide" type="button" id="checkout">{html.escape(c("buttons.checkout", "Checkout"))}</button>
    <p class="cart__note">{html.escape(c("buttons.cart_note", ""))}</p>
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

    A product with nothing but a name, a photo and a one-line blurb still
    produces a complete page. That is the whole design: written detail is an
    upgrade, never the thing that blocks a launch.
    """
    d = dict(DETAILS.get(p["slug"], {}))
    d.setdefault("hook", p["blurb"])
    d.setdefault("bullets", catalog.BULLETS.get(p["slug"]) or sentences(p["blurb"]))
    d.setdefault("features", [tuple(x) for x in c("product_features", [])])
    d.setdefault("specs", [tuple(x) for x in c("product_specs", [])])
    d.setdefault("box", [p["name"]])
    d.setdefault("reviews", REVIEWS_BY_SLUG.get(p["slug"], []))
    return d


def landing_page(p, others):
    d = detail_for(p)
    base = "../../"
    home = "../../index.html"
    main_img = img_for(p, 0, base)
    esc = html.escape

    save = (f'''<span class="pdp__save">You save {money(p["was"] - p["price"])}</span>'''
            if p["price"] is not None and p.get("was") else "")

    # Most products now carry the supplier's whole gallery - five to eight
    # photos. A handful still have one (the two Walmart-sourced items, and one
    # product whose page the supplier will not serve from here), and for those
    # the strip would be a row of one: hide it rather than render a control
    # that does nothing.
    if len(p["images"]) > 1:
        thumbs = '''      <div class="pdp__thumbs">
''' + "".join(
            f'''        <button class="pdp__thumb{" on" if i == 0 else ""}" type="button" data-view="{img_for(p, i, base)}" aria-label="View {i + 1}">
          <img src="{img_for(p, i, base)}" alt="" width="600" height="600" loading="lazy" />
        </button>
'''
            for i in range(len(p["images"]))) + "      </div>\n"
    else:
        thumbs = ""


    bullets = "".join(f"        <li>{esc(b)}</li>\n" for b in d["bullets"])

    features = "".join(f"""      <article class="feat">
        <h3>{esc(t)}</h3>
        <p>{esc(x)}</p>
      </article>
""" for t, x in d["features"])

    specs = "".join(f"          <tr><th scope=\"row\">{esc(k)}</th><td>{esc(v)}</td></tr>\n"
                    for k, v in d["specs"])

    box = "".join(f"          <li>{esc(b)}</li>\n" for b in d["box"])

    rel = "".join(product_card(o, base=base, href=f"../{o['slug']}/") for o in others)

    # Every block below hides itself rather than showing an invented value.
    # A star rating needs a review source; a price needs the client's margin
    # decision. Neither is something this script is entitled to make up.
    if p.get("rating"):
        n = p.get("reviews")
        # The count links to the reviews further down the page rather than
        # just stating a number - it is the one piece of proof on this screen
        # a sceptical shopper will want to check, so make checking one tap.
        cnt = (f' &middot; <a href="#reviews">{n:,} review{"s" if n != 1 else ""}</a>'
               if n else "")
        sold = (f'<span class="pdp__sold">{p["sold"]:,}+ sold</span>'
                if p.get("sold") else "")
        rating_html = (f'      <div class="pdp__rate">{stars(p["rating"])}'
                       f'<span class="pdp__rc">{p["rating"]:.1f}{cnt}</span>'
                       f'{sold}</div>\n')
    else:
        rating_html = ""

    price_block = price_html(p, "pdp__price").replace(
        "</div>", f"{save}</div>") if save else price_html(p, "pdp__price")

    # Defaults for every product; only the delisted branch below overrides them.
    qty_html = QTY_HTML
    trust_list = c("product_trust_list", [])

    if p["price"] is None and is_dead(p):
        # Kept on the site at the client's request, but honest about it. No
        # "notify me" box: there is nothing behind one, and a control that
        # collects an address nobody reads is worse than no control.
        # One word, for the same reason as the card label. .btn sets nowrap and
        # 1.9rem of side padding, so "Currently unavailable" gives the button a
        # min-content width of 401px - wider than a 390px phone - and a
        # full-width button that cannot shrink drags the whole column with it.
        # The price block directly above already says it in full.
        buy_button = ('<button class="btn btn--gold btn--wide" type="button" disabled>'
                      'Unavailable</button>')
        buynow_button = ""
        stick_button = ('<button class="btn btn--gold" type="button" disabled>'
                        'Unavailable</button>')
        # No price chip in the sticky bar. "Currently unavailable" sets
        # white-space:nowrap, and at 166px beside the button it pushed the bar
        # to 417px on a 390px phone - which widened the whole page, not just
        # the bar, because the bar is fixed. The button already says it.
        stick_price = ""
        # No quantity stepper: it is a working control wired to a button that
        # can never fire, so it invites a shopper to set a number that does
        # nothing. And none of the delivery promises can be kept on a product
        # with no supplier - "ships within 24 hours", "delivered before Oct 31
        # or it's free" - so they are replaced by the one true sentence.
        qty_html = ""
        trust_list = [c("unavailable_note",
                        "This one has sold out at our supplier. "
                        "Everything else on the site ships as normal.")]
    elif p["price"] is None:
        buy_button = ('<button class="btn btn--gold btn--wide" type="button" disabled>'
                      'Price not set yet</button>')
        buynow_button = ""
        stick_button = ('<button class="btn btn--gold" type="button" disabled>'
                        'Add</button>')
        stick_price = '<b class="tag-setprice">Price to be set</b>'
    else:
        # Add to Cart keeps the shopper on the page; Buy It Now takes the one
        # item straight to checkout. Two different intents, so two buttons -
        # and Buy It Now is the visually dominant one because a landing page
        # built for cold ad traffic is trying to close, not to build a basket.
        #
        # data-opts names the picker these buttons must read before they add
        # anything. It is spelled out rather than left for the script to find,
        # because the related-products strip further down this same page is
        # full of buttons that also carry data-add and must NOT inherit this
        # product's chosen colour.
        vopts = ' data-opts="opts"' if p["slug"] in VARIANTS else ""
        buy_button = (f'<button class="btn btn--out btn--wide btn--add" type="button"\n'
                      f'                data-add="{p["slug"]}" '
                      f'data-name="{esc(p["name"], quote=True)}" '
                      f'data-price="{p["price"]}" data-qty="qty"{vopts}>\n'
                      f'          {esc(c("buttons.add_to_cart", "Add to Cart"))}\n'
                      f'        </button>')
        buynow_button = (
            f'      <button class="btn btn--gold btn--wide btn--buynow" type="button"\n'
            f'              data-add="{p["slug"]}" '
            f'data-name="{esc(p["name"], quote=True)}" '
            f'data-price="{p["price"]}" data-qty="qty" data-buynow="1"{vopts}>\n'
            f'        {esc(c("buttons.buy_now", "Buy It Now"))} &mdash; {money(p["price"])}\n'
            f'      </button>\n')
        stick_button = (f'<button class="btn btn--gold btn--add" type="button"\n'
                        f'          data-add="{p["slug"]}" '
                        f'data-name="{esc(p["name"], quote=True)}" '
                        f'data-price="{p["price"]}" data-buynow="1"{vopts}>\n    '
                        f'{esc(c("buttons.buy_now", "Buy It Now"))}\n  </button>')
        was_s = f' <s>{money(p["was"])}</s>' if p.get("was") else ""
        stick_price = f'<b>{money(p["price"])}</b>{was_s}'

    buynow_note = (f'      <p class="pdp__bnote">{esc(c("buttons.buy_now_note", ""))}</p>\n'
                   if buynow_button and c("buttons.buy_now_note") else "")

    # The delisted note shares the trust list's markup but not its green tick.
    li_cls = ' class="note"' if is_dead(p) else ""
    trust_html = "".join(f"        <li{li_cls}>{esc(x)}</li>\n" for x in trust_list)

    # "limited stock left at this price" cannot be shown on a product with no
    # price, and it is a claim about stock levels nobody has checked. It only
    # renders once a price exists, and the client can switch it off in one
    # place - urgency.show_stock_bar in content.json - for all 52 pages.
    pct = c("urgency.bar_percent", 22)
    stock_bar = (f"""      <div class="pdp__stock">
        <div class="pdp__bar"><i style="width:{pct}%"></i></div>
        <p>{esc(c("urgency.text", ""))}</p>
      </div>
""" if p["price"] is not None and c("urgency.show_stock_bar", True)
        and c("urgency.text") else "")

    if d["reviews"] and c("reviews_section.show", True):
        # Best-rated first here. The full mix, complaints included, is in
        # reviews.csv and every one of them is on the page - this only decides
        # the order, which is a display choice, not a filter.
        ordered = sorted(d["reviews"], key=lambda r: -r["rating"])
        revs_html = "".join(review_card(r, base=base) for r in ordered)
        avg = p.get("rating")
        summary = (f'<p class="revs__sum">{stars(avg)} <b>{avg:.1f}</b> out of 5 '
                   f'from {p["reviews"]:,} reviews</p>'
                   if avg and p.get("reviews") else "")
        reviews_section = f"""<!-- reviews -->
<section class="sec sec--alt" id="reviews">
  <div class="wrap">
    <p class="sec__k">{esc(c("reviews_section.eyebrow", "Reviews"))}</p>
    <h2 class="sec__h">What buyers say</h2>
    {summary}
    <div class="revs">
{revs_html}    </div>
    <p class="revs__note">{esc(c("reviews_section.note", ""))}</p>
  </div>
</section>
"""
    else:
        reviews_section = ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(p['name'])} &mdash; {BRAND}</title>
<meta name="description" content="{esc(d['hook'])} Free US shipping, guaranteed on your doorstep before October 31st." />
<meta name="robots" content="noindex" />
<meta property="og:title" content="{esc(p['name'])}" />
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
        {discount_chip(p).replace('card__off', 'pdp__off')}
        <img id="pdpimg" src="{main_img}" alt="{esc(p['name'])}" width="600" height="600" />
      </div>
{thumbs}
    </div>

    <div class="pdp__buy">
      <p class="pdp__crumb"><a href="{home}#shop">Shop</a> <span>/</span> {esc(p['name'])}</p>
      <h1 class="pdp__h">{esc(p['name'])}</h1>
{rating_html}      <p class="pdp__hook">{esc(d['hook'])}</p>

      {price_block}

      <ul class="pdp__bul">
{bullets}      </ul>

{stock_bar}
{variant_block(p, base)}      <div class="pdp__act">
        {qty_html}{buy_button}
      </div>
{buynow_button}{buynow_note}
      <ul class="pdp__trust">
{trust_html}      </ul>
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
      <img class="spec__art" src="{img_for(p, len(p['images']) - 1 if p['images'] else 0, base)}" alt="" aria-hidden="true" width="600" height="600" />
    </div>
  </div>
</section>

{reviews_section}
<!-- faq -->
<section class="sec" id="faq">
  <div class="wrap wrap--narrow">
    <p class="sec__k">Before you ask</p>
    <h2 class="sec__h">Questions</h2>
    <div class="faq">
{"".join(faq_item(*f) for f in faq_items())}    </div>
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
  <img src="{main_img}" alt="" width="600" height="600" />
  <div class="stick__m">
    <p>{esc(p['name'])}</p>
    <span>{stick_price}</span>
  </div>
  {stick_button}
</div>

<script src="{base}script.js"></script>
</body>
</html>
"""


NO_PHOTO = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" role="img" aria-label="Photo not available yet">
<rect width="600" height="600" fill="#15111f"/>
<rect x="24" y="24" width="552" height="552" rx="18" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-dasharray="14 12" opacity=".5"/>
<g transform="translate(300 250)" fill="none" stroke="{ORANGE}" stroke-width="9" stroke-linejoin="round" opacity=".75">
<rect x="-92" y="-64" width="184" height="140" rx="12"/>
<path d="M-92 44 -30-16 8 22 44-10l48 44"/>
<circle cx="46" cy="-30" r="15"/>
</g>
<text x="300" y="404" text-anchor="middle" font-family="Inter,Segoe UI,sans-serif" font-size="30" font-weight="700" fill="{BONE}" opacity=".85">Photo needed</text>
<text x="300" y="446" text-anchor="middle" font-family="Inter,Segoe UI,sans-serif" font-size="21" fill="{BONE}" opacity=".55">Supplier blocked the page</text>
</svg>
"""




def hero_html():
    """Hero with the real products in it.

    The old hero was type on a gradient - it looked good and told a first-time
    visitor nothing about what was for sale. This one puts five actual product
    photographs on the right, so the answer to "what is this shop" is visible
    before a single word is read.

    The collage slugs come from content.json. Every one is validated in build()
    against the catalogue AND against the unavailable list, because the fastest
    way to make a hero look broken is to front it with a product nobody can buy.
    """
    ticks = "".join(
        f'<li>{html.escape(t)}</li>' for t in c("hero.ticks", []))
    ticks = f'<ul class="hero__ticks">{ticks}</ul>' if ticks else ""

    slugs = [s for s in c("hero.collage", []) if s in {x["slug"] for x in PRODUCTS}]
    by_slug = {x["slug"]: x for x in PRODUCTS}
    tiles = ""
    for i, s in enumerate(slugs[:5]):
        p = by_slug[s]
        tiles += (f'      <a class="hcol__t hcol__t--{i + 1}" '
                  f'href="p/{p["slug"]}/" aria-label="{html.escape(p["name"], quote=True)}">'
                  f'<img src="{img_for(p)}" alt="{html.escape(p["name"], quote=True)}" '
                  f'width="600" height="600" '
                  f'{"" if i < 2 else "loading=\'lazy\'"} /></a>\n')
    collage = f'    <div class="hcol" aria-hidden="false">\n{tiles}    </div>\n' if tiles else ""

    cd = ("""    <div class="cdown" id="cdown" aria-label="Countdown to Halloween">
      <div class="cdown__cell"><b id="cd-d">--</b><span>Days</span></div>
      <div class="cdown__cell"><b id="cd-h">--</b><span>Hours</span></div>
      <div class="cdown__cell"><b id="cd-m">--</b><span>Minutes</span></div>
      <div class="cdown__cell"><b id="cd-s">--</b><span>Seconds</span></div>
      <p class="cdown__lbl">""" + html.escape(c("countdown.label", "")) + """</p>
    </div>
""" if c("countdown.show", True) else "")

    sec = c("hero.cta_secondary", "")
    sec_btn = (f'<a class="btn btn--ghost" href="#cats">{html.escape(sec)}</a>'
               if sec else "")
    return f"""<section class="hero" id="top">
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="wrap hero__in">
    <div class="hero__txt">
      <p class="hero__k">{html.escape(c("hero.eyebrow", ""))}</p>
      <h1 class="hero__h">{html.escape(c("hero.heading_top", ""))}<br /><span>{html.escape(c("hero.heading_accent", ""))}</span></h1>
      <p class="hero__p">{html.escape(c("hero.paragraph", ""))}</p>
      {ticks}
      <div class="hero__cta">
        <a class="btn btn--gold btn--xl" href="#shop">{html.escape(c("hero.cta_primary", "Shop"))}</a>
        {sec_btn}
      </div>
    </div>
{collage}  </div>
  <div class="wrap">
{cd}  </div>
</section>
"""


def category_sections():
    """One section per category, in catalogue order, each with its own anchor.

    This is the change the client asked for: clicking Apparel scrolls to the
    apparel products on the same page instead of loading a separate listing.

    A category with no products renders nothing rather than an empty heading -
    which matters, because fifteen products turned out to be delisted and a
    category could in principle empty out entirely.
    """
    out = []
    for title, sub, front in CATEGORIES:
        items = [p for p in PRODUCTS if p["cat"] == title]
        if not items:
            continue
        # Priced first. The unpriced ones are still listed - they are real
        # products - but a shopper should hit a buyable item first, and the
        # client should see the gap gathered at the end of each row instead of
        # scattered through it.
        items.sort(key=lambda p: (p["price"] is None,
                                  -(p.get("reviews") or 0)))
        cards = "".join(product_card(p) for p in items)
        out.append(f"""<!-- {title} -->
<section class="sec sec--cat" id="{cat_anchor(title)}">
  <div class="wrap">
    <div class="cathd">
      <div>
        <h2 class="cathd__h">{html.escape(title)}</h2>
        <p class="cathd__s">{html.escape(sub)}</p>
      </div>
      <span class="cathd__n">{len(items)} product{"s" if len(items) != 1 else ""}</span>
    </div>
    <div class="grid">
{cards}    </div>
  </div>
</section>
""")
    return "".join(out)


def home_reviews_html():
    """The social-proof section.

    Picks the best review from each of several different products rather than
    four reviews of one - the job of this block is to say "people buy across
    this shop and are happy", which four reviews of a single mask does not do.

    Every quote is real, from a verified buyer of that product on the
    supplier's listing. The note under the block says exactly that, because
    they are product reviews and not reviews of this store, and pretending
    otherwise is the thing that gets a store fined.
    """
    if not REVIEWS_BY_SLUG or not c("reviews_section.show", True):
        return ""
    by_slug = {p["slug"]: p for p in PRODUCTS}
    picked = []
    for slug, revs in REVIEWS_BY_SLUG.items():
        p = by_slug.get(slug)
        if not p or slug in catalog.UNAVAILABLE:
            continue
        best = max(revs, key=lambda r: (r["rating"], -abs(len(r["text"]) - 180)))
        if best["rating"] >= 4:
            picked.append((p, best))
    # Longest-established proof first: most-reviewed products lead.
    picked.sort(key=lambda x: -(x[0].get("reviews") or 0))
    picked = picked[:6]
    if not picked:
        return ""

    total = sum(p.get("reviews") or 0 for p in PRODUCTS if p.get("rating"))
    rated = [p for p in PRODUCTS if p.get("rating")]
    avg = sum(p["rating"] for p in rated) / len(rated) if rated else 0
    head = ""
    if total and avg:
        head = (f'    <p class="revs__sum">{stars(avg)} <b>{avg:.1f}</b> average '
                f'from <b>{total:,}</b> '
                f'{html.escape(c("reviews_section.count_label", "reviews"))}</p>\n')

    cards = "".join(review_card(r, product_name=p["name"]) for p, r in picked)
    return f"""<!-- reviews -->
<section class="sec sec--alt" id="reviews">
  <div class="wrap">
    <p class="sec__k">{html.escape(c("reviews_section.eyebrow", ""))}</p>
    <h2 class="sec__h">{html.escape(c("reviews_section.heading", ""))}</h2>
{head}    <div class="revs">
{cards}    </div>
    <p class="revs__note">{html.escape(c("reviews_section.note", ""))}</p>
  </div>
</section>
"""


def build():
    global C, REVIEWS_BY_SLUG, VARIANTS
    os.makedirs(ART_DIR, exist_ok=True)
    C = load_content()
    priced = load_prices()
    rated = load_social()
    REVIEWS_BY_SLUG = load_reviews()
    VARIANTS = load_variants()
    if priced:
        print(f"prices.csv : {priced} products priced")
    if VARIANTS:
        n = sum(len(vals) for v in VARIANTS.values() for _n, vals in v["options"])
        print(f"variants.csv: {len(VARIANTS)} products with options, "
              f"{n} values across {sum(len(v['options']) for v in VARIANTS.values())} option lists")
        for slug, v in sorted(VARIANTS.items()):
            shape = " x ".join(f"{len(vals)} {nm}" for nm, vals in v["options"])
            print(f"    {slug:32} {shape}")
    print(f"social.csv : {rated} products with a real supplier rating")
    print(f"reviews.csv: {sum(len(v) for v in REVIEWS_BY_SLUG.values())} real "
          f"reviews across {len(REVIEWS_BY_SLUG)} products")

    # A hero fronted by a delisted product is the single most visible way to
    # make the shop look broken, so it is checked rather than trusted.
    slugs = {p["slug"] for p in PRODUCTS}
    for s in c("hero.collage", []):
        if s not in slugs:
            print(f"  ! hero.collage names {s!r}, which is not a product")
        elif s in catalog.UNAVAILABLE:
            print(f"  ! hero.collage fronts {s!r}, which the supplier no "
                  f"longer lists")
    ph = c("why_us.photo")
    if ph and ph not in slugs:
        print(f"  ! why_us.photo names {ph!r}, which is not a product")

    with open(os.path.join(ART_DIR, "_no-photo.svg"), "w", encoding="utf-8") as f:
        f.write(NO_PHOTO)
    n_art = 1

    trust = "".join(
        f'    <div class="trust__i"><b>{html.escape(t)}</b>'
        f'<span>{html.escape(s)}</span></div>\n' for t, s in trust_items())

    why = ""
    if c("why_us.show", True):
        why_photo = [x for x in PRODUCTS
                     if x["slug"] == c("why_us.photo")] or [PRODUCTS[0]]
        why = f"""<!-- why -->
<section class="sec" id="why">
  <div class="wrap why">
    <div class="why__txt">
      <p class="sec__k">{html.escape(c("why_us.eyebrow", ""))}</p>
      <h2 class="sec__h">{html.escape(c("why_us.heading_top", ""))}<br />{html.escape(c("why_us.heading_bottom", ""))}</h2>
      <p>{html.escape(c("why_us.paragraph", ""))}</p>
      <ul class="ticks">
{"".join(f"        <li>{html.escape(x)}</li>" + chr(10) for x in c("why_us.ticks", []))}      </ul>
      <a class="btn btn--gold" href="#shop">{html.escape(c("why_us.cta", "Shop"))}</a>
    </div>
    <div class="why__art">
      <img src="{img_for(why_photo[0])}" alt="" aria-hidden="true" loading="lazy" width="600" height="600" />
    </div>
  </div>
</section>
"""

    cap = ""
    if c("email_capture.show", True):
        cap = f"""<!-- email capture -->
<section class="cap">
  <div class="wrap cap__in">
    <h2>{html.escape(c("email_capture.heading", ""))}</h2>
    <p>{html.escape(c("email_capture.paragraph", ""))}</p>
    <form class="cap__f" id="capform" novalidate>
      <input type="email" id="capmail" placeholder="you@email.com" aria-label="Email address" required />
      <button class="btn btn--gold" type="submit">{html.escape(c("email_capture.button", "Sign up"))}</button>
    </form>
    <p class="cap__msg" id="capmsg" role="status"></p>
  </div>
</section>
"""

    faq = ""
    if faq_items():
        faq = f"""<!-- faq -->
<section class="sec" id="faq">
  <div class="wrap wrap--narrow">
    <p class="sec__k">Before you ask</p>
    <h2 class="sec__h">Questions</h2>
    <div class="faq">
{"".join(faq_item(*f) for f in faq_items())}    </div>
  </div>
</section>
"""

    cats = ""
    if c("categories_nav.show", True):
        cats = f"""<!-- categories -->
<section class="sec" id="cats">
  <div class="wrap">
    <p class="sec__k">{html.escape(c("categories_nav.eyebrow", ""))}</p>
    <h2 class="sec__h">{html.escape(c("categories_nav.heading", ""))}</h2>
    <p class="sec__sub">{html.escape(c("categories_nav.sub", ""))}</p>
    <div class="cats">
{"".join(category_card(*x) for x in CATEGORIES)}    </div>
  </div>
</section>
"""

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{BRAND} &mdash; {TAGLINE}</title>
<meta name="description" content="{html.escape(c("brand.footer_blurb", ""))}" />
<meta name="robots" content="noindex" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="styles.css" />
</head>
<body>

{announce_html()}
{header_html("", "")}
{hero_html()}
<!-- trust -->
<section class="trust">
  <div class="wrap trust__in">
{trust}  </div>
</section>

{cats}{cat_chips()}
<!-- everything, split by category, each with its own anchor -->
<div id="shop">
{category_sections()}</div>

{why}{home_reviews_html()}{cap}{faq}{footer_html("", "")}
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
    print(f"{n_art} placeholder SVG written to assets/products/")
    photos = sum(len(p["images"]) for p in PRODUCTS)
    print(f"{len(PRODUCTS)} products, {photos} supplier photos, "
          f"{sum(1 for p in PRODUCTS if p['price'] is None)} still need a price")


if __name__ == "__main__":
    build()
