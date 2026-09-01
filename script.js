/* =========================================================
   Hollow & Hex - storefront behaviour
   Cart state lives in localStorage so it survives a refresh.
   ========================================================= */
(function () {
  'use strict';

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var money = function (n) { return '$' + n.toFixed(2); };

  /* ---------------------------------------------------------
     Header: solid background once you leave the very top
     --------------------------------------------------------- */
  var hdr = $('#hdr');
  var onScroll = function () {
    hdr.classList.toggle('hdr--solid', window.scrollY > 24);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---------------------------------------------------------
     Mobile menu
     --------------------------------------------------------- */
  var burger = $('#burger');
  var nav = $('#nav');
  burger.addEventListener('click', function () {
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
    cd.d.textContent = pad(d);
    cd.h.textContent = pad(h);
    cd.m.textContent = pad(m);
    cd.s.textContent = pad(sec);
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
    var n = count();
    nEl.textContent = String(n);
    nEl.classList.toggle('on', n > 0);

    if (!cart.length) {
      bodyEl.innerHTML = '<p class="cart__empty">Your cart is empty.<br />The neighbours are winning.</p>';
      totEl.textContent = '$0.00';
      return;
    }

    bodyEl.innerHTML = cart.map(function (i) {
      return '<div class="ci" data-slug="' + i.slug + '">' +
        '<img src="assets/products/' + i.slug + '.svg" alt="" />' +
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
    scrim.hidden = false;
    requestAnimationFrame(function () {
      scrim.classList.add('on');
      cartEl.classList.add('on');
    });
    cartEl.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeCart() {
    scrim.classList.remove('on');
    cartEl.classList.remove('on');
    cartEl.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    setTimeout(function () { scrim.hidden = true; }, 300);
  }

  $('#cartbtn').addEventListener('click', openCart);
  $('#cartx').addEventListener('click', closeCart);
  scrim.addEventListener('click', closeCart);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && cartEl.classList.contains('on')) { closeCart(); }
  });

  /* quantity + remove, delegated so re-rendered rows keep working */
  bodyEl.addEventListener('click', function (e) {
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

  /* add to cart */
  $$('[data-add]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var slug = btn.getAttribute('data-add');
      var found = cart.filter(function (i) { return i.slug === slug; })[0];
      if (found) {
        found.qty += 1;
      } else {
        cart.push({
          slug: slug,
          name: btn.getAttribute('data-name'),
          price: parseFloat(btn.getAttribute('data-price')),
          qty: 1
        });
      }
      save();
      render();

      var label = btn.textContent;
      btn.textContent = 'Added';
      btn.classList.add('done');
      setTimeout(function () {
        btn.textContent = label;
        btn.classList.remove('done');
      }, 1100);

      toast(btn.getAttribute('data-name') + ' added to cart');
    });
  });

  $('#checkout').addEventListener('click', function () {
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
    toastEl.textContent = msg;
    toastEl.classList.add('on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('on'); }, 2400);
  }

  /* ---------------------------------------------------------
     Email capture
     --------------------------------------------------------- */
  var form = $('#capform');
  form.addEventListener('submit', function (e) {
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
     Reveal on scroll
     --------------------------------------------------------- */
  var targets = $$('.cat, .card, .rev, .trust__i, .why__txt, .why__art, .faq__item');
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
