/* SCAN2000 - cache applicatif.

   La page elle-meme passe par le reseau EN PREMIER : sans cela, une appli
   ajoutee a l'ecran d'accueil sert eternellement la version mise en cache
   le jour de l'installation, et ne voit aucune correction. Le cache ne
   sert plus que de filet quand le reseau manque.

   Les bibliotheques, elles, restent servies depuis le cache d'abord :
   elles ne changent qu'avec le numero de version ci-dessous. */
var CACHE = "scan2000-v3";
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

function enCache(req, res) {
  var copie = res.clone();
  caches.open(CACHE).then(function (c) {
    try { c.put(req, copie); } catch (err) { /* non cachable */ }
  });
  return res;
}

self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;

  var url = new URL(e.request.url);
  var estLaPage = e.request.mode === "navigate"
    || (url.origin === location.origin
        && (url.pathname.endsWith("/") || url.pathname.endsWith(".html")));

  if (estLaPage) {
    e.respondWith(
      fetch(e.request).then(function (res) { return enCache(e.request, res); })
        ["catch"](function () {
          return caches.match(e.request).then(function (hit) {
            return hit || caches.match("index.html");
          });
        })
    );
    return;
  }

  e.respondWith(
    caches.match(e.request).then(function (hit) {
      if (hit) return hit;
      return fetch(e.request).then(function (res) {
        return enCache(e.request, res);
      })["catch"](function () { return caches.match("index.html"); });
    })
  );
});
