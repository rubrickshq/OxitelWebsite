/* Oxitel — site.js. Vanilla, no dependencies. Everything degrades without JS. */
(function () {
  'use strict';

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* ---------- Header: shadow once the page scrolls ---------- */
  var header = $('#site-header');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---------- Services dropdown (hover + click + keyboard) ---------- */
  $$('[data-menu-toggle]').forEach(function (btn) {
    var li = btn.parentNode;
    var menu = $('[data-menu]', li);
    if (!menu) return;
    var hoverTimer;
    var open = function () { btn.setAttribute('aria-expanded', 'true'); menu.classList.add('is-open'); };
    var close = function () { btn.setAttribute('aria-expanded', 'false'); menu.classList.remove('is-open'); };
    var isOpen = function () { return btn.getAttribute('aria-expanded') === 'true'; };

    btn.addEventListener('click', function () { isOpen() ? close() : open(); });
    li.addEventListener('mouseenter', function () { clearTimeout(hoverTimer); open(); });
    li.addEventListener('mouseleave', function () { hoverTimer = setTimeout(close, 120); });
    li.addEventListener('focusout', function (e) { if (!li.contains(e.relatedTarget)) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && isOpen()) { close(); btn.focus(); } });
    document.addEventListener('click', function (e) { if (!li.contains(e.target)) close(); });
  });

  /* ---------- Mobile panel ---------- */
  var navToggle = $('[data-nav-toggle]');
  var navPanel = $('[data-nav-panel]');
  if (navToggle && navPanel) {
    var setPanel = function (openState) {
      navToggle.setAttribute('aria-expanded', openState ? 'true' : 'false');
      navToggle.setAttribute('aria-label', openState ? 'Close menu' : 'Open menu');
      navPanel.classList.toggle('is-open', openState);
      document.body.classList.toggle('no-scroll', openState);
    };
    navToggle.addEventListener('click', function () {
      setPanel(navToggle.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && navToggle.getAttribute('aria-expanded') === 'true') { setPanel(false); navToggle.focus(); }
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 960 && navToggle.getAttribute('aria-expanded') === 'true') setPanel(false);
    });
  }

  /* ---------- FAQ accordion ---------- */
  $$('[data-faq]').forEach(function (faq) {
    $$('.faq-q', faq).forEach(function (q) {
      q.addEventListener('click', function () {
        var item = q.closest('.faq-item');
        var expanded = q.getAttribute('aria-expanded') === 'true';
        q.setAttribute('aria-expanded', expanded ? 'false' : 'true');
        item.classList.toggle('is-open', !expanded);
      });
    });
  });

  /* ---------- Coverage: region filter ---------- */
  var filters = $('[data-filters]');
  var routeTable = $('[data-route-table]');
  if (filters && routeTable) {
    var rows = $$('tbody tr', routeTable);
    var empty = $('[data-table-empty]');
    var apply = function (key) {
      var shown = 0;
      rows.forEach(function (row) {
        var show = key === 'all' || row.getAttribute('data-region') === key;
        row.hidden = !show;
        if (show) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    };
    $$('.filter', filters).forEach(function (b) {
      b.addEventListener('click', function () {
        $$('.filter', filters).forEach(function (o) { o.setAttribute('aria-pressed', 'false'); });
        b.setAttribute('aria-pressed', 'true');
        apply(b.getAttribute('data-filter'));
      });
    });
    var initial = new URLSearchParams(location.search).get('region');
    if (initial) {
      var match = $('.filter[data-filter="' + initial + '"]', filters);
      if (match) match.click();
    }
  }

  /* ---------- Contact form ---------- */
  var form = $('[data-contact-form]');
  if (form) {
    var status = $('[data-form-status]', form);
    var submitBtn = $('[data-submit]', form);
    var params = new URLSearchParams(location.search);

    // Prefill interest from ?interest=
    var interest = params.get('interest');
    var select = $('#f-interest', form);
    if (interest && select && select.querySelector('option[value="' + interest + '"]')) {
      select.value = interest;
    }
    // Non-JS fallback returns here with ?sent=1
    if (params.get('sent') === '1' && status) {
      showStatus('success', "Thanks — we've got your message. A member of our team will reply within 24 business hours.");
      form.scrollIntoView({ block: 'start' });
    }

    function showStatus(kind, msg) {
      status.className = 'form-status is-' + kind;
      status.textContent = msg;
    }

    function fieldOf(input) { return input.closest('.field'); }
    function validate(input) {
      var f = fieldOf(input);
      var ok = input.checkValidity() && input.value.trim() !== '';
      if (input.type === 'email') ok = ok && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(input.value.trim());
      f.classList.toggle('is-error', !ok);
      var err = $('.error', f);
      if (err) input.setAttribute('aria-describedby', ok ? '' : err.id);
      input.setAttribute('aria-invalid', ok ? 'false' : 'true');
      return ok;
    }

    var inputs = $$('.input, .select, .textarea', form);
    inputs.forEach(function (i) {
      i.addEventListener('blur', function () { if (i.value !== '') validate(i); });
      i.addEventListener('input', function () { if (fieldOf(i).classList.contains('is-error')) validate(i); });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var allOk = true, first = null;
      inputs.forEach(function (i) { if (!validate(i)) { allOk = false; if (!first) first = i; } });
      if (!allOk) { first.focus(); showStatus('error', 'Check the highlighted fields and try again.'); return; }
      if (form.elements._honey && form.elements._honey.value) { return; } // bot

      var endpoint = form.getAttribute('data-endpoint');
      var data = {};
      new FormData(form).forEach(function (v, k) { if (k !== '_honey') data[k] = v; });

      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending…';
      status.className = 'form-status';

      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data)
      }).then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      }).then(function () {
        showStatus('success', "Thanks — we've got your message. A member of our team will reply within 24 business hours. Need something urgent on a live route? Email " + (form.getAttribute('data-noc') || 'the NOC') + '.');
        form.reset();
        submitBtn.textContent = 'Sent';
      }).catch(function () {
        showStatus('error', "Something went wrong and your message didn't send. Please try again, or email us directly at " + (form.getAttribute('data-sales') || 'sales@oxitel.net') + '.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send message';
      });
    });
  }
})();
