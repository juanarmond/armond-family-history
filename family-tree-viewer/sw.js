// Service worker — for the optional "What's new" push notifications, and for Chrome's install
// prompt (beforeinstallprompt), which still asks for a fetch handler. The handler answers only
// page loads, and passes them straight to the network (no caching): images, scripts and data
// load directly, so a scan never streams through the worker (the suspected cause of scans left
// half-drawn on an iPhone). Add cache logic here if you ever want offline support.

// Must match NOTIFY_API in app.js.
const NOTIFY_API = "https://family-notify.juan-armond.workers.dev";

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (event) => {
  if (event.request.mode === "navigate") event.respondWith(fetch(event.request));
});

// A push from the family-notify Worker: { title, body, url, tag }. One tag means a newer
// summary replaces an unread older one instead of stacking up.
self.addEventListener("push", (event) => {
  let data = {};
  try {
    data = event.data ? event.data.json() : {};
  } catch {
    data = { body: event.data ? event.data.text() : "" };
  }
  event.waitUntil(Promise.all([
    self.registration.showNotification(data.title || "Quatro Rios", {
      body: data.body || "",
      tag: data.tag || "whats-new",
      renotify: true,
      icon: "icon-192.png",
      badge: "icon-192.png",
      data: { url: data.url || "./?open=updates" },
    }),
    // A dot on the installed app's icon until What's new is opened (the page clears it).
    self.navigator && "setAppBadge" in self.navigator ? self.navigator.setAppBadge().catch(() => {}) : null,
  ]));
});

// Tapping the notification: bring an open copy of the site forward and ask it to show
// What's new, or open the site on What's new.
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const target = new URL((event.notification.data && event.notification.data.url) || "./?open=updates", self.registration.scope).href;
  event.waitUntil((async () => {
    const windows = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const client of windows) {
      // Only the app page listens for "open-updates" (not, say, terms.html).
      const path = new URL(client.url).pathname;
      const isApp = client.url.startsWith(self.registration.scope) && (path.endsWith("/") || path.endsWith("/index.html"));
      if (isApp && "focus" in client) {
        client.postMessage({ type: "open-updates" });
        return client.focus();
      }
    }
    return self.clients.openWindow(target);
  })());
});

// The browser replaced this device's push subscription (keys rotated or expired). Register the
// new one with the Worker, which carries over the old one's language and forgets the old one;
// without this the device would silently stop receiving notifications.
self.addEventListener("pushsubscriptionchange", (event) => {
  event.waitUntil((async () => {
    try {
      let subscription = event.newSubscription;
      if (!subscription) {
        const health = await (await fetch(`${NOTIFY_API}/health`, { cache: "no-store" })).json();
        if (!health || !health.ok || !health.publicKey) return;
        const base64 = health.publicKey.replace(/-/g, "+").replace(/_/g, "/");
        const key = Uint8Array.from(atob(base64 + "=".repeat((4 - (base64.length % 4)) % 4)), (c) => c.charCodeAt(0));
        subscription = await self.registration.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: key });
      }
      await fetch(`${NOTIFY_API}/subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subscription: subscription.toJSON(),
          replaces: event.oldSubscription ? event.oldSubscription.endpoint : undefined,
        }),
      });
    } catch { /* the page's daily re-sync is the fallback */ }
  })());
});
