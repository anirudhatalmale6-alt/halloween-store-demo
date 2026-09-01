# Hollow & Hex — Halloween storefront demo

A hand-coded demo storefront built to show the look, feel and interaction of a
Halloween dropshipping store. No frameworks, no build step, no dependencies —
plain HTML, CSS and JavaScript.

**Live:** https://anirudhatalmale6-alt.github.io/halloween-store-demo/

## What's in it

**One store, plus a dedicated landing page per product.** Every product has its
own URL — `/p/animatronic-reaper/`, `/p/fog-machine/` and so on — so an ad can
point straight at a single product, while the visitor still lands inside the
shop and can browse the rest instead of bouncing.

Each landing page has a three-shot gallery, a buy box with a quantity stepper,
benefit bullets, a feature section, a specification table, what's in the box,
product reviews, an FAQ, related products, and a sticky buy bar on mobile.

- Sticky header, mobile menu, announcement bar
- Live countdown to the next October 31st (recalculates itself every year)
- Product grid driven from a single list in `build.py`
- Working cart — add, change quantity, remove, running subtotal, saved to
  `localStorage` so it survives a page refresh
- Category tiles, review cards, email capture with validation, FAQ accordion
- Reveal-on-scroll animations, and a `prefers-reduced-motion` path that turns
  them all off for anyone who has asked their device for less movement
- Fully responsive — checked at 1440, 1280, 1024, 860, 640 and 390 px with no
  horizontal overflow at any of them

## Files

    build.py                page generator — products, copy, artwork
    index.html              generated, do not edit by hand
    p/<slug>/index.html     generated landing page, one per product
    styles.css              all styling; every colour is a variable at the top
    script.js               countdown, cart, gallery, sticky bar, menu, form
    assets/products/*.svg   generated product artwork, 3 views per product

## Editing

Everything a shop owner normally changes lives at the top of `build.py` —
`PRODUCTS`, `CATEGORIES`, `REVIEWS`, `TRUST`, `FAQ`, and `DETAILS` for the
per-product landing page copy. Add a dict, then:

    python3 build.py

That regenerates the homepage, all ten landing pages and all the artwork.

`DETAILS` is optional. A product with no entry still gets a complete landing
page from the fallbacks — name, price and a photo are enough to ship one, and
the written detail is an upgrade rather than a blocker.

## Artwork

The product images are hand-drawn SVG rather than stock photography, so there
are no licensing questions and the whole set stays on-palette. On a real store
these get swapped for supplier photography.

Each product is drawn once and staged three ways for the gallery — a catalogue
shot on a glow, a close-up crop, and an in-use shot on a night porch. They are
three genuinely different views of the same drawing, not one picture repeated.

## Note

This is a design demo. Checkout is deliberately not wired to a payment
provider — a live store would run on Shopify or WooCommerce for that.
