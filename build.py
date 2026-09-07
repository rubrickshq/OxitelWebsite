#!/usr/bin/env python3
"""Build the Oxitel static site into ./dist"""
import os, shutil, json, datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
STATIC = ROOT / "static"
VERSION = datetime.date.today().strftime("%Y%m%d") + "a"

SITE = {
    "url": "https://oxitel.net",
    "version": VERSION,
    "sales_email": "sales@oxitel.net",
    "noc_email": "noc@oxitel.net",
    "phone": "+91 124 567 8900",
    "phone_tel": "+911245678900",
    "address": "4th Floor, Tower B, DLF Cyber City, Gurugram 122002, India",
    "address_short": "Gurugram, India",
    "tz": "IST",
    "founded": "2026",
    "linkedin": "https://www.linkedin.com/company/oxitel",
    # Contact form: FormSubmit (no account needed; first submission triggers an activation email to the address).
    "form_action": "https://formsubmit.co/sales@oxitel.net",
    "form_ajax": "https://formsubmit.co/ajax/sales@oxitel.net",
}

DIRECT_ROUTES = [
    {"country": "Nigeria", "cli": True, "ncli": True, "networks": "Major mobile networks", "detail": "Direct termination to the major mobile networks. CLI and NCLI routes."},
    {"country": "Zambia", "cli": True, "ncli": False, "networks": "Mobile", "detail": "Direct routes with CLI delivery."},
    {"country": "Zimbabwe", "cli": True, "ncli": True, "networks": "Mobile and fixed", "detail": "Direct termination, CLI and NCLI options."},
    {"country": "South Africa", "cli": True, "ncli": True, "networks": "Mobile and fixed", "detail": "Direct routes to mobile and fixed networks."},
    {"country": "Tanzania", "cli": True, "ncli": False, "networks": "Mobile", "detail": "Direct termination with CLI delivery."},
]

REGIONS = [
    {"key": "africa", "name": "Africa"},
    {"key": "middle-east", "name": "Middle East"},
    {"key": "sea", "name": "South East Asia"},
    {"key": "australia", "name": "Australia"},
    {"key": "latam", "name": "Latin America"},
    {"key": "cis", "name": "CIS"},
    {"key": "europe", "name": "Europe"},
]
REGION_NAME = {r["key"]: r["name"] for r in REGIONS}

PARTNER_ROUTES = [
    ("africa", "Kenya", True, True), ("africa", "Ghana", True, True), ("africa", "Uganda", True, False),
    ("africa", "Cameroon", True, True), ("africa", "Côte d'Ivoire", True, False), ("africa", "Ethiopia", False, True),
    ("middle-east", "United Arab Emirates", True, True), ("middle-east", "Saudi Arabia", True, True),
    ("middle-east", "Qatar", True, False), ("middle-east", "Oman", True, True), ("middle-east", "Jordan", True, True),
    ("sea", "Philippines", True, True), ("sea", "Indonesia", True, True), ("sea", "Vietnam", True, False),
    ("sea", "Malaysia", True, True), ("sea", "Thailand", True, True),
    ("australia", "Australia", True, True), ("australia", "New Zealand", True, True),
    ("latam", "Mexico", True, True), ("latam", "Brazil", True, True), ("latam", "Colombia", True, False),
    ("latam", "Peru", True, True), ("latam", "Argentina", True, True),
    ("cis", "Russia", True, True), ("cis", "Kazakhstan", True, True), ("cis", "Uzbekistan", True, False),
    ("cis", "Georgia", True, True),
    ("europe", "United Kingdom", True, True), ("europe", "Germany", True, True), ("europe", "France", True, True),
    ("europe", "Spain", True, True), ("europe", "Italy", True, True), ("europe", "Turkey", True, True),
]

