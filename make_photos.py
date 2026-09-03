#!/usr/bin/env python3
"""Download every supplier photo for each product, and the customer review photos.

Why this exists
---------------
Each product landing page showed ONE photo. That single image is the catalogue
shot carried in the `og_info` parameter of the short link's first redirect hop,
which is all a redirect hop carries - the rest of the supplier's gallery lives
in the product page itself. This script pulls the whole gallery down, converts
it, and records it in photos.csv.

The photos are saved LOCALLY and served from this site. The supplier's CDN URLs
carry expiring signatures (`t=`, `ps=`, `shp=` in the query string); linking to
them directly would give a shop full of broken images within days. The URL is
kept in photos.csv as provenance, not as the thing the browser loads.

De-duplication
--------------
The main photo already on disk stays at position 1 - it is the one the client
has been looking at, and re-ordering approved pictures is not what was asked
for. The gallery is appended after it, minus any frame that is the same picture
again. "Same" is decided by a perceptual average-hash on a 16x16 greyscale
reduction, not by URL or by byte equality: the supplier serves the identical
photograph under several URIs and at several crops, and a gallery that shows
one picture three times is worse than a gallery of one.

Review photos
-------------
Only reviews ALREADY IN reviews.csv get a photo. This script never adds a
review. It matches on the review text it harvested against the text in the CSV,
so a review the client has edited or deleted simply does not match and stays
without a photo - his file stays the source of truth.

Re-running
----------
Safe. Existing files are skipped unless --force. photos.csv is rewritten from
what is on disk, so deleting a jpg and re-running removes the row.
"""
import csv, hashlib, io, json, os, sys, time, urllib.request

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import catalog  # noqa: E402

PROD_DIR = os.path.join(HERE, "assets", "products")
REV_DIR = os.path.join(HERE, "assets", "reviews")
PHOTOS_CSV = os.path.join(HERE, "photos.csv")
REVIEWS_CSV = os.path.join(HERE, "reviews.csv")

MAX_PER_PRODUCT = 8          # incl. the main photo
GAL_PX, GAL_Q = 900, 78
REV_PX, REV_Q = 600, 75
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"

FORCE = "--force" in sys.argv


def fetch(url, tries=3):
    for n in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return urllib.request.urlopen(req, timeout=30).read()
        except Exception as e:
            if n == tries - 1:
                print(f"    ! {e}")
                return None
            time.sleep(1.5 * (n + 1))


def ahash(im):
    """16x16 greyscale average hash. Survives re-encoding and re-cropping to a
    different size, which is exactly how the supplier serves the same photo."""
    g = im.convert("L").resize((16, 16), Image.BILINEAR)
    px = list(g.getdata())
    avg = sum(px) / len(px)
    return int("".join("1" if v > avg else "0" for v in px), 2)


def dist(a, b):
    return bin(a ^ b).count("1")


def save_jpeg(raw, path, px, q):
    im = Image.open(io.BytesIO(raw))
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    if max(im.size) > px:
        im.thumbnail((px, px), Image.LANCZOS)
    im.save(path, "JPEG", quality=q, optimize=True, progressive=True)
    return im


