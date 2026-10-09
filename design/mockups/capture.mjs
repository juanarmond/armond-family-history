// Regenerates the screen references in design/mockups/screens/ from the real viewer.
//
//   uv run --frozen python scripts/build_pages_site.py   # privacy-filtered build in _site/
//   node design/mockups/capture.mjs                       # mobile + desktop screens
//
// It serves the privacy-filtered build (never the raw data, so no living person's details can
// appear), drives headless Chrome over the DevTools protocol, and saves WebP screenshots. The
// visitor counter, analytics, the AI assistant Worker and the flag CDN are blocked, so a run
// never counts as a visit or spends an AI call. Set CHROME to use another Chrome binary.
import { spawn } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.resolve(HERE, "../../_site");
const OUT = path.join(HERE, "screens");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const BLOCKED = ["*family-visitor-counter*", "*cloudflareinsights*", "*family-assistant*", "*flagcdn*"];
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

if (!fs.existsSync(path.join(SITE, "index.html"))) {
  console.error("No _site/ build found. Run: uv run --frozen python scripts/build_pages_site.py");
  process.exit(1);
}

// ---------- A static server for _site/ ----------
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css",
  ".json": "application/json", ".yaml": "text/yaml", ".svg": "image/svg+xml", ".png": "image/png",
  ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webmanifest": "application/manifest+json", ".pdf": "application/pdf" };
const server = http.createServer((request, response) => {
  const urlPath = decodeURIComponent(new URL(request.url, "http://x").pathname);
  const file = path.join(SITE, urlPath.endsWith("/") ? `${urlPath}index.html` : urlPath);
  if (!file.startsWith(SITE) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    response.writeHead(404).end();
    return;
  }
  response.writeHead(200, { "Content-Type": TYPES[path.extname(file).toLowerCase()] || "application/octet-stream" });
  fs.createReadStream(file).pipe(response);
});
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const BASE = `http://127.0.0.1:${server.address().port}`;

// ---------- Headless Chrome over the DevTools protocol ----------
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "mockup-capture-"));
const port = 9400 + Math.floor(Math.random() * 400);
const chrome = spawn(CHROME, ["--headless=new", "--disable-gpu", "--hide-scrollbars", `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`, "--no-first-run", "--window-size=1440,900", "about:blank"], { stdio: "ignore" });
let targets = [];
for (let i = 0; i < 60 && !targets.length; i += 1) {
  try { targets = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).filter((t) => t.type === "page"); } catch { /* starting */ }
  if (!targets.length) await sleep(200);
}
const socket = new WebSocket(targets[0].webSocketDebuggerUrl);
await new Promise((resolve) => socket.addEventListener("open", resolve));
let nextId = 0;
const pending = new Map();
const errors = [];
socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) { pending.get(message.id)(message); pending.delete(message.id); }
  if (message.method === "Runtime.exceptionThrown") errors.push(message.params.exceptionDetails.exception?.description);
});
const send = (method, params = {}) => new Promise((resolve) => {
  const id = ++nextId;
  pending.set(id, resolve);
  socket.send(JSON.stringify({ id, method, params }));
});
await send("Runtime.enable");
await send("Page.enable");
await send("Network.enable");
await send("Network.setBlockedURLs", { urls: BLOCKED });

const evaluate = async (expression) => {
  const reply = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (reply.result?.exceptionDetails) throw new Error(`${expression}\n${reply.result.exceptionDetails.exception?.description}`);
  return reply.result?.result?.value;
};
const click = async (selector, wait = 700) => {
  const found = await evaluate(`(() => { const el = document.querySelector(${JSON.stringify(selector)}); if (el) el.click(); return Boolean(el); })()`);
  if (!found) throw new Error(`Nothing matches ${selector}`);
  await sleep(wait);
};
const clickText = async (selector, text, wait = 700) => {
  const found = await evaluate(`(() => { const el = [...document.querySelectorAll(${JSON.stringify(selector)})].find((node) => node.textContent.includes(${JSON.stringify(text)})); if (el) el.click(); return Boolean(el); })()`);
  if (!found) throw new Error(`No ${selector} containing “${text}”`);
  await sleep(wait);
};
const type = async (text) => {
  await evaluate(`(() => { const box = document.querySelector('#person-search'); box.focus(); box.value = ${JSON.stringify(text)}; box.dispatchEvent(new Event('input')); })()`);
  await sleep(500);
};
const scroll = async (selector, top) => { await evaluate(`(document.querySelector(${JSON.stringify(selector)}) || document.scrollingElement).scrollTop = ${top}`); await sleep(300); };

// The newest curated What's new entries are left unread, so the badge and NEW marks show.
const feed = JSON.parse(fs.readFileSync(path.join(SITE, "updates.json"), "utf8")).updates
  .slice().sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")));
const curatedKeys = feed.filter((entry) => (entry.kind || "document") !== "document").map((entry) => `${entry.date || ""}|${entry.title || ""}`);
const seenKeys = curatedKeys.slice(6);

let device = "mobile";
async function viewport(kind) {
  device = kind;
  if (kind === "mobile") {
    await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
    await send("Emulation.setTouchEmulationEnabled", { enabled: true });
  } else {
    await send("Emulation.setTouchEmulationEnabled", { enabled: false });
    await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  }
}