ALL_ROUTES = [
    {"country": r["country"], "region": "africa", "region_name": "Africa", "direct": True, "cli": r["cli"], "ncli": r["ncli"]}
    for r in DIRECT_ROUTES
] + [
    {"country": c, "region": k, "region_name": REGION_NAME[k], "direct": False, "cli": cli, "ncli": ncli}
    for (k, c, cli, ncli) in PARTNER_ROUTES
]

CONTACT_FAQ = [
    {"q": "Do you offer test routes before we commit?", "a": "Yes. Every new customer gets a test interconnect so you can check quality on real traffic first."},
    {"q": "What is the difference between CLI and NCLI routes?", "a": "CLI routes deliver the caller's number to the called party; NCLI routes don't. CLI is best when callbacks and trust matter. NCLI is cheaper and suits high-volume wholesale traffic."},
    {"q": "Is there a minimum volume?", "a": "No. We work with carriers and providers of every size."},
    {"q": "What are your payment terms?", "a": "Prepaid by default. Postpaid is available once we have an established trading history."},
    {"q": "How quickly can we go live?", "a": "Typically within 24–48 hours of receiving your IP details and signed agreement."},
    {"q": "Which protocol do you support?", "a": "SIP only. We keep the interconnect simple so setup is fast and troubleshooting is easy."},
]

