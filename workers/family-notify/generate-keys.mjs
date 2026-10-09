// One-time setup for the family-notify Worker: create the VAPID key pair and the token
// the deploy workflow uses to call /notify.
//
//   node workers/family-notify/generate-keys.mjs
//
// Writes the PUBLIC key into wrangler.toml (it is not secret). Writes the private key and
// the token to the gitignored _local/ folder, and never prints them, so they stay out of
// git, logs and chat transcripts. Refuses to overwrite existing keys: rotating them would
// silently break every existing subscription.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..");
const localDir = join(root, "_local");
const privatePath = join(localDir, "notify-vapid-private-key.txt");
const tokenPath = join(localDir, "notify-token.txt");
const tomlPath = join(here, "wrangler.toml");

const b64url = (bytes) => Buffer.from(bytes).toString("base64url");

if (existsSync(privatePath)) {
  console.error(`Keys already exist (${privatePath}); not overwriting. Delete it first to rotate.`);
  process.exit(1);
}

const { subtle } = globalThis.crypto;
const keys = await subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign", "verify"]);
const publicKey = b64url(new Uint8Array(await subtle.exportKey("raw", keys.publicKey)));
const privateKey = (await subtle.exportKey("jwk", keys.privateKey)).d;
const token = b64url(globalThis.crypto.getRandomValues(new Uint8Array(32)));

mkdirSync(localDir, { recursive: true });
writeFileSync(privatePath, privateKey, { mode: 0o600 });
writeFileSync(tokenPath, token, { mode: 0o600 });
const toml = readFileSync(tomlPath, "utf8").replace(/^VAPID_PUBLIC_KEY = ".*"$/m, `VAPID_PUBLIC_KEY = "${publicKey}"`);
writeFileSync(tomlPath, toml);

console.log(`VAPID public key (written to wrangler.toml): ${publicKey}`);
console.log(`Private key -> ${privatePath}`);
console.log(`Deploy token -> ${tokenPath}`);
console.log("Next steps: workers/family-notify/README.md");
