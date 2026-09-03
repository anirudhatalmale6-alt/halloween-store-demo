# Hollow & Hex — the store, with the real products in it

Live: https://anirudhatalmale6-alt.github.io/halloween-store-demo/

52 products, each with its own landing page on its own URL, built from the
links you sent.

    index.html            the store homepage
    p/<product>/          a landing page per product, 52 of them
    catalog.py            the products - names, descriptions, bullets, photos
    prices.csv            YOUR PRICES GO HERE
    content.json          EVERY line of shipping/guarantee/countdown wording
    social.csv            star rating, review count and units sold per product
    reviews.csv           the review quotes themselves
    make_prices_csv.py    regenerates prices.csv without losing your edits
    build.py              regenerates every page from the files above
    styles.css            all styling
    script.js             cart, gallery, countdown, menu, category jump bar

---

## Where it stands

| | |
|---|---|
| Products with a real photo | **52 of 52** |
| Products with a verified price | **22** |
| Products the supplier no longer lists | **15** |
| Products that still need a price from you | **15** |
| Products with a real star rating | **32** |
| Real review quotes on the site | **126** |

Every product has its supplier's own photographs. Nothing is a placeholder.

### What changed in this round

- The homepage now has **a section per category** with its own heading and
  count. The category tiles and the sticky jump bar under the header both
  scroll you down to them instead of loading a separate page.
- The hero leads with **five real product photographs**, and *Shop the
  Collection* is now the one obviously dominant button on the screen.
- Cards show the price, the crossed-out compare-at price, the discount
  percentage, the star rating and review count, and a full-width Add to Cart.
- Every product page has **Buy It Now** beside Add to Cart.
- There is a **reviews section** on the homepage and on every rated product
  page, built from real reviews (see below), with the markup and the CSV column
  already in place for customer photos.
- All of the shipping, delivery, guarantee, warehouse and countdown wording
  moved into **`content.json`** — one file, one place.
- Fixed on the way past: the cart drawer was asking for `.svg` thumbnails long
  after every product got a real `.jpg` photograph, so every image in the cart
  was a silent 404.

---

## 1. The 15 products that are no longer available

These load nothing on TikTok and appear nowhere else, so they cannot be bought
at any price:

    floating-candles-kidsafe        led-mask-4-modes
    floating-candles-12pc           led-mask-gloves-set
    pumpkin-night-light-mini        pumpkin-skull-slippers
    halloween-tree-lights-black     toddler-spooky-goose-sweater
    skeleton-pumpkin-figures-3      pumpkin-dog-collar
    bat-wall-stickers-160           ghostface-phone-case
    garage-door-bat-magnets         glow-cobwebs-spiders
    spider-web-kit-lights

This is not one failed request. Each returns the same error to every URL form —
the bare product id and the full slug alike — in three separate runs hours
apart, while other products loaded normally from the same browser seconds
later. None of them appears even once across 99 pages I pulled: not in a single
recommendation strip, not in their own seller's store listing, not in a
category page.

Worth checking on your phone before you write them off, since you are in the
US. If they open for you, tell me and I will price them.

**They are still on the site.** All 15 are unpriced, so their buy buttons are
already switched off — nothing can be ordered that you cannot fulfil — and it
is your call whether to drop them, not mine. In the Shopify import file they
arrive as **drafts**, tagged `unavailable-at-supplier`, so uploading the file
cannot put them on a live storefront by accident.

Two category tiles used to be fronted by items on this list (the bat wall
stickers and the Ghostface phone case). Those tiles now point at the Boo
kitchen rug set and the trick-or-treat phone case instead.

---

## 2. Setting your prices

`prices.csv` has a row per product with your price next to the source price:

    handle,product,your_price,was_price,set_by,source_price,source_was,source

- **your_price** — what you charge. Edit this.
- **set_by** — `you` if you typed it, `source` if I filled it in. **Put `you`
  in this column whenever you change a price**, or the next regeneration will
  overwrite your figure with the source price again.
- **source_price / source_was / source** — what the item sells for today on the
  page you linked, and where I read it. Reference only; the build ignores it.

Then run `python3 build.py`. Products with no price stay marked **Price to be
set** with the buy button switched off, so a half-priced catalogue is obviously
half-finished rather than quietly selling something for nothing.

The build refuses to guess: a blank cell leaves a product unpriced rather than
becoming `$0.00`, a `was_price` at or below the selling price prints a warning
and drops the discount badge rather than rendering a negative saving, and text
that is not a number prints a warning and leaves the product unpriced.

**One price needs your judgement rather than a copy.** Walmart sells the scary
face headrest covers for $1.99. Free US shipping cannot come out of $1.99, so
that one needs a real markup or it costs you money on every order.

---

## 2b. The star ratings and the reviews