// A clean start: this device's choices, then a full page load of the app.
let loads = 0;
async function open({ branch = "all", lang = "en", guideSeen = true, hash = "" } = {}) {
  await send("Page.navigate", { url: `${BASE}/terms.html` });
  await sleep(600);
  const storage = { "armond-viewer-lang": lang, "armond-updates-seen-v1": JSON.stringify(seenKeys) };
  if (branch !== null) storage["armond-viewer-branches"] = branch;
  if (guideSeen) storage["armond-viewer-guide-seen-v1"] = "1";
  await evaluate(`localStorage.clear(); Object.entries(${JSON.stringify(storage)}).forEach(([k, v]) => localStorage.setItem(k, v));`);
  loads += 1;
  await send("Page.navigate", { url: `${BASE}/index.html?load=${loads}${hash ? `#${hash}` : ""}` });
  await sleep(device === "mobile" ? 3500 : 4500);
}

const written = [];
async function shot(name) {
  const reply = await send("Page.captureScreenshot", { format: "webp", quality: 82 });
  const dir = path.join(OUT, device);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, `${name}.webp`), Buffer.from(reply.result.data, "base64"));
  written.push(`${device}/${name}.webp`);
}

// ---------- Mobile ----------
await viewport("mobile");
await open({ branch: null });
await shot("01-welcome");
await click(".branch-help", 800);
await shot("01b-start-help");
await scroll("#guide-panel", 560);
await shot("01c-install-steps");
await click("#close-guide", 500);
await evaluate("document.querySelectorAll('.branch-both')[1].click()");
await sleep(400);
await shot("02-welcome-one-side");

await open({ branch: "all" });
await shot("03-home-everything");
await open({ branch: "muniz,bohrer" });
await shot("04-home-chosen-families");
await scroll(null, 560);
await shot("05-home-surnames");
await scroll(null, 0);
await type("Maria");
await shot("06-search-chosen-families");
await click(".search-more", 500);
await shot("07-search-everyone");
await type("");
await evaluate("document.querySelector('#person-search').blur()");
await sleep(300);
await click(".surname-chip-all");
await shot("08-surnames-a-z");
await clickText(".surname-chip", "Bohrer");
await shot("09-surname-people");
await click(".mobile-nav-home");
await clickText(".mobile-row", "Celina Bohrer");
await shot("10-person-focus");

await open({ branch: "muniz,bohrer", hash: "sel=P-0007" });
await shot("11-person-page");
await scroll("#details-panel", 1500);
await shot("12-person-page-sources");
await click(".tab[data-tab=assistant]", 900);
await shot("13-ask-ai-about-person");

await open({ branch: "all", hash: "sel=P-0004" });
await click(".portrait-more-btn", 900);
await scroll(".portrait-panel-body", 700);
await shot("14-more-details");
await evaluate("document.querySelector('.portrait-panel .portrait-close:last-child').click()");
await sleep(400);
await click("#details-content .reader-open", 1800);
await shot("15-record-reader");

await open({ branch: "muniz,bohrer" });
await click(".tab[data-tab=updates]", 1600);
await shot("16-whats-new");
await click(".tab[data-tab=story]", 1500);
await shot("17-story");
await click(".tab[data-tab=family]", 500);
await click("#branch-chip");
await shot("18-families-sheet");
await click(".branch-panel .branch-cta", 400);
await click("#home-button", 800);
await shot("19-start-again");
await click(".branch-panel .branch-cta", 600);
await click("#header-help", 800);
await shot("20-help");

await open({ branch: "all", lang: "pt-BR" });
await shot("21-home-portuguese");

// ---------- Desktop ----------
await viewport("desktop");
await open({ branch: null });
await shot("01-welcome");
await click(".branch-help", 800);
await shot("01b-start-help");
await open({ branch: "all" });
await shot("02-tree-everything");
await open({ branch: "bohrer" });
await shot("03-tree-one-family");
await click("#branch-chip-toolbar");
await shot("04-families-sheet");
await click(".branch-panel .branch-cta", 400);
await open({ branch: "muniz,bohrer" });
await type("Maria");
await shot("05-search-chosen-families");
await open({ branch: "muniz,bohrer", hash: "sel=P-0007" });
await shot("06-person-panel");
await open({ branch: "muniz,bohrer" });
await click("#open-updates", 1600);
await shot("07-whats-new");
await open({ branch: "muniz,bohrer" });
await click("#open-story", 1500);
await shot("08-story");
await open({ branch: "all", hash: "sel=P-0007" });
await click("#detail-ask-ai", 900);
await shot("09-ask-ai");
await open({ branch: "all" });
await click("#help-fab", 800);
await shot("10-help");

socket.close();
chrome.kill();
server.close();
fs.rmSync(profile, { recursive: true, force: true });
console.log(`Wrote ${written.length} screens to ${path.relative(process.cwd(), OUT)}/`);
if (errors.length) {
  console.log(`Page errors:\n${errors.join("\n")}`);
  process.exitCode = 1;
}