SERVICES = {
    "wholesale-voice": {
        "title": "Wholesale voice termination (A-Z) — Oxitel",
        "description": "A-Z wholesale voice termination for carriers and aggregators. Direct routes into Africa, competitive rates, SIP interconnect, 24/7 NOC. Request rates from Oxitel.",
        "kicker": "Wholesale voice",
        "h1": "Wholesale voice termination, A to Z",
        "lead": "High-volume international termination for carriers, aggregators and wholesale VoIP providers — on direct routes where we have them, and tested partner routes everywhere else.",
        "cta": "Request A-Z rates", "interest": "wholesale",
        "who": "Carriers and MNOs exchanging international traffic. Aggregators consolidating volume across destinations. Wholesale VoIP providers who need reach at a rate that leaves room for margin.",
        "gets": ["A-Z coverage through direct and partner routes", "Competitive wholesale rates, updated weekly", "Direct termination into Nigeria, Zambia, Zimbabwe, South Africa and Tanzania", "CLI and NCLI options by destination", "Capacity for large, sustained volumes", "24/7 NOC monitoring and support"],
        "extras": [
            {"title": "How we route your traffic", "body": "Direct routes first. Where we don't have a direct termination, traffic goes to partner routes we test on an ongoing basis. Quality is tracked per destination — ASR, ACD, PDD — and routing is adjusted when a supplier degrades. You get one rate sheet and one interconnect; we handle what sits behind it.", "dark": False},
        ],
        "commercials": [("Rates", "A-Z rate sheet sent on request, updated weekly"), ("Billing", "Prepaid by default; postpaid available after an established trading history"), ("Minimum volume", "None"), ("Currency", "USD")],
        "technical": [("Protocol", "SIP"), ("Codecs", "G.711 (A-law / µ-law), G.729"), ("Interconnect", "IP-to-IP, IP-whitelisted"), ("Capacity", "Scaled to your forecast; tell us expected concurrent calls"), ("Monitoring", "24/7 NOC, real-time route quality")],
        "faq": [
            {"q": "Do you offer test routes?", "a": "Yes. Every new customer gets a test interconnect before committing."},
            {"q": "How often do rates change?", "a": "We send updates weekly, with notice on any increase."},
            {"q": "Can I send both CLI and NCLI traffic?", "a": "Yes — tell us the split and we'll route each correctly."},
        ],
        "cta_title": "Get our A-Z rate sheet", "cta_body": "Send your destinations and expected volume. Rates back within 24 business hours.", "cta_label": "Request A-Z rates",
    },
    "retail-voice": {
        "title": "Retail voice termination — Oxitel",
        "description": "Quality-first voice termination for VoIP providers, call centres and resellers. Priority routing, consistent ASR and ACD, 24/7 support from Oxitel.",
        "kicker": "Retail voice",
        "h1": "Retail voice for traffic that can't afford a bad call",
        "lead": "Quality-first termination for VoIP providers, call centres and resellers whose customers notice every dropped call, every delay, every wrong caller ID.",
        "cta": "Talk to us about retail routes", "interest": "retail",
        "who": "Retail VoIP providers serving businesses and consumers. Calling-card and softswitch operators. Call centres running outbound campaigns. Resellers who sell on quality, not just price.",
        "gets": ["Priority routing on stable, tested routes", "Consistent ASR and ACD across destinations", "CLI delivery where the destination supports it", "Proactive rerouting when a route degrades", "Dedicated account contact plus 24/7 NOC"],
        "extras": [
            {"title": "Our quality promise", "body": "Retail traffic is monitored more tightly than wholesale. We track ASR, ACD and PDD per destination and reroute the moment a supplier slips — usually before you see it in your own stats. If you do see it first, the NOC is one email away, around the clock.", "dark": True},
        ],
        "commercials": [("Rates", "Quality-tier pricing per destination, sent on request"), ("Billing", "Prepaid or postpaid"), ("Minimum volume", "None"), ("Currency", "USD")],
        "technical": [("Protocol", "SIP"), ("Codecs", "G.711 (A-law / µ-law), G.729"), ("Interconnect", "IP-to-IP, IP-whitelisted"), ("Monitoring", "24/7 NOC, per-destination ASR / ACD / PDD")],
        "faq": None,
        "cta_title": "Your customers judge you by the call. So do we.", "cta_body": "Tell us your destinations and we'll set up a test route on our retail tier.", "cta_label": "Contact us",
    },
    "premium-cli": {
        "title": "Premium CLI routes — Oxitel",
        "description": "Premium CLI voice routes with guaranteed caller-ID delivery on direct terminations. Built for call centres and callback-dependent traffic. Contact Oxitel.",
        "kicker": "Premium CLI",
        "h1": "Premium CLI routes. Caller ID delivered, every time.",
        "lead": "Direct routes where the caller's number reaches the called party exactly as sent — so your customers can call back, and your calls get answered.",
        "cta": "Ask about CLI destinations", "interest": "cli",
        "who": "Outbound call centres and telemarketing. Business calling where callbacks matter. Customer service and collections. Any traffic where a visible, correct caller ID is a requirement.",
        "gets": ["Guaranteed CLI delivery on direct terminations", "Balanced cost and quality on our core African destinations", "Highest routing priority in our network", "Consistent ASR and ACD", "24/7 NOC monitoring"],
        "extras": [
            {"title": "Why CLI matters", "body": "When caller ID is missing or wrong, people don't pick up, and they can't call back. For call centres, that is lost conversions. For businesses, it is lost trust. Premium CLI routes solve this by sending traffic only over direct terminations that preserve the caller ID end to end.", "dark": False},
            {"title": "Destinations", "body": "Premium CLI is available on our direct routes today, with further destinations available on request.", "dark": True, "chips": ["Nigeria", "Zambia", "Zimbabwe", "South Africa", "Tanzania"], "direct": True, "after": "Need CLI into another market? Tell us the destination and expected volume and we'll confirm availability."},
        ],
        "commercials": [("Rates", "Premium tier, per destination, sent on request"), ("Billing", "Prepaid by default; postpaid after an established trading history"), ("Minimum volume", "None")],
        "technical": [("Protocol", "SIP"), ("Codecs", "G.711 (A-law / µ-law), G.729"), ("CLI", "Preserved end to end on direct routes"), ("Monitoring", "24/7 NOC, CLI delivery verified on test traffic")],
        "faq": None,
        "cta_title": "Test a Premium CLI route on your own traffic", "cta_body": "Send a destination and we'll set up a test interconnect so you can verify caller ID delivery yourself.", "cta_label": "Contact us",
    },
    "virtual-numbers": {
        "title": "DID and virtual numbers — Oxitel",
        "description": "Local and international virtual numbers (DIDs) delivered over SIP to your switch or PBX. Multi-country coverage under one account with Oxitel.",
        "kicker": "DID / virtual numbers",
        "h1": "Virtual numbers that give you a local presence",
        "lead": "Inbound numbers in the countries where your customers are, delivered over SIP to your switch or PBX. One account, one interconnect, as many countries as you need.",
        "cta": "Check number availability", "interest": "did",
        "who": "Call centres taking inbound customer calls in multiple countries. Businesses expanding into new markets without a local office. VoIP providers and resellers adding numbers to their own offering.",
        "gets": ["Local and international DIDs", "SIP delivery to your existing switch or PBX", "Multi-country coverage under one account", "Fast provisioning — most numbers live within 24 hours", "Simple monthly pricing per number, plus inbound per minute"],
        "extras": [
            {"title": "Countries available", "body": "Numbers in these countries today, with more on request.", "dark": True, "chips": ["United States", "United Kingdom", "Canada", "Australia", "Germany", "South Africa", "Nigeria", "Kenya"], "direct": False, "after": "Need a country not listed? Ask — we add coverage based on customer demand."},
            {"title": "How it works", "dark": False, "steps": [
                {"t": "Tell us what you need", "d": "Countries, quantities, and where the calls should land."},
                {"t": "We provision", "d": "Numbers are assigned and pointed to your SIP endpoint."},
                {"t": "Calls land on your switch", "d": "Usually within 24 hours. The NOC monitors from there."},
            ]},
        ],
        "commercials": [("Pricing", "Monthly per number, plus inbound per minute"), ("Billing", "Prepaid or postpaid"), ("Minimum", "One number")],
        "technical": [("Delivery", "SIP to your switch or PBX"), ("Codecs", "G.711 (A-law / µ-law), G.729"), ("Provisioning", "Most numbers live within 24 hours")],
        "faq": None,
        "cta_title": "Need numbers in a country not listed? Ask.", "cta_body": "Tell us the countries and quantities and we'll confirm availability and pricing.", "cta_label": "Check availability",
    },
}