`social.csv` — one row per product:

    handle,product,rating,reviews,sold,set_by,source

`reviews.csv` — the quotes:

    handle,name,rating,title,text,verified,photo

**Every number and every quote in both files was read off the supplier's own
listing for that exact product.** Nothing is invented. 32 of the 52 have a
rating; the other 20 have empty cells and the star row simply does not appear
on them. There is no fallback rating anywhere in the build — a 4.8 nobody
earned is not a placeholder, it is a claim, and it would be your name on it.

Reviewer names arrive already masked by the supplier (`S**r`), so no real
name is republished.

Three things to know before you use them:

1. **They are reviews of the product, not of your store.** The line under the
   reviews section says exactly that. Leave it there until your own orders
   start producing reviews. Quoting a product review is normal; presenting it
   as your own customer is not.
2. **They are yours to edit.** Delete a row from `reviews.csv` and it is gone
   on the next build. The mix includes honest four-star reviews with
   complaints, which is deliberate — a wall of five stars reads as fake — but
   the choice is yours.
3. **A reviews app replaces all of this.** Judge.me or Loox on Shopify pulls
   reviews from your real orders and takes over the same fields. Free to start.

The `photo` column is empty in every row today. The supplier's review images
sit behind expiring signed URLs and would break within days, so they were left
out rather than shipped as future 404s. Put a filename in that column and the
review grows a photo — the markup and the styling are already there.

---

## 2c. The wording you will want to change

Everything about shipping, delivery, guarantees and urgency is in
**`content.json`**. One file. Change a line, run `python3 build.py`, and it
changes on the homepage and on all 52 product pages at once.

That covers the announcement bar, the trust bar, the four promises on every
product page, the "selling fast" line, the countdown label, the FAQ, and the
reasons-to-buy block. Empty a line and it disappears rather than leaving a gap;
set a `show` flag to `false` and the whole block goes.

These are the claims that get a store in trouble when they go stale, which is
why they are the ones that had to be trivial to correct. None of them is
enforced by code — if the page promises 24-hour dispatch, that promise is
yours to keep.

---

## 3. How the prices were obtained, and why some are missing

TikTok hides a product's price on its own page. It prints `"3*"` where the
price should be — real leading digit, rest starred. The price is visible
elsewhere: every product page carries strips of *other* products with their
prices unmasked, and every seller has a store page listing their whole range.
So each price was read off somebody else's page.

Two things made that harder than it sounds.

**The structured data lies by omission.** The same masked price appears in the
page's schema.org block truncated to a bare integer, so a product selling for
$31.99 reports `"price": 3`. Ten products would have been priced at roughly a
tenth of their value by anything that trusted it.

**The two sources disagree, on 15 products, sometimes threefold.** Recommendation
strips quote the "from" price; a seller's store page quotes the selected
variant. Both are real and they are not the same number — the tripod cauldron
is $31.99 in the strips and $54.99 in its seller's store.

The tie-break is the mask itself. It is useless for pricing and decisive for
refuting: a $54.99 claim cannot survive a `"3*"` mask. That threw out 15 wrong
figures, including one case where the strips agreed with each other and were
still wrong — $9.11 against a `"1*"` mask, where the real price is $19.09.

**6 products have two candidates that both fit the mask.** They are left
unpriced rather than guessed. **9 more** appear in no strip and no store page I
could reach. Those 15 are the ones that still need a number, and reading them
off your phone will take you about two minutes.

---

## 4. Two things worth reading before you launch

**The four hero masks.** Four of the LED masks are Marvel character products —
Spider-Man and Spider-Gwen. They are listed under descriptive names rather than
the character names, because selling unlicensed merchandise under a trademarked
name is one of the fastest ways to get a Shopify store suspended and a payment
processor to freeze a payout. Selling the item is your call and your supplier's
problem; putting the trademark in your product title makes it yours.

**No star ratings, and no reviews section.** The earlier demo had them, because
the products on it were invented too. These products are real and will go in
front of real customers, so nothing on the site claims a rating or a review
count. Install a reviews app on Shopify (Judge.me and Loox both have free
tiers) and the stars appear on their own, from actual orders.

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
store full of broken images later, so all 58 photos are saved in this repo.

**Written detail is optional everywhere.** A product with nothing but a name, a
photo and a one-line description still produces a complete page — bullets fall
back to sentences from the description, and any section with no content hides
itself instead of rendering an empty box.

**The "selling fast" bar** on each product page is an urgency claim, not a real
stock reading. Set `SHOW_STOCK_BAR = False` at the top of `build.py` to remove
it from all 52 pages at once.

**Discounts round down.** $34.99 down to $21.99 is 37.1% off and shows as 37%,
never 38. A saving is always rounded in the customer's favour.
