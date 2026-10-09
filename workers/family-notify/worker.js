// Web Push sender for the Quatro Rios family site (juanarmond.github.io).
//
// A Cloudflare Worker with no dependencies (so it can be pasted into the dashboard).
// It stores anonymous push subscriptions in a KV namespace and, when the deploy
// workflow calls /notify, sends one encrypted Web Push message (RFC 8291 aes128gcm,
// VAPID per RFC 8292) to every subscribed device. A subscription is only a push-service
// URL plus two browser keys: no name, e-mail or other personal data is ever stored.
//
// Endpoints:
//   GET  /health       -> { ok, publicKey }          the site uses it to show the button
//   POST /subscribe    { subscription, lang }        from the site (origin-checked)
//   POST /unsubscribe  { endpoint }                  from the site (origin-checked)
//   POST /notify       { title:{en,pt}, body:{en,pt}, url, tag, cursor }
//                      Authorization: Bearer NOTIFY_TOKEN — from the deploy workflow.
//                      Sends to one page of subscribers and returns { cursor } for the
//                      next page (the free plan allows 50 outgoing requests per call).
//
// Setup (see README.md): bind a KV namespace as SUBSCRIPTIONS; set the variable
// VAPID_PUBLIC_KEY and the secrets VAPID_PRIVATE_KEY and NOTIFY_TOKEN.

const ALLOW_ORIGIN = "https://juanarmond.github.io";
const VAPID_SUBJECT = "https://juanarmond.github.io/";
const PAGE_SIZE = 40;
const TTL_SECONDS = 4 * 24 * 3600;
const MAX_BODY_BYTES = 8192;
// Only real browser push services may be stored, so /notify can never be turned into a
// way of POSTing to arbitrary URLs.
const PUSH_HOSTS = [
  /(^|\.)push\.apple\.com$/,
  /^fcm\.googleapis\.com$/,
  /(^|\.)push\.services\.mozilla\.com$/,
  /(^|\.)notify\.windows\.com$/,
];

const encoder = new TextEncoder();

export function b64urlEncode(bytes) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

