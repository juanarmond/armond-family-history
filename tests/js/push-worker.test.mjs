// End-to-end tests of the family-notify Worker's HTTP handler, with an in-memory KV
// namespace and a mocked push service: origin checks, subscription validation, the
// /notify token, cleanup of dead subscriptions, idempotent re-runs and pagination.
import { afterEach, test } from "node:test";
import assert from "node:assert/strict";

import worker, { b64urlEncode } from "../../workers/family-notify/worker.js";

const { subtle } = globalThis.crypto;
const SITE = "https://juanarmond.github.io";
const realFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = realFetch; });

function memoryKv() {
  const map = new Map();
  return {
    map,
    async put(key, value, options = {}) { map.set(key, { value, metadata: options.metadata ?? null }); },
    async get(key, type) {
      const entry = map.get(key);
      if (!entry) return null;
      return type === "json" ? JSON.parse(entry.value) : entry.value;
    },
    async delete(key) { map.delete(key); },
    async list({ prefix = "", limit = 1000, cursor } = {}) {
      const keys = [...map.keys()].filter((key) => key.startsWith(prefix)).sort();
      const start = cursor ? Number(cursor) : 0;
      const end = start + limit;
      return {
        keys: keys.slice(start, end).map((name) => ({ name, metadata: map.get(name).metadata })),
        list_complete: end >= keys.length,
        cursor: end >= keys.length ? undefined : String(end),
      };
    },
    subscriptions() {
      return [...map.entries()].filter(([key]) => key.startsWith("sub:")).map(([, entry]) => JSON.parse(entry.value));
    },
  };
}

async function makeEnv() {
  const vapid = await subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign", "verify"]);
  return {
    SUBSCRIPTIONS: memoryKv(),
    VAPID_PUBLIC_KEY: b64urlEncode(new Uint8Array(await subtle.exportKey("raw", vapid.publicKey))),
    VAPID_PRIVATE_KEY: (await subtle.exportKey("jwk", vapid.privateKey)).d,
    NOTIFY_TOKEN: "secret-token",
  };
}

async function browserSubscription(endpoint) {
  const keys = await subtle.generateKey({ name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]);
  return {
    endpoint,
    keys: {
      p256dh: b64urlEncode(new Uint8Array(await subtle.exportKey("raw", keys.publicKey))),
      auth: b64urlEncode(globalThis.crypto.getRandomValues(new Uint8Array(16))),
    },
  };
}

