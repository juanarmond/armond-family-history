// End-to-end tests of the family-notify Worker's HTTP handler, with an in-memory KV
// namespace and a mocked push service: origin checks, subscription validation, the
// /notify token, removal of expired subscriptions and pagination past 40 devices.
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
    async put(key, value) { map.set(key, value); },
    async get(key, type) {
      const value = map.get(key);
      if (value === undefined) return null;
      return type === "json" ? JSON.parse(value) : value;
    },
    async delete(key) { map.delete(key); },
    async list({ prefix = "", limit = 1000, cursor } = {}) {
      const keys = [...map.keys()].filter((key) => key.startsWith(prefix)).sort();
      const start = cursor ? Number(cursor) : 0;
      const end = start + limit;
      return {
        keys: keys.slice(start, end).map((name) => ({ name })),
        list_complete: end >= keys.length,
        cursor: end >= keys.length ? undefined : String(end),
      };
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

const MESSAGE = { title: { en: "Hello", pt: "Olá" }, body: { en: "News", pt: "Novidades" } };

test("health reports whether the Worker is configured", async () => {
  const bare = await worker.fetch(new Request("https://x/health"), {});
  assert.deepEqual(await bare.json(), { ok: false, publicKey: null });
  const env = await makeEnv();
  const ready = await (await worker.fetch(new Request("https://x/health"), env)).json();
  assert.equal(ready.ok, true);
  assert.equal(ready.publicKey, env.VAPID_PUBLIC_KEY);
});

test("subscribe accepts only the site's origin and real push services", async () => {
  const env = await makeEnv();
  const good = await browserSubscription("https://fcm.googleapis.com/fcm/send/one");
  const foreign = await worker.fetch(post("/subscribe", { subscription: good }, { Origin: "https://evil.example" }), env);
  assert.equal(foreign.status, 403);
  const notPush = await browserSubscription("https://evil.example/collect");
  assert.equal((await worker.fetch(post("/subscribe", { subscription: notPush }), env)).status, 400);
  const ok = await worker.fetch(post("/subscribe", { subscription: good, lang: "pt-BR" }), env);
  assert.equal(ok.status, 200);
  const [stored] = [...env.SUBSCRIPTIONS.map.values()].map((value) => JSON.parse(value));
  assert.equal(stored.lang, "pt-BR");
  assert.equal(stored.endpoint, good.endpoint);
  assert.equal(Object.keys(stored).includes("name"), false);
});

test("notify needs the token, sends in each device's language and drops expired ones", async () => {
  const env = await makeEnv();
  const live = await browserSubscription("https://fcm.googleapis.com/fcm/send/live");
  const gone = await browserSubscription("https://web.push.apple.com/gone");
  await worker.fetch(post("/subscribe", { subscription: live, lang: "en" }), env);
  await worker.fetch(post("/subscribe", { subscription: gone, lang: "pt-BR" }), env);

  const calls = [];
  globalThis.fetch = async (url, init) => {
    calls.push({ url, init });
    return new Response(null, { status: String(url).includes("gone") ? 410 : 201 });
  };

  const denied = await worker.fetch(post("/notify", MESSAGE, { Authorization: "Bearer wrong" }), env);
  assert.equal(denied.status, 401);
  assert.equal(calls.length, 0);

  const result = await (await worker.fetch(post("/notify", MESSAGE, { Authorization: "Bearer secret-token" }), env)).json();
  assert.deepEqual(result, { sent: 1, removed: 1, failed: 0, cursor: null });
  assert.equal(calls.length, 2);
  for (const { init } of calls) {
    assert.equal(init.headers["Content-Encoding"], "aes128gcm");
    assert.match(init.headers.Authorization, /^vapid t=.+, k=.+$/);
  }
  assert.equal(env.SUBSCRIPTIONS.map.size, 1);
});

test("notify pages through subscribers 40 at a time", async () => {
  const env = await makeEnv();
  for (let i = 0; i < 45; i += 1) {
    const subscription = await browserSubscription(`https://fcm.googleapis.com/fcm/send/device-${i}`);
    await worker.fetch(post("/subscribe", { subscription }), env);
  }
  globalThis.fetch = async () => new Response(null, { status: 201 });
  const auth = { Authorization: "Bearer secret-token" };
  const first = await (await worker.fetch(post("/notify", MESSAGE, auth), env)).json();
  assert.equal(first.sent, 40);
  assert.ok(first.cursor);
  const second = await (await worker.fetch(post("/notify", { ...MESSAGE, cursor: first.cursor }, auth), env)).json();
  assert.equal(second.sent, 5);
  assert.equal(second.cursor, null);
});