def main():
    src = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") \
        else "gallery.json"
    data = json.load(open(src))
    by_pid = {p["pid"]: p for p in catalog.PRODUCTS if p.get("pid")}
    os.makedirs(REV_DIR, exist_ok=True)

    rows = []
    added = skipped = dupes = 0

    for pid, blob in data.items():
        p = by_pid.get(pid)
        if not p:
            continue
        slug = p["slug"]
        main_path = os.path.join(PROD_DIR, f"{slug}.jpg")
        if not os.path.exists(main_path):
            print(f"  {slug}: no main photo on disk, skipping")
            continue

        seen = [ahash(Image.open(main_path))]
        rows.append({"handle": slug, "position": 1,
                     "file": f"{slug}.jpg", "source": "og_info (first hop)"})

        pos = 1
        for url in blob["images"]:
            if pos >= MAX_PER_PRODUCT:
                break
            out = os.path.join(PROD_DIR, f"{slug}-{pos + 1}.jpg")
            if os.path.exists(out) and not FORCE:
                # Already downloaded on an earlier run. Hash it so the images
                # that follow are still compared against it.
                seen.append(ahash(Image.open(out)))
                rows.append({"handle": slug, "position": pos + 1,
                             "file": os.path.basename(out), "source": url})
                pos += 1
                skipped += 1
                continue
            raw = fetch(url)
            if not raw:
                continue
            try:
                im = Image.open(io.BytesIO(raw))
                h = ahash(im)
            except Exception as e:
                print(f"    ! {slug}: undecodable image, {e}")
                continue
            if any(dist(h, s) <= 6 for s in seen):
                dupes += 1
                continue
            save_jpeg(raw, out, GAL_PX, GAL_Q)
            seen.append(h)
            rows.append({"handle": slug, "position": pos + 1,
                         "file": os.path.basename(out), "source": url})
            pos += 1
            added += 1
        print(f"  {slug}: {pos} photo(s)")

    # Products this harvest said nothing about (the two non-TikTok sources, and
    # anything the supplier has since pulled) keep whatever is already on disk.
    have = {r["handle"] for r in rows}
    for p in catalog.PRODUCTS:
        if p["slug"] in have:
            continue
        for i in range(len(p["images"])):
            f = f"{p['slug']}.jpg" if i == 0 else f"{p['slug']}-{i + 1}.jpg"
            if os.path.exists(os.path.join(PROD_DIR, f)):
                rows.append({"handle": p["slug"], "position": i + 1,
                             "file": f, "source": p.get("source") or ""})

    rows.sort(key=lambda r: (r["handle"], r["position"]))
    with open(PHOTOS_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["handle", "position", "file", "source"])
        w.writeheader()
        w.writerows(rows)

    print(f"\ngallery: {added} downloaded, {skipped} already there, "
          f"{dupes} dropped as the same picture again")
    print(f"photos.csv: {len(rows)} rows, "
          f"{len({r['handle'] for r in rows})} products")

    review_photos(data, by_pid)


def norm(s):
    return " ".join((s or "").split()).lower()


def review_photos(data, by_pid):
    """Attach a photo to reviews that are ALREADY in reviews.csv. Never adds one."""
    with open(REVIEWS_CSV, encoding="utf-8") as fh:
        revs = list(csv.DictReader(fh))
        cols = list(csv.DictReader(open(REVIEWS_CSV, encoding="utf-8")).fieldnames)

    # slug -> normalised review text -> [urls]
    idx = {}
    for pid, blob in data.items():
        p = by_pid.get(pid)
        if not p:
            continue
        for r in blob["reviews"]:
            if r["images"]:
                idx.setdefault(p["slug"], {})[norm(r["text"])] = r["images"]

    got = kept = 0
    for row in revs:
        if row.get("photo"):
            kept += 1                      # a value already there is the client's
            continue
        urls = idx.get(row["handle"], {}).get(norm(row["text"]))
        if not urls:
            continue
        name = hashlib.sha1((row["handle"] + norm(row["text"])).encode()).hexdigest()[:8]
        fn = f"{row['handle']}-{name}.jpg"
        out = os.path.join(REV_DIR, fn)
        if not os.path.exists(out) or FORCE:
            raw = fetch(urls[0])
            if not raw:
                continue
            try:
                save_jpeg(raw, out, REV_PX, REV_Q)
            except Exception as e:
                print(f"    ! review photo {fn}: {e}")
                continue
        row["photo"] = fn
        got += 1

    with open(REVIEWS_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols)
        w.writeheader()
        w.writerows(revs)
    print(f"review photos: {got} attached, {kept} left as you set them, "
          f"{len(revs)} reviews total")


if __name__ == "__main__":
    main()