function post(path, body, headers = {}) {
  return new Request(`https://family-notify.example${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Origin: SITE, ...headers },
    body: JSON.stringify(body),
  });
}

const AUTH = { Authorization: "Bearer secret-token" };
const MESSAGE = { title: { en: "Hello", pt: "Olá" }, body: { en: "News", pt: "Novidades" } };

test("health reports whether the Worker is configured", async () => {
  const bare = await worker.fetch(new Request("https://x/health"), {});
  assert.deepEqual(await bare.json(), { ok: false, publicKey: null });
  const env = await makeEnv();
  const ready = await (await worker.fetch(new Request("https://x/health"), env)).json();
  assert.equal(ready.ok, true);
  assert.equal(ready.publicKey, env.VAPID_PUBLIC_KEY);
});

test("subscribe accepts only the site's origin, real push services and real keys", async () => {
  const env = await makeEnv();
  const good = await browserSubscription("https://fcm.googleapis.com/fcm/send/one");
  const foreign = await worker.fetch(post("/subscribe", { subscription: good }, { Origin: "https://evil.example" }), env);
  assert.equal(foreign.status, 403);
  const notPush = await browserSubscription("https://evil.example/collect");
  assert.equal((await worker.fetch(post("/subscribe", { subscription: notPush }), env)).status, 400);
  const notBase64 = { ...good, keys: { p256dh: "not*base64", auth: "x" } };
  const badKeysResponse = await worker.fetch(post("/subscribe", { subscription: notBase64 }), env);
  assert.equal(badKeysResponse.status, 400);
  assert.equal(badKeysResponse.headers.get("Access-Control-Allow-Origin"), SITE);
  const offCurve = { ...good, keys: { p256dh: b64urlEncode(Uint8Array.of(4, ...new Uint8Array(64).fill(7))), auth: good.keys.auth } };
  assert.equal((await worker.fetch(post("/subscribe", { subscription: offCurve }), env)).status, 400);

  const ok = await worker.fetch(post("/subscribe", { subscription: good, lang: "pt-BR" }), env);
  assert.equal(ok.status, 200);
  const [stored] = env.SUBSCRIPTIONS.subscriptions();
  assert.deepEqual(Object.keys(stored).sort(), ["endpoint", "keys", "lang"]);
  assert.equal(stored.lang, "pt-BR");
});

test("a replaced subscription keeps its language and the old one is removed", async () => {
  const env = await makeEnv();
  const original = await browserSubscription("https://updates.push.services.mozilla.com/wpush/v2/old");
  await worker.fetch(post("/subscribe", { subscription: original, lang: "pt-BR" }), env);
  const replacement = await browserSubscription("https://updates.push.services.mozilla.com/wpush/v2/new");
  await worker.fetch(post("/subscribe", { subscription: replacement, replaces: original.endpoint }), env);
  const stored = env.SUBSCRIPTIONS.subscriptions();
  assert.equal(stored.length, 1);
  assert.equal(stored[0].endpoint, replacement.endpoint);
  assert.equal(stored[0].lang, "pt-BR");
});

test("notify needs the token, signs and encrypts, and drops expired subscriptions", async () => {
  const env = await makeEnv();
  await worker.fetch(post("/subscribe", { subscription: await browserSubscription("https://fcm.googleapis.com/fcm/send/live") }), env);
  await worker.fetch(post("/subscribe", { subscription: await browserSubscription("https://web.push.apple.com/gone") }), env);
  const calls = [];
  globalThis.fetch = async (url, init) => {
    calls.push({ url, init });
    return new Response(null, { status: String(url).includes("gone") ? 410 : 201 });
  };
  assert.equal((await worker.fetch(post("/notify", MESSAGE, { Authorization: "Bearer wrong" }), env)).status, 401);
  assert.equal(calls.length, 0);
  const result = await (await worker.fetch(post("/notify", MESSAGE, AUTH), env)).json();
  assert.deepEqual(result, { sent: 1, removed: 1, failed: 0, cursor: null });
  for (const { init } of calls) {
    assert.equal(init.headers["Content-Encoding"], "aes128gcm");
    assert.match(init.headers.Authorization, /^vapid t=.+, k=.+$/);
    assert.equal(init.headers.Topic, undefined, "Apple rejects a Topic header (BadWebPushTopic)");
  }
  assert.equal(env.SUBSCRIPTIONS.subscriptions().length, 1);
});

test("a subscription that keeps failing is dropped after three attempts; transient errors are not counted", async () => {
  const env = await makeEnv();
  await worker.fetch(post("/subscribe", { subscription: await browserSubscription("https://fcm.googleapis.com/fcm/send/broken") }), env);
  await worker.fetch(post("/subscribe", { subscription: await browserSubscription("https://fcm.googleapis.com/fcm/send/busy") }), env);
  globalThis.fetch = async (url) => new Response(null, { status: String(url).includes("broken") ? 403 : 503 });
  for (let attempt = 1; attempt <= 2; attempt += 1) {
    await worker.fetch(post("/notify", MESSAGE, AUTH), env);
    assert.equal(env.SUBSCRIPTIONS.subscriptions().length, 2);
  }
  const third = await (await worker.fetch(post("/notify", MESSAGE, AUTH), env)).json();
  assert.equal(third.removed, 1);
  const [left] = env.SUBSCRIPTIONS.subscriptions();
  assert.match(left.endpoint, /busy$/);
  assert.equal(left.fails, undefined);
});

test("re-sending the same message id skips pages that already went out", async () => {
  const env = await makeEnv();
  await worker.fetch(post("/subscribe", { subscription: await browserSubscription("https://fcm.googleapis.com/fcm/send/a") }), env);
  let pushes = 0;
  globalThis.fetch = async () => { pushes += 1; return new Response(null, { status: 201 }); };
  const first = await (await worker.fetch(post("/notify", { ...MESSAGE, id: "abc" }, AUTH), env)).json();
  assert.equal(first.sent, 1);
  const again = await (await worker.fetch(post("/notify", { ...MESSAGE, id: "abc" }, AUTH), env)).json();
  assert.equal(again.sent, 0);
  assert.equal(again.skipped, 1);
  assert.equal(pushes, 1);
});

test("notify pages through subscribers 20 at a time", async () => {
  const env = await makeEnv();
  for (let i = 0; i < 45; i += 1) {
    await worker.fetch(post("/subscribe", { subscription: await browserSubscription(`https://fcm.googleapis.com/fcm/send/device-${i}`) }), env);
  }
  globalThis.fetch = async () => new Response(null, { status: 201 });
  const sentPerPage = [];
  let cursor = null;
  do {
    const page = await (await worker.fetch(post("/notify", { ...MESSAGE, cursor }, AUTH), env)).json();
    sentPerPage.push(page.sent);
    cursor = page.cursor;
  } while (cursor);
  assert.deepEqual(sentPerPage, [20, 20, 5]);
});