PRIVACY_HTML = """
<p class="updated">Last updated 7 September 2026</p>
<h2>Who we are</h2>
<p>Oxitel ("we", "us") is a wholesale voice carrier. This policy explains what personal data we collect through oxitel.net, why we collect it, and the choices you have. Questions go to <a href="mailto:sales@oxitel.net">sales@oxitel.net</a>.</p>
<h2>What we collect</h2>
<ul>
<li><strong>Contact form.</strong> Your name, company, work email, country, area of interest and message — only when you send them to us.</li>
<li><strong>Email.</strong> Anything you include when you email us, and the technical headers that come with it.</li>
<li><strong>Website usage.</strong> Standard server logs (IP address, browser type, pages requested, time of request). We do not run advertising trackers.</li>
</ul>
<h2>Why we collect it</h2>
<p>To reply to your enquiry, prepare rates and agreements, set up and support an interconnect, and keep the website secure. We don't sell personal data and we don't use it for advertising.</p>
<h2>How long we keep it</h2>
<p>Enquiries are kept for as long as we are in a business conversation with you and for up to 24 months afterwards, unless a contract or a legal obligation requires longer. Server logs are kept for 90 days.</p>
<h2>Who we share it with</h2>
<p>Service providers that help us run the website and handle email (hosting and form-delivery providers), under agreements that restrict how they use the data. We may also disclose data where the law requires it.</p>
<h2>Your rights</h2>
<p>You can ask us to access, correct or delete the personal data we hold about you, or to stop processing it. Email <a href="mailto:sales@oxitel.net">sales@oxitel.net</a> and we will respond within 30 days.</p>
<h2>Cookies</h2>
<p>oxitel.net does not set cookies for tracking or advertising. Any cookies used are strictly necessary for the site to function.</p>
<h2>Changes</h2>
<p>If we change this policy, we will update the date at the top of this page.</p>
"""

