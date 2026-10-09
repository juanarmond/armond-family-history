// Service worker — required for Chrome's beforeinstallprompt to fire, and for the
// optional "What's new" push notifications. Chrome's installability checklist still
// requires a fetch event handler; this one is a transparent passthrough (no caching).
// Add cache logic here if you ever want offline support.

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (e) => e.respondWith(fetch(e.request)));

// A push from the family-notify Worker: { title, body, url, tag }. One tag means a newer
// summary replaces an unread older one instead of stacking up.
self.addEventListener("push", (event) => {
  let data = {};
  try {
    data = event.data ? event.data.json() : {};
  } catch {
    data = { body: event.data ? event.data.text() : "" };
  }
  event.waitUntil(self.registration.showNotification(data.title || "Quatro Rios", {
    body: data.body || "",
    tag: data.tag || "whats-new",
    renotify: true,
    icon: "icon-192.png",
    badge: "icon-192.png",
    data: { url: data.url || "./?open=updates" },
  }));
});

// Tapping the notification: bring an open copy of the site forward and ask it to show
// What's new, or open the site on What's new.
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const target = new URL((event.notification.data && event.notification.data.url) || "./?open=updates", self.registration.scope).href;
  event.waitUntil((async () => {
    const windows = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const client of windows) {
      if (client.url.startsWith(self.registration.scope) && "focus" in client) {
        client.postMessage({ type: "open-updates" });
        return client.focus();
      }
    }
    return self.clients.openWindow(target);
  })());
});
