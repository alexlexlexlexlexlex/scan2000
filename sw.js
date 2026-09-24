/* Scanner Douze - cache applicatif pour un fonctionnement hors ligne. */
var CACHE = "scanner-douze-v1";
var ASSETS = [
  "./",
  "index.html",
  "manifest.webmanifest",
  "vendor/jsQR.js",
  "vendor/xlsx.full.min.js",
  "icons/icon-180.png",
  "icons/icon-192.png",
  "icons/icon-512.png"
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE)
      .then(function (c) { return c.addAll(ASSETS); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (k) {
        return k === CACHE ? null : caches.delete(k);
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request).then(function (hit) {
      if (hit) return hit;
      return fetch(e.request).then(function (res) {
        var copy = res.clone();
        caches.open(CACHE).then(function (c) {
          try { c.put(e.request, copy); } catch (err) { /* requetes non cachables */ }
        });
        return res;
      })["catch"](function () {
        return caches.match("index.html");
      });
    })
  );
});
