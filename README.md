# Hollow & Hex — the store, with the real products in it

Live: https://anirudhatalmale6-alt.github.io/halloween-store-demo/

52 products, each with its own landing page on its own URL, built from the
links you sent.

    index.html            the store homepage
    p/<product>/          a landing page per product, 52 of them
    catalog.py            the products - names, descriptions, bullets, photos
    prices.csv            YOUR PRICES GO HERE
    build.py              regenerates every page from the two files above
    styles.css            all styling
    script.js             cart, gallery, countdown, menu

---

## Setting your prices

This is the one thing left to do, and it is the only thing I could not get for
you. TikTok Shop puts the price behind a captcha, and in any case the selling
price is your margin decision, not a number to copy off a supplier.

1. Open `prices.csv`. It has a row per product, already named.
2. Fill in `your_price`, and `was_price` if you want a crossed-out "was" price
   and a discount badge.
3. Run `python3 build.py`.

Every page updates. Products you have not priced yet stay marked **Price to be
set** with the buy button switched off — so a half-priced catalogue is
obviously half-finished rather than quietly selling something for nothing.

The build refuses to guess:

- a blank cell leaves the product unpriced, it does not become `$0.00`
- a `was_price` that is not above `your_price` prints a warning and drops the
  discount badge rather than rendering a negative saving
- text that is not a number prints a warning and leaves the product unpriced

---

## Where the products came from

You sent 57 links. Here is what each one actually yielded.

| Source | Links | Products | What came back |
|---|---|---|---|
| TikTok Shop | 54 | 50 | Name and catalogue photo. Four links were duplicates of products you had already sent. |
| TikTok video | 1 | 0 | An ordinary video post, no product attached |
| splatmatofficial.com | 1 | 1 | Everything — name, price, was-price, description, 4 photos |
| Walmart | 1 | 1 | Name only. Walmart blocks automated requests, so no photo and no price. |

The TikTok Shop links are region-locked and bounce a non-US request to the
TikTok homepage. The product data turned out to be in the **first redirect
hop** — the short link forwards to `shop.tiktok.com/us/pdp/<id>` carrying the
title and photo in the URL, and only then does the geo-check fire. Following
the redirects to the end throws that away.

Prices are not in that hop, which is why `prices.csv` exists.

---

## Two things worth reading before you launch

**The four hero masks.** Four of the LED masks are Marvel character products —
Spider-Man and Spider-Gwen. I have listed them under descriptive names rather
than the character names, because selling unlicensed merchandise under a
trademarked name is one of the fastest ways to get a Shopify store suspended
and a payment processor to freeze a payout. Selling the item is your call and
your supplier's problem; putting the trademark in your product title makes it
yours. Keep the names generic.

**No star ratings, and no reviews section.** The earlier demo had them, because
the products on it were invented too. These products are real and will go in
front of real customers, so there is nothing on the site claiming a rating or a
review count. Install a reviews app on Shopify (Judge.me and Loox both have
free tiers) and the stars appear on their own, from actual orders.

---

## Possible duplicates

Two pairs looked close enough to be the same item listed twice. Both are
included; check before you import both.

- `halloween-tree-lights-black` and `halloween-tree-lights-24led`
- `skeleton-cardigan-black` and `skeleton-cardigan-colours`

---

## Notes on the build

**Photos are hosted here, not hot-linked.** The TikTok CDN URLs carry expiring
signatures. Importing straight from them would work today and leave you with a
store full of broken images later, so all 54 photos are saved in this repo.

**Written detail is optional everywhere.** A product with nothing but a name, a
photo and a one-line description still produces a complete page — bullets fall
back to sentences from the description, and any section with no content hides
itself instead of rendering an empty box.

**The "selling fast" bar** on each product page is an urgency claim, not a real
stock reading. Set `SHOW_STOCK_BAR = False` at the top of `build.py` to remove
it from all 52 pages at once.

**Discounts round down.** $34.99 down to $21.99 is 37.1% off and shows as 37%,
never 38. A saving is always rounded in the customer's favour.
