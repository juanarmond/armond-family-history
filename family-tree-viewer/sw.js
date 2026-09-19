// Minimal service worker — required for Chrome's beforeinstallprompt to fire.
// Chrome's installability checklist still requires a fetch event handler; this
// one is a transparent passthrough (no caching). Add cache logic here if you
// ever want offline support.

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (e) => e.respondWith(fetch(e.request)));
