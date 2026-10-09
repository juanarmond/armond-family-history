// Round-trip tests for the family-notify Worker's Web Push crypto. The Worker encrypts
// (RFC 8291, aes128gcm) and signs (RFC 8292 VAPID); these tests decrypt the message the
// way a browser does and verify the JWT signature, so a broken derivation fails here
// rather than silently on people's phones.
import { test } from "node:test";
import assert from "node:assert/strict";

import {
  b64urlDecode,
  b64urlEncode,
  encryptPayload,
  isPushEndpoint,
  vapidAuthorization,
} from "../../workers/family-notify/worker.js";

const { subtle } = globalThis.crypto;
const encoder = new TextEncoder();

async function hmac(keyBytes, dataBytes) {
  const key = await subtle.importKey("raw", keyBytes, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return new Uint8Array(await subtle.sign("HMAC", key, dataBytes));
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

// The receiving side of RFC 8291, written independently of the Worker.
async function decrypt(body, uaKeys, authSecret) {
  const salt = body.slice(0, 16);
  const recordSize = new DataView(body.buffer, body.byteOffset).getUint32(16);
  const idLength = body[20];
  const asPublic = body.slice(21, 21 + idLength);
  const ciphertext = body.slice(21 + idLength);

  const uaPublic = new Uint8Array(await subtle.exportKey("raw", uaKeys.publicKey));
  const asKey = await subtle.importKey("raw", asPublic, { name: "ECDH", namedCurve: "P-256" }, false, []);
  const ecdhSecret = new Uint8Array(await subtle.deriveBits({ name: "ECDH", public: asKey }, uaKeys.privateKey, 256));
  const prkKey = await hmac(authSecret, ecdhSecret);
  const keyInfo = concat(encoder.encode("WebPush: info\0"), uaPublic, asPublic);
  const ikm = (await hmac(prkKey, concat(keyInfo, Uint8Array.of(1)))).slice(0, 32);
  const prk = await hmac(salt, ikm);
  const cek = (await hmac(prk, concat(encoder.encode("Content-Encoding: aes128gcm\0"), Uint8Array.of(1)))).slice(0, 16);
  const nonce = (await hmac(prk, concat(encoder.encode("Content-Encoding: nonce\0"), Uint8Array.of(1)))).slice(0, 12);
  const key = await subtle.importKey("raw", cek, { name: "AES-GCM" }, false, ["decrypt"]);
  const padded = new Uint8Array(await subtle.decrypt({ name: "AES-GCM", iv: nonce }, key, ciphertext));
  return { recordSize, plaintext: padded.slice(0, padded.lastIndexOf(2)), delimiter: padded[padded.length - 1] };
}

test("encryptPayload produces an aes128gcm message a browser can decrypt", async () => {
  const uaKeys = await subtle.generateKey({ name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]);
  const authSecret = globalThis.crypto.getRandomValues(new Uint8Array(16));
  const p256dh = b64urlEncode(new Uint8Array(await subtle.exportKey("raw", uaKeys.publicKey)));
  const message = JSON.stringify({ title: "Quatro Rios — novidades", body: "Correção: Celina Bohrer…" });

  const body = await encryptPayload(encoder.encode(message), p256dh, b64urlEncode(authSecret));
  const result = await decrypt(body, uaKeys, authSecret);

  assert.equal(result.recordSize, 4096);
  assert.equal(result.delimiter, 2);
  assert.equal(new TextDecoder().decode(result.plaintext), message);
});

test("vapidAuthorization signs a verifiable ES256 JWT for the push service origin", async () => {
  const keys = await subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign", "verify"]);
  const publicKey = b64urlEncode(new Uint8Array(await subtle.exportKey("raw", keys.publicKey)));
  const privateKey = (await subtle.exportKey("jwk", keys.privateKey)).d;
  const now = 1_800_000_000;

  const header = await vapidAuthorization("https://fcm.googleapis.com/fcm/send/abc", publicKey, privateKey, now);
  const match = /^vapid t=([^.]+)\.([^.]+)\.([^,]+), k=(.+)$/.exec(header);
  assert.ok(match, header);
  const [, jwtHeader, jwtClaims, signature, k] = match;
  assert.equal(k, publicKey);

  const claims = JSON.parse(new TextDecoder().decode(b64urlDecode(jwtClaims)));
  assert.equal(claims.aud, "https://fcm.googleapis.com");
  assert.equal(claims.exp, now + 12 * 3600);
  assert.match(claims.sub, /^https:\/\//);

  const verifyKey = await subtle.importKey("raw", b64urlDecode(publicKey), { name: "ECDSA", namedCurve: "P-256" }, false, ["verify"]);
  const valid = await subtle.verify(
    { name: "ECDSA", hash: "SHA-256" }, verifyKey, b64urlDecode(signature), encoder.encode(`${jwtHeader}.${jwtClaims}`),
  );
  assert.equal(valid, true);
});

test("isPushEndpoint accepts browser push services and nothing else", () => {
  assert.equal(isPushEndpoint("https://fcm.googleapis.com/fcm/send/abc"), true);
  assert.equal(isPushEndpoint("https://web.push.apple.com/QKx"), true);
  assert.equal(isPushEndpoint("https://updates.push.services.mozilla.com/wpush/v2/x"), true);
  assert.equal(isPushEndpoint("http://fcm.googleapis.com/fcm/send/abc"), false);
  assert.equal(isPushEndpoint("https://fcm.googleapis.com.evil.example/x"), false);
  assert.equal(isPushEndpoint("https://example.com/push"), false);
  assert.equal(isPushEndpoint("not a url"), false);
});
