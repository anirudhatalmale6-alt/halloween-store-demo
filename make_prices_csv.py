#!/usr/bin/env python3
"""Regenerate prices.csv without losing anything already typed into it.

The file is the client's control panel: one row per product, he fills
your_price, he re-runs build.py. This script rewrites it so that newly
discovered source prices appear alongside his own figures, and it treats
whatever is already in the file as authoritative - a value he typed is never
overwritten by one I looked up.

The source_price column is reference only. build.py does not read it. It is
what the item sells for TODAY on the page the client linked, so he can price
against a real number instead of a guess.

Run:  python3 make_prices_csv.py
"""
import csv
import os

import catalog

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "prices.csv")
COLS = ["handle", "product", "your_price", "was_price", "set_by",
        "source_price", "source_was", "source"]

# set_by tells the two kinds of number apart, and it exists because the first
# version could not.
#
# That version preserved anything already in your_price as "kept as you had
# them". But some of those figures were not the client's - they were mine, from
# an earlier pass that ran before the prices were verified. When verification
# later threw two of them out, the CSV kept quoting them anyway, and the
# Shopify export shipped $45.99 for a product whose price is genuinely in
# dispute.
#
#   set_by = "source"  I filled this from a verified source price. Mine to
#                      refresh, and mine to CLEAR if it stops verifying.
#   set_by = "you"     typed by the client. Never touched.


# Below this, matching the source price cannot cover picking, packing and free
# US shipping. Flagged rather than silently adjusted - the markup is a business
# decision, and quietly inventing one would hide the problem.
FLOOR = 10.00


def existing():
    """What the client has already typed, keyed by handle."""
    if not os.path.exists(PATH):
        return {}
    out = {}
    with open(PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            h = (row.get("handle") or "").strip()
            if h:
                out[h] = row
    return out


def main():
    catalog.check()
    prev = existing()
    rows, prefilled, kept, thin, withdrawn = [], 0, 0, [], []

    for p in catalog.PRODUCTS:
        src = catalog.SOURCE_PRICES.get(p["slug"])
        old = prev.get(p["slug"], {})
        typed = (old.get("your_price") or "").strip()
        by = (old.get("set_by") or "").strip().lower()

        # A row with no set_by came from the version that had no such column,
        # so its figure is mine unless it is one I would still write today.
        client_typed = typed and by == "you"

        if client_typed:
            kept += 1
            your, was, by = typed, (old.get("was_price") or "").strip(), "you"
        elif src:
            your, was, by = f"{src[0]:.2f}", "", "source"
            prefilled += 1
            if src[0] < FLOOR:
                thin.append((p["slug"], src[0]))
        else:
            if typed:
                # I put this here before it was verified, and it no longer
                # verifies. Blank beats a figure I can no longer stand behind.
                withdrawn.append((p["slug"], typed))
            your, was, by = "", "", ""

        rows.append({
            "handle": p["slug"],
            "product": p["name"],
            "your_price": your,
            "was_price": was,
            "set_by": by,
            "source_price": f"{src[0]:.2f}" if src else "",
            "source_was": f"{src[1]:.2f}" if src and src[1] else "",
            "source": src[2] if src else "",
        })

    with open(PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)

    unpriced = sum(1 for r in rows if not r["your_price"])
    print(f"prices.csv: {len(rows)} rows")
    print(f"  {kept} kept as you had them")
    print(f"  {prefilled} filled from the source price")
    print(f"  {unpriced} still with no price")
    for slug, v in withdrawn:
        print(f"  - {slug}: cleared ${v} - I set that before it was verified "
              f"and it did not survive the check")
    for slug, v in thin:
        print(f"  ! {slug}: source sells it for ${v:.2f} - free shipping cannot "
              f"come out of that, needs your own markup")


if __name__ == "__main__":
    main()