export function b64urlDecode(text) {
  const base64 = String(text).replace(/-/g, "+").replace(/_/g, "/");
  const binary = atob(base64 + "=".repeat((4 - (base64.length % 4)) % 4));
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

function concat(...parts) {
  const out = new Uint8Array(parts.reduce((sum, part) => sum + part.length, 0));
  let offset = 0;
  for (const part of parts) {
    out.set(part, offset);
    offset += part.length;
  }
  return out;
}

async function hmacSha256(keyBytes, dataBytes) {
  const key = await crypto.subtle.importKey(
    "raw", keyBytes, { name: "HMAC", hash: "SHA-256" }, false, ["sign"],
  );
  return new Uint8Array(await crypto.subtle.sign("HMAC", key, dataBytes));
}

export function isPushEndpoint(endpoint) {
  try {
    const url = new URL(endpoint);
    return url.protocol === "https:" && PUSH_HOSTS.some((pattern) => pattern.test(url.hostname));
  } catch {
    return false;
  }
}

// RFC 8291 message encryption with the aes128gcm content coding (RFC 8188): a single
// record, so the plaintext is followed by the 0x02 last-record delimiter.
export async function encryptPayload(plaintext, p256dh, auth, options = {}) {
  const uaPublic = b64urlDecode(p256dh);
  const authSecret = b64urlDecode(auth);
  const server = options.serverKeys
    || (await crypto.subtle.generateKey({ name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]));
  const asPublic = new Uint8Array(await crypto.subtle.exportKey("raw", server.publicKey));
  const uaKey = await crypto.subtle.importKey("raw", uaPublic, { name: "ECDH", namedCurve: "P-256" }, false, []);
  const ecdhSecret = new Uint8Array(
    await crypto.subtle.deriveBits({ name: "ECDH", public: uaKey }, server.privateKey, 256),
  );

  const prkKey = await hmacSha256(authSecret, ecdhSecret);
  const keyInfo = concat(encoder.encode("WebPush: info\0"), uaPublic, asPublic);
  const ikm = (await hmacSha256(prkKey, concat(keyInfo, Uint8Array.of(1)))).slice(0, 32);

  const salt = options.salt || crypto.getRandomValues(new Uint8Array(16));
  const prk = await hmacSha256(salt, ikm);
  const cek = (await hmacSha256(prk, concat(encoder.encode("Content-Encoding: aes128gcm\0"), Uint8Array.of(1)))).slice(0, 16);
  const nonce = (await hmacSha256(prk, concat(encoder.encode("Content-Encoding: nonce\0"), Uint8Array.of(1)))).slice(0, 12);

  const aesKey = await crypto.subtle.importKey("raw", cek, { name: "AES-GCM" }, false, ["encrypt"]);
  const ciphertext = new Uint8Array(
    await crypto.subtle.encrypt({ name: "AES-GCM", iv: nonce }, aesKey, concat(plaintext, Uint8Array.of(2))),
  );

  const header = new Uint8Array(16 + 4 + 1 + asPublic.length);
  header.set(salt, 0);
  new DataView(header.buffer).setUint32(16, 4096);
  header[20] = asPublic.length;
  header.set(asPublic, 21);
  return concat(header, ciphertext);
}

// RFC 8292 VAPID: a short-lived ES256 JWT for the push service's origin.
export async function vapidAuthorization(endpoint, publicKey, privateKey, now = Math.floor(Date.now() / 1000)) {
  const header = b64urlEncode(encoder.encode(JSON.stringify({ typ: "JWT", alg: "ES256" })));
  const claims = b64urlEncode(encoder.encode(JSON.stringify({
    aud: new URL(endpoint).origin,
    exp: now + 12 * 3600,
    sub: VAPID_SUBJECT,
  })));
  const raw = b64urlDecode(publicKey);
  const key = await crypto.subtle.importKey(
    "jwk",
    { kty: "EC", crv: "P-256", x: b64urlEncode(raw.slice(1, 33)), y: b64urlEncode(raw.slice(33, 65)), d: privateKey },
    { name: "ECDSA", namedCurve: "P-256" },
    false,
    ["sign"],
  );
  const signature = new Uint8Array(
    await crypto.subtle.sign({ name: "ECDSA", hash: "SHA-256" }, key, encoder.encode(`${header}.${claims}`)),
  );
  return `vapid t=${header}.${claims}.${b64urlEncode(signature)}, k=${publicKey}`;
}

async function sendPush(subscription, message, env) {
  const body = await encryptPayload(
    encoder.encode(JSON.stringify(message)), subscription.keys.p256dh, subscription.keys.auth,
  );
  const response = await fetch(subscription.endpoint, {
    method: "POST",
    headers: {
      Authorization: await vapidAuthorization(subscription.endpoint, env.VAPID_PUBLIC_KEY, env.VAPID_PRIVATE_KEY),
      "Content-Encoding": "aes128gcm",
      "Content-Type": "application/octet-stream",
      TTL: String(TTL_SECONDS),
      Urgency: "normal",
      Topic: "whats-new",
    },
    body,
  });
  return response.status;
}

function isAllowedOrigin(origin) {
  return origin === ALLOW_ORIGIN || /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin);
}

function corsHeaders(request) {
  const origin = request.headers.get("Origin") || "";
  return {
    "Access-Control-Allow-Origin": isAllowedOrigin(origin) ? origin : ALLOW_ORIGIN,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Cache-Control": "no-store",
    Vary: "Origin",
  };
}

function json(request, data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders(request) },
  });
}

async function readJson(request) {
  const text = await request.text();
  if (text.length > MAX_BODY_BYTES) throw new Error("body too large");
  return JSON.parse(text);
}

async function subscriptionKey(endpoint) {
  const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", encoder.encode(endpoint)));
  return `sub:${b64urlEncode(digest)}`;
}

