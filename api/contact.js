// Contact form handler — Vercel Serverless Function (Node runtime, no dependencies).
// Configure in Vercel → Project → Settings → Environment Variables:
//   RESEND_API_KEY  = re_xxx            (from https://resend.com)
//   CONTACT_TO      = sales@oxitel.net  (where enquiries land)
//   CONTACT_FROM    = Oxitel Website <website@oxitel.net>   (optional; domain must be verified in Resend.
//                     Until then use "Oxitel Website <onboarding@resend.dev>" which only delivers to the Resend account owner.)

const MAX = { name: 120, company: 120, email: 200, country: 80, interest: 60, message: 4000 };

function clean(v, max) {
  return String(v ?? "").replace(/[\u0000-\u001F\u007F]/g, " ").trim().slice(0, max);
}

async function readBody(req) {
  if (req.body && typeof req.body === "object") return req.body;
  const raw = await new Promise((resolve) => {
    let d = ""; req.on("data", (c) => (d += c)); req.on("end", () => resolve(d));
  });
  const type = req.headers["content-type"] || "";
  if (type.includes("application/json")) { try { return JSON.parse(raw); } catch { return {}; } }
  return Object.fromEntries(new URLSearchParams(raw));
}

module.exports = async (req, res) => {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") { res.statusCode = 405; res.setHeader("Allow", "POST"); return res.end(JSON.stringify({ ok: false, error: "method_not_allowed" })); }

  const body = await readBody(req);
  const wantsJson = (req.headers.accept || "").includes("application/json");
  const reply = (code, payload, redirect) => {
    if (!wantsJson && redirect) { res.statusCode = 303; res.setHeader("Location", redirect); return res.end(); }
    res.statusCode = code; res.setHeader("Content-Type", "application/json"); return res.end(JSON.stringify(payload));
  };

  // Honeypot: bots fill hidden fields. Pretend success.
  if (body["bot-field"]) return reply(200, { ok: true }, "/contact/thanks/");

  const data = {
    name: clean(body.name, MAX.name),
    company: clean(body.company, MAX.company),
    email: clean(body.email, MAX.email),
    country: clean(body.country, MAX.country),
    interest: clean(body.interest, MAX.interest),
    message: clean(body.message, MAX.message),
  };
  if (!data.name || !data.company || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email) || !data.message) {
    return reply(400, { ok: false, error: "invalid" }, "/contact/?error=invalid");
  }

  const key = process.env.RESEND_API_KEY;
  const to = process.env.CONTACT_TO;
  if (!key || !to) return reply(503, { ok: false, error: "not_configured" }, "/contact/?error=not_configured");

  const from = process.env.CONTACT_FROM || "Oxitel Website <onboarding@resend.dev>";
  const text =
`New enquiry from oxitel.net

Name:      ${data.name}
Company:   ${data.company}
Email:     ${data.email}
Country:   ${data.country || "-"}
Interest:  ${data.interest || "-"}

${data.message}
`;
  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from, to: [to], reply_to: data.email, subject: `[oxitel.net] ${data.interest || "Enquiry"} — ${data.company}`, text }),
    });
    if (!r.ok) throw new Error("resend " + r.status + " " + (await r.text()));
    return reply(200, { ok: true }, "/contact/thanks/");
  } catch (err) {
    console.error(err);
    return reply(502, { ok: false, error: "send_failed" }, "/contact/?error=send_failed");
  }
};
