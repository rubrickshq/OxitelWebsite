/* Oxitel — main.js (no dependencies) */
(function () {
  "use strict";
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  /* ---------- Nav ---------- */
  const nav = $("#nav");
  const toggle = $("#navToggle");
  const onScroll = () => nav.classList.toggle("is-scrolled", window.scrollY > 40);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  if (toggle) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      document.body.style.overflow = open ? "hidden" : "";
    });
    $$(".nav__panel a").forEach((a) => a.addEventListener("click", () => {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      document.body.style.overflow = "";
    }));
  }
  $$(".sub__toggle").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const li = btn.closest(".has-sub");
      const open = li.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", String(open));
    });
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    $$(".has-sub.is-open").forEach((li) => { li.classList.remove("is-open"); $(".sub__toggle", li).setAttribute("aria-expanded", "false"); });
    if (nav.classList.contains("is-open")) toggle.click();
  });
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".has-sub")) $$(".has-sub.is-open").forEach((li) => { li.classList.remove("is-open"); $(".sub__toggle", li).setAttribute("aria-expanded", "false"); });
  });

  /* ---------- Page-load sequence ---------- */
  const start = () => {
    document.body.classList.add("is-loaded");
    $$(".hero .route").forEach((r) => setTimeout(() => r.classList.add("is-on"), reduceMotion ? 0 : 650));
  };
  if (document.fonts && document.fonts.ready) {
    Promise.race([document.fonts.ready, new Promise((res) => setTimeout(res, 600))]).then(start);
  } else start();

  /* ---------- Reveal on scroll (route motifs, steps, tables) ---------- */
  const revealables = $$("[data-reveal]");
  if ("IntersectionObserver" in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add("is-on"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0.2 });
    revealables.forEach((el) => io.observe(el));
  } else revealables.forEach((el) => el.classList.add("is-on"));

  /* ---------- FAQ ---------- */
  $$(".faq__item").forEach((item) => {
    const btn = $(".faq__q", item);
    btn.addEventListener("click", () => {
      const open = item.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", String(open));
    });
  });

  /* ---------- Coverage filters ---------- */
  const filters = $(".filters");
  if (filters) {
    const rows = $$(".rt tbody tr");
    const count = $(".filters__count");
    const apply = (key) => {
      let n = 0;
      rows.forEach((tr) => {
        const show = key === "all" || tr.dataset.region === key || (key === "direct" && tr.dataset.route === "direct");
        tr.hidden = !show; if (show) n++;
      });
      if (count) count.textContent = n + (n === 1 ? " destination" : " destinations") + (key === "all" ? " listed — the A-Z sheet covers many more." : " shown.");
    };
    $$("button", filters).forEach((b) => b.addEventListener("click", () => {
      $$("button", filters).forEach((x) => x.setAttribute("aria-pressed", "false"));
      b.setAttribute("aria-pressed", "true");
      apply(b.dataset.filter);
    }));
    apply("all");
  }

  /* ---------- Contact form ---------- */
  const form = $("#contactForm");
  if (form) {
    const status = $("#formStatus");
    const submit = $("button[type=submit]", form);
    const setInvalid = (name, msg) => {
      const field = form.elements[name].closest(".field");
      field.classList.toggle("is-invalid", !!msg);
      const hint = $(".hint", field);
      if (hint) hint.textContent = msg || hint.dataset.default || "";
    };
    const validate = () => {
      let ok = true;
      const v = (n) => form.elements[n].value.trim();
      if (!v("name")) { setInvalid("name", "Enter your name."); ok = false; } else setInvalid("name", "");
      if (!v("company")) { setInvalid("company", "Enter your company name."); ok = false; } else setInvalid("company", "");
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v("email"))) { setInvalid("email", "Enter a valid email address, like you@company.com."); ok = false; } else setInvalid("email", "");
      if (!v("message")) { setInvalid("message", "Tell us about your traffic — destinations, volume, CLI or NCLI."); ok = false; } else setInvalid("message", "");
      return ok;
    };
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      status.className = "form__status";
      if (!validate()) { $(".is-invalid input, .is-invalid textarea", form)?.focus(); return; }
      const data = Object.fromEntries(new FormData(form).entries());
      submit.classList.add("is-sending"); submit.disabled = true;
      try {
        const res = await fetch(form.action, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(data) });
        const json = await res.json().catch(() => ({}));
        if (res.ok && json.ok) {
          status.className = "form__status is-ok";
          status.textContent = "Thanks — we've got your message. A member of our team will reply within 24 business hours.";
          form.reset();
        } else if (json.error === "not_configured") {
          status.className = "form__status is-err";
          status.innerHTML = "The form isn't connected to our inbox yet. Please email us directly at <a href=\"mailto:sales@oxitel.net\">sales@oxitel.net</a> — we reply within 24 business hours.";
        } else {
          status.className = "form__status is-err";
          status.innerHTML = "Something went wrong and your message didn't send. Please try again or email <a href=\"mailto:sales@oxitel.net\">sales@oxitel.net</a>.";
        }
      } catch (err) {
        status.className = "form__status is-err";
        status.innerHTML = "We couldn't reach the server. Please try again or email <a href=\"mailto:sales@oxitel.net\">sales@oxitel.net</a>.";
      } finally {
        submit.classList.remove("is-sending"); submit.disabled = false;
        status.scrollIntoView({ block: "nearest", behavior: reduceMotion ? "auto" : "smooth" });
      }
    });
    ["name", "company", "email", "message"].forEach((n) => form.elements[n].addEventListener("input", () => setInvalid(n, "")));
  }

  /* ---------- Footer year ---------- */
  const y = $("#year"); if (y) y.textContent = String(new Date().getFullYear());
})();
