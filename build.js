// Oxitel static site builder — zero dependencies.
// Usage: node build.js   →  writes ./dist
const fs = require("fs");
const crypto = require("crypto");
const path = require("path");

const SITE_URL = process.env.SITE_URL || "https://oxitel.net";
const SRC = path.join(__dirname, "src");
const DIST = path.join(__dirname, "dist");

const read = (p) => fs.readFileSync(p, "utf8");
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const layout = read(path.join(SRC, "partials", "layout.html"));
const navTpl = read(path.join(SRC, "partials", "nav.html"));
const footerTpl = read(path.join(SRC, "partials", "footer.html"));
const hash = (p) => crypto.createHash("md5").update(fs.readFileSync(p)).digest("hex").slice(0, 8);
const CSS_V = hash(path.join(SRC, "assets", "css", "styles.css"));
const JS_V = hash(path.join(SRC, "assets", "js", "main.js"));

function parsePage(file) {
  const raw = read(file);
  const m = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!m) throw new Error("Missing front matter in " + file);
  const meta = {};
  m[1].split("\n").forEach((line) => {
    const i = line.indexOf(":");
    if (i > 0) meta[line.slice(0, i).trim()] = line.slice(i + 1).trim();
  });
  return { meta, content: m[2] };
}

function activeNav(route) {
  // Mark the nav item that owns this route with aria-current.
  return navTpl.replace(/data-nav="([^"]+)"/g, (all, navRoute) => {
    const isActive =
      navRoute === "/" ? route === "/" : route === navRoute || route.startsWith(navRoute + "/") || route === navRoute + "/";
    return isActive ? `data-nav="${navRoute}" aria-current="page"` : all;
  });
}

function render(page) {
  const { meta, content } = page;
  const route = meta.route;
  const canonical = SITE_URL + route;
  let html = layout
    .replace(/\{\{title\}\}/g, esc(meta.title))
    .replace(/\{\{description\}\}/g, esc(meta.description))
    .replace(/\{\{canonical\}\}/g, canonical)
    .replace(/\{\{route\}\}/g, route)
    .replace(/\{\{bodyclass\}\}/g, meta.bodyclass || "")
    .replace(/\{\{robots\}\}/g, meta.noindex === "true" ? "noindex, nofollow" : "index, follow")
    .replace(/\{\{jsonld\}\}/g, meta.jsonld === "organization" ? organizationJsonLd() : "")
    .replace("{{nav}}", activeNav(route))
    .replace("{{footer}}", footerTpl)
    .replace("{{content}}", content)
    .replace("/assets/css/styles.css", "/assets/css/styles.css?v=" + CSS_V)
    .replace("/assets/js/main.js", "/assets/js/main.js?v=" + JS_V);
  return html;
}

function organizationJsonLd() {
  const data = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "Oxitel",
    url: SITE_URL,
    logo: SITE_URL + "/assets/img/logo-mark.svg",
    description:
      "Oxitel is a wholesale voice carrier delivering A-Z termination, Premium CLI routes and virtual numbers to carriers, VoIP providers and call centres.",
    contactPoint: [{ "@type": "ContactPoint", contactType: "sales", email: "sales@oxitel.net", availableLanguage: "English" }],
  };
  return `<script type="application/ld+json">${JSON.stringify(data)}</script>`;
}

function copyDir(from, to) {
  fs.mkdirSync(to, { recursive: true });
  for (const entry of fs.readdirSync(from, { withFileTypes: true })) {
    const s = path.join(from, entry.name);
    const d = path.join(to, entry.name);
    entry.isDirectory() ? copyDir(s, d) : fs.copyFileSync(s, d);
  }
}

function build() {
  fs.rmSync(DIST, { recursive: true, force: true });
  fs.mkdirSync(DIST, { recursive: true });

  const pagesDir = path.join(SRC, "pages");
  const files = fs.readdirSync(pagesDir).filter((f) => f.endsWith(".html")).sort();
  const routes = [];

  for (const f of files) {
    const page = parsePage(path.join(pagesDir, f));
    const route = page.meta.route;
    const html = render(page);
    let out;
    if (route === "/404") out = path.join(DIST, "404.html");
    else if (route === "/") out = path.join(DIST, "index.html");
    else out = path.join(DIST, route.replace(/^\//, ""), "index.html");
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, html);
    if (route !== "/404" && page.meta.noindex !== "true") routes.push(route);
    console.log("✓", route.padEnd(28), path.relative(DIST, out));
  }

  copyDir(path.join(SRC, "assets"), path.join(DIST, "assets"));

  const today = new Date().toISOString().slice(0, 10);
  const sitemap =
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
    routes.map((r) => `  <url><loc>${SITE_URL}${r === "/" ? "/" : r + "/"}</loc><lastmod>${today}</lastmod></url>`).join("\n") +
    `\n</urlset>\n`;
  fs.writeFileSync(path.join(DIST, "sitemap.xml"), sitemap);
  fs.writeFileSync(path.join(DIST, "robots.txt"), `User-agent: *\nAllow: /\nSitemap: ${SITE_URL}/sitemap.xml\n`);
  console.log(`\nBuilt ${routes.length} pages → dist/`);
}

build();