function sameSecret(given, expected) {
  const a = encoder.encode(given || "");
  const b = encoder.encode(expected || "");
  let diff = a.length ^ b.length;
  for (let i = 0; i < Math.max(a.length, b.length); i += 1) diff |= (a[i] || 0) ^ (b[i] || 0);
  return diff === 0 && b.length > 0;
}

function configured(env) {
  return Boolean(env.SUBSCRIPTIONS && env.VAPID_PUBLIC_KEY && env.VAPID_PRIVATE_KEY);
}

async function subscribe(request, env) {
  if (!isAllowedOrigin(request.headers.get("Origin") || "")) return json(request, { error: "forbidden" }, 403);
  let data;
  try { data = await readJson(request); } catch { return json(request, { error: "bad request" }, 400); }
  const subscription = data && data.subscription;
  const keys = subscription && subscription.keys;
  if (!subscription || !isPushEndpoint(subscription.endpoint) || !keys
      || b64urlDecode(keys.p256dh || "").length !== 65 || b64urlDecode(keys.auth || "").length !== 16) {
    return json(request, { error: "invalid subscription" }, 400);
  }
  const lang = data.lang === "pt-BR" ? "pt-BR" : "en";
  await env.SUBSCRIPTIONS.put(await subscriptionKey(subscription.endpoint), JSON.stringify({
    endpoint: subscription.endpoint,
    keys: { p256dh: keys.p256dh, auth: keys.auth },
    lang,
    updated: new Date().toISOString().slice(0, 10),
  }));
  return json(request, { ok: true });
}

async function unsubscribe(request, env) {
  if (!isAllowedOrigin(request.headers.get("Origin") || "")) return json(request, { error: "forbidden" }, 403);
  let data;
  try { data = await readJson(request); } catch { return json(request, { error: "bad request" }, 400); }
  if (!data || typeof data.endpoint !== "string") return json(request, { error: "bad request" }, 400);
  await env.SUBSCRIPTIONS.delete(await subscriptionKey(data.endpoint));
  return json(request, { ok: true });
}

async function notify(request, env) {
  const token = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  if (!sameSecret(token, env.NOTIFY_TOKEN)) return json(request, { error: "unauthorised" }, 401);
  let data;
  try { data = await readJson(request); } catch { return json(request, { error: "bad request" }, 400); }
  const pick = (field, lang) => (field && (lang === "pt-BR" ? field.pt : field.en)) || "";

  const page = await env.SUBSCRIPTIONS.list({ prefix: "sub:", limit: PAGE_SIZE, cursor: data.cursor || undefined });
  let sent = 0;
  let removed = 0;
  let failed = 0;
  await Promise.all(page.keys.map(async ({ name }) => {
    const stored = await env.SUBSCRIPTIONS.get(name, "json");
    if (!stored) return;
    try {
      const status = await sendPush(stored, {
        title: pick(data.title, stored.lang),
        body: pick(data.body, stored.lang),
        url: data.url || "./?open=updates",
        tag: data.tag || "whats-new",
      }, env);
      if (status === 404 || status === 410) {
        await env.SUBSCRIPTIONS.delete(name);
        removed += 1;
      } else if (status >= 200 && status < 300) {
        sent += 1;
      } else {
        failed += 1;
      }
    } catch {
      failed += 1;
    }
  }));
  return json(request, { sent, removed, failed, cursor: page.list_complete ? null : page.cursor });
}

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders(request) });
    if (request.method === "GET" && pathname === "/health") {
      return json(request, { ok: configured(env), publicKey: configured(env) ? env.VAPID_PUBLIC_KEY : null });
    }
    if (!configured(env)) return json(request, { error: "not configured" }, 503);
    if (request.method === "POST" && pathname === "/subscribe") return subscribe(request, env);
    if (request.method === "POST" && pathname === "/unsubscribe") return unsubscribe(request, env);
    if (request.method === "POST" && pathname === "/notify") return notify(request, env);
    return json(request, { error: "not found" }, 404);
  },
};
