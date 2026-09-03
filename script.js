/* =========================================================
   Hollow & Hex - storefront behaviour
   Cart state lives in localStorage so it survives a refresh.
   ========================================================= */
(function () {
  'use strict';

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var money = function (n) { return '$' + n.toFixed(2); };

  /* This file is shared by the homepage and every product landing page, and
     the landing pages sit two directories down at /p/<slug>/. Two consequences
     run through everything below:
       1. asset paths must be prefixed with BASE, not hardcoded
       2. every element lookup must tolerate absence - a landing page has no
          email capture, the homepage has no gallery */
  var BASE = (document.body.getAttribute('data-base') || '');

  /* Bind only if the element is actually on this page. */
  function on(el, ev, fn) { if (el) { el.addEventListener(ev, fn); } }

  /* ---------------------------------------------------------
     Header: solid background once you leave the very top
     --------------------------------------------------------- */
  var hdr = $('#hdr');
  var onScroll = function () {
    if (hdr) { hdr.classList.toggle('hdr--solid', window.scrollY > 24); }
    stickBar();
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---------------------------------------------------------
     Mobile menu
     --------------------------------------------------------- */
  var burger = $('#burger');
  var nav = $('#nav');
  on(burger, 'click', function () {
    var open = nav.classList.toggle('on');
    burger.classList.toggle('on', open);
    burger.setAttribute('aria-expanded', String(open));
  });
  $$('#nav a').forEach(function (a) {
    a.addEventListener('click', function () {
      nav.classList.remove('on');
      burger.classList.remove('on');
      burger.setAttribute('aria-expanded', 'false');
    });
  });

  /* ---------------------------------------------------------
     Countdown to the next October 31st
     --------------------------------------------------------- */
  var cd = {
    d: $('#cd-d'), h: $('#cd-h'), m: $('#cd-m'), s: $('#cd-s'), ann: $('#ann-count')
  };

  function target() {
    var now = new Date();
    var y = now.getFullYear();
    var t = new Date(y, 9, 31, 23, 59, 59); // month 9 = October
    if (t < now) { t = new Date(y + 1, 9, 31, 23, 59, 59); }
    return t;
  }

  var pad = function (n) { return n < 10 ? '0' + n : String(n); };

  function tickCountdown() {
    var diff = Math.max(0, target() - new Date());
    var s = Math.floor(diff / 1000);
    var d = Math.floor(s / 86400);
    var h = Math.floor((s % 86400) / 3600);
    var m = Math.floor((s % 3600) / 60);
    var sec = s % 60;
    if (cd.d) { cd.d.textContent = pad(d); }
    if (cd.h) { cd.h.textContent = pad(h); }
    if (cd.m) { cd.m.textContent = pad(m); }
    if (cd.s) { cd.s.textContent = pad(sec); }
    if (cd.ann) {
      cd.ann.textContent = d + (d === 1 ? ' DAY' : ' DAYS') + ' TO HALLOWEEN';
    }
  }
  tickCountdown();
  setInterval(tickCountdown, 1000);

  /* ---------------------------------------------------------
     Cart
     --------------------------------------------------------- */
  var KEY = 'hollowhex.cart.v1';
  var cart = [];

  try {
    var raw = localStorage.getItem(KEY);
    if (raw) { cart = JSON.parse(raw) || []; }
    if (!Array.isArray(cart)) { cart = []; }
  } catch (e) { cart = []; }

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch (e) { /* private mode */ }
  }

  var cartEl = $('#cart');
  var scrim = $('#scrim');
  var bodyEl = $('#cartbody');
  var totEl = $('#carttot');
  var nEl = $('#cartn');

  function count() {
    return cart.reduce(function (a, i) { return a + i.qty; }, 0);
  }

  function render() {
    if (!bodyEl || !nEl || !totEl) { return; }
    var n = count();
    nEl.textContent = String(n);
    nEl.classList.toggle('on', n > 0);

    if (!cart.length) {
      bodyEl.innerHTML = '<p class="cart__empty">Your cart is empty.<br />The neighbours are winning.</p>';
      totEl.textContent = '$0.00';
      return;
    }

    bodyEl.innerHTML = cart.map(function (i) {
      /* .jpg, not .svg. The demo's hand-drawn placeholders were SVGs and this
         line still asked for one long after every product got its real
         supplier photograph - so every thumbnail in the cart drawer was a
         404. Nothing in the drawer looked broken enough to notice: an <img>
         that fails to load in a fixed-size box just renders empty. */
      return '<div class="ci" data-slug="' + i.slug + '">' +
        '<img src="' + BASE + 'assets/products/' + i.slug + '.jpg" alt="" ' +
        'onerror="this.src=\'' + BASE + 'assets/products/_no-photo.svg\'" />' +
        '<div class="ci__m">' +
          '<p class="ci__n">' + i.name + '</p>' +
          '<p class="ci__p">' + money(i.price * i.qty) + '</p>' +
          '<div class="ci__q">' +
            '<button type="button" data-step="-1" aria-label="Decrease quantity">&minus;</button>' +
            '<b>' + i.qty + '</b>' +
            '<button type="button" data-step="1" aria-label="Increase quantity">+</button>' +
          '</div>' +
        '</div>' +
        '<button class="ci__x" type="button" data-remove aria-label="Remove item">&times;</button>' +
      '</div>';
    }).join('');

    var total = cart.reduce(function (a, i) { return a + i.price * i.qty; }, 0);
    totEl.textContent = money(total);
  }

  function openCart() {
    if (!scrim || !cartEl) { return; }
    scrim.hidden = false;
    requestAnimationFrame(function () {
      scrim.classList.add('on');
      cartEl.classList.add('on');
    });
    cartEl.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeCart() {
    if (!scrim || !cartEl) { return; }
    scrim.classList.remove('on');
    cartEl.classList.remove('on');
    cartEl.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    setTimeout(function () { scrim.hidden = true; }, 300);
  }

  on($('#cartbtn'), 'click', openCart);
  on($('#cartx'), 'click', closeCart);
  on(scrim, 'click', closeCart);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && cartEl && cartEl.classList.contains('on')) { closeCart(); }
  });

  /* quantity + remove, delegated so re-rendered rows keep working */
  on(bodyEl, 'click', function (e) {
    var row = e.target.closest('.ci');
    if (!row) { return; }
    var slug = row.getAttribute('data-slug');
    var item = cart.filter(function (i) { return i.slug === slug; })[0];
    if (!item) { return; }

    if (e.target.hasAttribute('data-remove')) {
      cart = cart.filter(function (i) { return i.slug !== slug; });
    } else if (e.target.hasAttribute('data-step')) {
      item.qty += parseInt(e.target.getAttribute('data-step'), 10);
      if (item.qty < 1) {
        cart = cart.filter(function (i) { return i.slug !== slug; });
      }
    } else {
      return;
    }
    save();
    render();
  });

  /* add to cart. A button may carry data-qty pointing at a stepper, which is
     how the landing page adds 3 of something in one click. */
  $$('[data-add]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var slug = btn.getAttribute('data-add');
      var stepper = btn.getAttribute('data-qty');
      var add = 1;
      if (stepper) {
        var el = document.getElementById(stepper);
        var read = el && parseInt(el.querySelector('b').textContent, 10);
        if (read > 0) { add = read; }
      }

      var found = cart.filter(function (i) { return i.slug === slug; })[0];
      if (found) {
        found.qty += add;
      } else {
        cart.push({
          slug: slug,
          name: btn.getAttribute('data-name'),
          price: parseFloat(btn.getAttribute('data-price')),
          qty: add
        });
      }
      save();
      render();

      /* Buy It Now is the same add, followed immediately by checkout. On
         Shopify this button posts the line item straight to /checkout and
         skips the cart entirely; here there is no payment provider, so it
         opens the cart and says so rather than pretending to charge anyone. */
      if (btn.hasAttribute('data-buynow')) {
        openCart();
        toast('Demo store - checkout is not connected yet');
        return;
      }

      var label = btn.innerHTML;
      btn.textContent = 'Added';
      btn.classList.add('done');
      setTimeout(function () {
        btn.innerHTML = label;
        btn.classList.remove('done');
      }, 1100);

      toast(btn.getAttribute('data-name') + (add > 1 ? ' x' + add : '') + ' added to cart');
    });
  });

  on($('#checkout'), 'click', function () {
    if (!cart.length) { toast('Your cart is empty'); return; }
    toast('Demo store - checkout is not connected yet');
  });

  render();

  /* ---------------------------------------------------------
     Toast
     --------------------------------------------------------- */
  var toastEl = $('#toast');
  var toastTimer = null;
  function toast(msg) {
    if (!toastEl) { return; }
    toastEl.textContent = msg;
    toastEl.classList.add('on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('on'); }, 2400);
  }

  /* ---------------------------------------------------------
     Email capture
     --------------------------------------------------------- */
  var form = $('#capform');
  on(form, 'submit', function (e) {
    e.preventDefault();
    var input = $('#capmail');
    var msg = $('#capmsg');
    var v = input.value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) {
      msg.textContent = 'That email address does not look right.';
      msg.classList.add('err');
      return;
    }
    msg.classList.remove('err');
    msg.textContent = 'Done. Your code is HOLLOW10 - use it at checkout.';
    input.value = '';
  });

  /* ---------------------------------------------------------
     Product landing page: gallery, quantity, sticky buy bar.
     All three no-op on the homepage.
     --------------------------------------------------------- */
  var pdpImg = $('#pdpimg');
  $$('.pdp__thumb').forEach(function (t) {
    t.addEventListener('click', function () {
      if (!pdpImg) { return; }
      pdpImg.src = t.getAttribute('data-view');
      $$('.pdp__thumb').forEach(function (o) { o.classList.remove('on'); });
      t.classList.add('on');
    });
  });

  /* ---------------------------------------------------------
     Grid cards: show the product's SECOND photo on hover.

     The second src is only fetched the first time a pointer actually enters
     the card, so the homepage still loads 52 photographs, not 104. A phone
     never fires pointerenter without a tap, and a tap follows the link, so
     mobile pays nothing for this - which is the point, the brief asks for the
     site to be fast on a phone.

     Guarded on hover:hover so a stylus or a hybrid laptop doesn't get a photo
     swapped under a finger that was about to tap it.
     --------------------------------------------------------- */
  var canHover = window.matchMedia && window.matchMedia('(hover:hover)').matches;
  if (canHover) {
    $$('.card__media img[data-alt]').forEach(function (img) {
      var card = img.closest('.card__media') || img.parentNode;
      var first = img.getAttribute('src');
      var alt = img.getAttribute('data-alt');
      var pre = null;
      card.addEventListener('pointerenter', function () {
        if (!pre) { pre = new Image(); pre.src = alt; }
        img.src = alt;
      });
      card.addEventListener('pointerleave', function () { img.src = first; });
    });
  }

  var qtyBox = $('#qty');
  var qtyN = $('#qtyn');
  on(qtyBox, 'click', function (e) {
    var step = e.target.getAttribute && e.target.getAttribute('data-q');
    if (!step) { return; }
    var v = parseInt(qtyN.textContent, 10) + parseInt(step, 10);
    /* clamped, so a fast clicker can't reach 0 or -3 and add nothing */
    qtyN.textContent = String(Math.min(20, Math.max(1, v)));
  });

  /* The bar appears once the real buy button has scrolled past, and hides
     again when it comes back - two of them on screen at once is clutter. */
  var stick = $('#stick');
  /* The lowest of the two buy buttons, not the first. Buy It Now sits UNDER
     Add to Cart, so keying off .pdp__act alone made the sticky bar appear
     while the real Buy It Now button was still on screen. */
  var buyBtn = $('.btn--buynow') || $('.pdp__act .btn--add');
  function stickBar() {
    if (!stick || !buyBtn) { return; }
    var past = buyBtn.getBoundingClientRect().bottom < 0;
    stick.classList.toggle('on', past);
    stick.setAttribute('aria-hidden', String(!past));
  }
  stickBar();

  /* ---------------------------------------------------------
     Category jump bar: highlight whichever section you are in.

     Scroll position, not click. Clicking a chip and marking it active is
     easy and wrong - it goes stale the moment you scroll away, and it says
     nothing at all if you arrive by scrolling rather than by tapping.
     --------------------------------------------------------- */
  /* A category chip or tile whose section is not on the page is a link to
     nowhere. It cannot happen here today - the build emits a section for every
     non-empty category and hides the tile otherwise - but the same rule runs on
     the Shopify side where the jump bar and the category rows are configured
     separately, so it is enforced in both. */
  $$('a[href^="#"]').forEach(function (a) {
    var id = a.getAttribute('href').slice(1);
    if (id && !document.getElementById(id) &&
        (a.classList.contains('chip') || a.classList.contains('cat'))) {
      a.hidden = true;
    }
  });

  var chipBar = $('#chips');
  if (chipBar) {
    var chips = $$('.chip', chipBar).filter(function (ch) { return !ch.hidden; });
    var sections = chips.map(function (ch) {
      var id = (ch.getAttribute('href') || '').split('#')[1];
      return id ? document.getElementById(id) : null;
    });
    var spy = function () {
      /* the line just under the header and the chip bar - the first pixel of
         content the reader can actually see */
      var line = chipBar.getBoundingClientRect().bottom + 8;
      var best = -1;
      sections.forEach(function (sec, i) {
        if (!sec) { return; }
        var r = sec.getBoundingClientRect();
        if (r.top <= line && r.bottom > line) { best = i; }
      });
      chips.forEach(function (ch, i) { ch.classList.toggle('on', i === best); });
    };
    spy();
    window.addEventListener('scroll', spy, { passive: true });
    window.addEventListener('resize', spy);
  }

  /* ---------------------------------------------------------
     Reveal on scroll
     --------------------------------------------------------- */
  var targets = $$('.cat, .card, .rev, .trust__i, .why__txt, .why__art, .faq__item, .feat');
  targets.forEach(function (el) { el.classList.add('rv'); });

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add('in');
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    targets.forEach(function (el) { io.observe(el); });
  } else {
    targets.forEach(function (el) { el.classList.add('in'); });
  }
})();
