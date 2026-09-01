# Hollow & Hex — Halloween storefront demo

A hand-coded demo storefront built to show the look, feel and interaction of a
Halloween dropshipping store. No frameworks, no build step, no dependencies —
plain HTML, CSS and JavaScript.

**Live:** https://anirudhatalmale6-alt.github.io/halloween-store-demo/

## What's in it

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

    build.py      page generator — product list, categories, reviews, FAQ, artwork
    index.html    generated, do not edit by hand
    styles.css    all styling; every colour is a variable at the top
    script.js     countdown, cart, menu, form, scroll reveals
    assets/products/*.svg   generated product artwork

## Editing

Everything a shop owner normally changes lives at the top of `build.py` —
`PRODUCTS`, `CATEGORIES`, `REVIEWS`, `TRUST`, `FAQ`. Add a dict, then:

    python3 build.py

That regenerates `index.html` and all the artwork.

## Artwork

The product images are hand-drawn SVG rather than stock photography, so there
are no licensing questions and the whole set stays on-palette. On a real store
these get swapped for supplier photography.

## Note

This is a design demo. Checkout is deliberately not wired to a payment
provider — a live store would run on Shopify or WooCommerce for that.
