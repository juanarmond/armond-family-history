// Visitor counter + country for the Four Rivers family site (juanarmond.github.io).
//
// A Cloudflare Worker: privacy-first, no cookies, no personal data stored. It
// keeps a single running total in a KV namespace and reads the caller's country
// from Cloudflare's edge (request.cf.country) — Cloudflare gives every Worker the
// country of the requester automatically, so no third-party geo-IP service is
// needed. It never stores or returns anything that identifies an individual.
//
// Responses (JSON):
//   GET /            -> { total, country }            (returning visitor)
//   GET /?new=1      -> { total, country, number }    (first-ever visit: increments)
//
// Setup: bind a KV namespace as COUNTER (see README.md). The front-end owns the
// visitor's own number in localStorage; the Worker only ever increments the
// global total when the page reports a brand-new visitor (?new=1).

const ALLOW_ORIGIN = "https://juanarmond.github.io";

function corsHeaders(request) {
  const origin = request.headers.get("Origin") || "";
  return {
    // Echo the site origin when it matches; otherwise still answer (the count is
    // not sensitive) but pin the header to the canonical site.
    "Access-Control-Allow-Origin": origin === ALLOW_ORIGIN ? origin : ALLOW_ORIGIN,
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Cache-Control": "no-store",
    "Vary": "Origin",
  };
}

export default {
  async fetch(request, env) {
    const cors = corsHeaders(request);

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: cors });
    }
    if (request.method !== "GET") {
      return new Response("Method Not Allowed", { status: 405, headers: cors });
    }

    const country = (request.cf && request.cf.country) || "XX";
    const isNew = new URL(request.url).searchParams.get("new") === "1";

    let total = parseInt(await env.COUNTER.get("total"), 10);
    if (!Number.isFinite(total) || total < 0) total = 0;

    const body = { country };
    if (isNew) {
      total += 1;
      body.number = total;
      // KV is eventually consistent and non-atomic; at family-site volume the
      // odd concurrent collision is acceptable. Durable Objects would make this
      // strictly atomic if the count ever needs to be exact.
      await env.COUNTER.put("total", String(total));
    }
    body.total = total;

    return new Response(JSON.stringify(body), {
      headers: { ...cors, "Content-Type": "application/json" },
    });
  },
};
