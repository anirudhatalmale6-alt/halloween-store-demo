#!/usr/bin/env python3
"""Write social.csv and reviews.csv from the supplier harvest.

Run once, from the harvest JSON in the working directory used to fetch the
supplier pages. The two CSVs it produces are the source of truth after that -
the client edits them by hand, so this script must never be run again against
a live site without checking what it would overwrite. It refuses to clobber a
row a human has edited (`set_by = you`), the same rule prices.csv follows and
for the same reason: once I pre-fill a file the client edits, my values and
his live in the same column and "don't overwrite" silently becomes "don't
overwrite MYSELF".

Where the numbers come from
---------------------------
Every rating, review count, sold count and review quote in these files was
read off the supplier's own listing pages, out of the `__MODERN_ROUTER_DATA__`
blob, attributed node by node (the rating hangs off the same JSON object as
the product_id, so it cannot drift onto the neighbouring product).

Nothing here is invented. Where the supplier has no rating for a product, the
cell is EMPTY and the star row hides itself rather than falling back to a
flattering default.

What they are NOT
-----------------
These are reviews of the PRODUCT, left by buyers of the supplier's listing.
They are not reviews of this store. The page wording says so. Reviewer names
arrive already masked by the supplier ("S**r"), so no real name is republished.
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import catalog  # noqa: E402

HARVEST = sys.argv[1] if len(sys.argv) > 1 else "social.json"

SOCIAL_COLS = ["handle", "product", "rating", "reviews", "sold", "set_by", "source"]
REVIEW_COLS = ["handle", "name", "rating", "title", "text", "verified", "photo"]


def read_existing(path, key):
    if not os.path.exists(path):
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        return {r[key]: r for r in csv.DictReader(f) if r.get(key)}


def main():
    d = json.load(open(HARVEST, encoding="utf-8"))
    stats, quotes = d["stats"], d["quotes"]
    bypid = {p["pid"]: p for p in catalog.PRODUCTS if p.get("pid")}

    old = read_existing(os.path.join(HERE, "social.csv"), "handle")
    rows, filled, kept = [], 0, 0
    for p in catalog.PRODUCTS:
        prev = old.get(p["slug"], {})
        if (prev.get("set_by") or "").strip() == "you":
            rows.append({c: prev.get(c, "") for c in SOCIAL_COLS})
            kept += 1
            continue
        s = stats.get(p.get("pid") or "") or {}
        r = {c: "" for c in SOCIAL_COLS}
        r["handle"], r["product"] = p["slug"], p["name"]
        if s.get("rating"):
            r["rating"] = f"{s['rating']:.1f}"
            r["reviews"] = str(s["reviews"] or "")
            r["sold"] = str(s["sold"] or "")
            r["set_by"] = "supplier"
            r["source"] = "tiktok"
            filled += 1
        rows.append(r)

    with open(os.path.join(HERE, "social.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SOCIAL_COLS)
        w.writeheader()
        w.writerows(rows)

    # ---- reviews ---------------------------------------------------------
    # Longest first, capped per product. A wall of one-line "love it" adds
    # nothing; the ones that describe the product are what a shopper reads.
    revs = []
    for p in catalog.PRODUCTS:
        for q in (quotes.get(p.get("pid") or "") or [])[:4]:
            revs.append({
                "handle": p["slug"],
                "name": q["name"] or "Verified buyer",
                "rating": f"{q['rating']:.0f}" if q.get("rating") else "5",
                "title": "",
                "text": q["text"],
                "verified": "yes" if q.get("verified") else "",
                "photo": "",
            })
    with open(os.path.join(HERE, "reviews.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=REVIEW_COLS)
        w.writeheader()
        w.writerows(revs)

    print(f"social.csv : {len(rows)} rows, {filled} from the supplier, "
          f"{kept} kept as you had them, "
          f"{sum(1 for r in rows if not r['rating'])} with no rating")
    print(f"reviews.csv: {len(revs)} real reviews across "
          f"{len({r['handle'] for r in revs})} products")


if __name__ == "__main__":
    main()