TERMS_HTML = """
<p class="updated">Last updated 7 September 2026</p>
<h2>Scope</h2>
<p>These terms cover your use of oxitel.net and the way we take enquiries. Commercial terms for voice termination, numbers or partnership are set out in the agreement we sign with you, which takes precedence over anything here.</p>
<h2>Services</h2>
<p>Oxitel provides wholesale and retail voice termination, Premium CLI routes and DID / virtual numbers to carriers, VoIP providers, call centres and resellers. Availability, quality and pricing vary by destination and are confirmed in writing before traffic goes live.</p>
<h2>Accounts and billing</h2>
<p>Services are prepaid by default. Postpaid terms may be offered after an established trading history. Rates can change with notice as set out in your agreement.</p>
<h2>Acceptable use</h2>
<p>You may not send fraudulent, illegal, spoofed or abusive traffic over our network, including traffic that violates the laws of the originating or terminating country. We may suspend traffic immediately where we reasonably suspect fraud or abuse.</p>
<h2>Service levels and support</h2>
<p>Our NOC is available 24/7. Specific service levels, if any, are those set out in your agreement. We do not guarantee uninterrupted service on partner routes.</p>
<h2>Liability</h2>
<p>To the extent permitted by law, we are not liable for indirect or consequential loss arising from the use of this website or our services. Our total liability under an agreement is limited as stated in that agreement.</p>
<h2>Termination</h2>
<p>Either party may end an agreement as set out in it. We may suspend or terminate services immediately for breach of acceptable use or non-payment.</p>
<h2>Governing law</h2>
<p>These terms are governed by the laws of India. Disputes are subject to the exclusive jurisdiction of the courts of Gurugram, Haryana, unless your agreement with us says otherwise.</p>
<h2>Contact</h2>
<p><a href="mailto:sales@oxitel.net">sales@oxitel.net</a></p>
"""

PAGES = [
    {"path": "/", "template": "index.html", "nav": "home", "title": "Oxitel — Wholesale voice, CLI routes and DID numbers",
     "description": "Wholesale voice carrier with direct routes into Africa: A-Z termination, Premium CLI routes and virtual numbers over SIP, backed by a 24/7 NOC. Contact us for rates."},
    {"path": "/about/", "template": "about.html", "nav": "about", "title": "About Oxitel — a voice carrier built on direct routes",
     "description": "Oxitel is a new wholesale voice carrier founded by experienced telecom professionals, with direct termination in Africa and interconnects worldwide.",
     "cta_title": "Let's talk routes.", "cta_body": "Send your destinations and volumes. We reply with rates within 24 business hours."},
    {"path": "/services/", "template": "services.html", "nav": "services", "title": "Voice termination services — Oxitel",
     "description": "Wholesale voice, retail voice, Premium CLI routes and DID numbers from a single SIP interconnect. Explore Oxitel's carrier services.",
     "cta_title": "Not sure which one you need?", "cta_body": "Tell us about your traffic and we'll recommend the right setup — and send rates for it."},
    {"path": "/coverage/", "template": "coverage.html", "nav": "coverage", "title": "Coverage and network — Oxitel",
     "description": "Direct voice termination in Nigeria, Zambia, Zimbabwe, South Africa and Tanzania, plus interconnects across the Middle East, Asia, Australia, LATAM, CIS and Europe.",
     "cta_title": "Don't see your destination?", "cta_body": "Our A-Z sheet is broader than this page. Ask and we'll send it.", "cta_label": "Request the A-Z sheet", "cta_query": "interest=wholesale"},
    {"path": "/partners/", "template": "partners.html", "nav": "partners", "title": "Partner with Oxitel — carriers and resellers",
     "description": "Interconnect with Oxitel to exchange traffic, or resell our routes to your own customers. Direct African terminations, fair terms, 24/7 NOC.",
     "cta_title": "Let's build the route together.", "cta_body": "Tell us who you are and what traffic you send or receive.", "cta_label": "Become a partner", "cta_query": "interest=partnership"},
    {"path": "/contact/", "template": "contact.html", "nav": "contact", "title": "Contact Oxitel — request rates",
     "description": "Contact Oxitel for wholesale voice rates, Premium CLI routes, DIDs or partnership. Sales replies within 24 business hours; NOC available 24/7.", "cta": False},
    {"path": "/privacy/", "template": "legal.html", "nav": "legal", "title": "Privacy policy — Oxitel", "h1": "Privacy policy",
     "lead": "What we collect through this website, why, and the choices you have.", "description": "How Oxitel collects and uses personal data through oxitel.net.", "body": PRIVACY_HTML, "cta": False},
    {"path": "/terms/", "template": "legal.html", "nav": "legal", "title": "Terms of service — Oxitel", "h1": "Terms of service",
     "lead": "The terms that apply to this website and to enquiries. Your signed agreement governs commercial terms.", "description": "Terms of service for oxitel.net and Oxitel's enquiry process.", "body": TERMS_HTML, "cta": False},
    {"path": "/404.html", "template": "404.html", "nav": "", "title": "Page not found — Oxitel", "description": "The page you're looking for has moved or never existed. Head back to the Oxitel home page or contact us.", "cta": False, "noindex": True},
]
for slug, svc in SERVICES.items():
    PAGES.append({"path": f"/services/{slug}/", "template": "service.html", "nav": "services", "title": svc["title"],
                  "description": svc["description"], "svc": svc,
                  "cta_title": svc["cta_title"], "cta_body": svc["cta_body"], "cta_label": svc["cta_label"], "cta_query": f"interest={svc['interest']}"})


