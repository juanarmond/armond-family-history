// Minimal service worker — required for Chrome's beforeinstallprompt to fire.
// Caches nothing; exists solely to satisfy the PWA installability criteria.
// If you later want offline support, add fetch/cache logic here.

const CACHE = "armond-family-v1";

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
