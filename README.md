# oxitel.net — website

Static, dependency-free site for Oxitel (wholesale voice carrier). Built 7 Sep 2026 from Content v2 and the design foundations style guide.

## Structure
```
src/pages/*.html        one file per page — front matter (route, title, description) + the page HTML
src/partials/           layout.html (head), nav.html, footer.html
src/assets/css/         styles.css (tokens = Figma variables)
src/assets/js/          main.js (nav, page-load sequence, reveals, FAQ, filters, contact form)
src/assets/img/         favicon.svg, logo-mark.svg, og.png, apple-touch-icon.png
api/contact.js          Vercel serverless function for the contact form
build.js                builds src/ → dist/ (adds sitemap.xml, robots.txt, 404.html, cache-busting)
vercel.json             clean URLs, trailing slashes, security + cache headers
```

## Run locally
```
node build.js            # → dist/
npx serve dist           # http://localhost:3000
```

## Edit copy
Change the HTML in `src/pages/`. Titles and meta descriptions are in the front matter at the top of each file. Rebuild.

## Deploy (Vercel)
From this folder:
```
npm i -g vercel
vercel --prod
```
Or push this folder to GitHub and import it in Vercel (framework: Other, build: `node build.js`, output: `dist`).

No-CLI fallback: build locally with `node build.js`, then drag the `dist` folder onto https://app.netlify.com/drop. Everything works except the contact form (the serverless function is Vercel-specific), which falls back to showing the sales@ email.

## Connect the contact form (5 minutes)
1. Create a free account at https://resend.com and get an API key.
2. In Vercel → Project → Settings → Environment Variables add:
   - `RESEND_API_KEY` = your key
   - `CONTACT_TO` = the inbox that should receive enquiries (e.g. sales@oxitel.net)
   - `CONTACT_FROM` = `Oxitel Website <website@oxitel.net>` after verifying oxitel.net in Resend
     (until then leave it unset; Resend's onboarding sender only delivers to the account owner's email)
3. Redeploy. Until this is done the form shows "email us directly at sales@oxitel.net".

## Connect the domain
Vercel → Project → Settings → Domains → add `oxitel.net` and `www.oxitel.net`. Vercel shows the DNS records to add at GoDaddy (an A record for the apex and a CNAME for www). Propagation takes minutes to a few hours; SSL is automatic.

## Dummy content to confirm with the client
- Legal entity name (footer, privacy, terms) — currently "Oxitel"
- Emails sales@ / noc@ / info@oxitel.net — mailboxes must exist
- Office address, phone number, office hours (contact page + footer)
- Countries where DID numbers are available (virtual-numbers page)
- Partner-route destination list on the coverage page (src/pages/07-coverage.html)
- Founded year (about page), codecs, billing model, setup times, rate update cadence
- LinkedIn URL in the footer