def render():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")), autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    for page in PAGES:
        tpl = env.get_template(page["template"])
        html = tpl.render(site=SITE, page=page, svc=page.get("svc"), body=page.get("body", ""),
                          direct_routes=DIRECT_ROUTES, all_routes=ALL_ROUTES, regions=REGIONS, faq=CONTACT_FAQ)
        if page["path"].endswith(".html"):
            out = DIST / page["path"].lstrip("/")
        else:
            out = DIST / page["path"].lstrip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print("wrote", out.relative_to(DIST))

    # Static assets
    for sub in ("css", "js", "fonts"):
        src = STATIC / sub
        dst = DIST / sub
        dst.mkdir(exist_ok=True)
        for f in src.iterdir():
            if sub == "fonts" and f.suffix != ".woff2":
                continue
            shutil.copy2(f, dst / f.name)
    for extra in ("favicon.svg", "favicon.ico", "og.png", "apple-touch-icon.png"):
        p = STATIC / extra
        if p.exists():
            shutil.copy2(p, DIST / extra)

    # robots + sitemap
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")
    today = datetime.date.today().isoformat()
    urls = [p["path"] for p in PAGES if not p.get("noindex")]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        pri = "1.0" if u == "/" else ("0.8" if u.startswith("/services/") or u in ("/coverage/", "/contact/") else "0.6")
        sm.append(f"  <url><loc>{SITE['url']}{u}</loc><lastmod>{today}</lastmod><priority>{pri}</priority></url>")
    sm.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sm) + "\n")

    # Vercel config: trailing slashes, security + cache headers, 404
    vercel = {
        "trailingSlash": True,
        "cleanUrls": False,
        "headers": [
            {"source": "/(.*)", "headers": [
                {"key": "X-Content-Type-Options", "value": "nosniff"},
                {"key": "X-Frame-Options", "value": "DENY"},
                {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()"},
                {"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload"},
            ]},
            {"source": "/fonts/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
            {"source": "/(css|js)/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=604800"}]},
        ],
    }
    (DIST / "vercel.json").write_text(json.dumps(vercel, indent=2))
    print("built", len(PAGES), "pages ->", DIST)


if __name__ == "__main__":
    render()
