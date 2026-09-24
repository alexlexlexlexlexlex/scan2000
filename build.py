"""Genere les fichiers derives du site : manifeste, service worker, icones,
README, et la variante publiee comme Artifact Claude.

L'unique source est index.html. Lancer : python build.py
"""
import json
import os
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
ARTIFACT_OUT = pathlib.Path(
    r"C:\Users\alexa\AppData\Local\Temp\claude"
    r"\C--Users-alexa-Documents-Bass2Partition-basse2partition-basse2partition"
    r"\ae0edbfa-06c2-4805-834a-7143265598e0\scratchpad\scanner-douze.html"
)

CDN_JSQR = "https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js"
CDN_XLSX = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"

src = (ROOT / "index.html").read_text(encoding="utf-8")

# ---------------------------------------------------------------- manifeste
manifest = {
    "name": "SCAN2000",
    "short_name": "SCAN2000",
    "description": "Releve de QR codes et de numeros imprimes, export Excel.",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#3A575A",
    "theme_color": "#2E4A4D",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png",
         "purpose": "maskable"},
    ],
}
(ROOT / "manifest.webmanifest").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
)

# ---------------------------------------------------------- service worker
# Le moteur OCR (environ 6 Mo) n'est PAS pre-cache : il serait telecharge au
# premier lancement meme sans jamais servir. Il entre dans le cache a sa
# premiere utilisation, via la branche reseau ci-dessous.
sw = """/* SCAN2000 - cache applicatif, pour un fonctionnement hors ligne. */
var CACHE = "scan2000-v2";
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
          try { c.put(e.request, copy); } catch (err) { /* non cachable */ }
        });
        return res;
      })["catch"](function () {
        return caches.match("index.html");
      });
    })
  );
});
"""
(ROOT / "sw.js").write_text(sw, encoding="utf-8")

# ------------------------------------------------------------------ icones
from PIL import Image, ImageDraw

SMOKY = "#161311"
TEAL = "#F5FFFF"
MYRTLE = "#4D7175"
SEALSALT = "#FAFAF8"


def icone(size):
    """Charte PI2000 : fond smoky, equerres teal, motif QR sealsalt."""
    img = Image.new("RGB", (size, size), SMOKY)
    d = ImageDraw.Draw(img)
    u = size / 24.0
    ep = max(2, int(round(u * 1.3)))
    m = int(round(u * 2.6))
    bras = int(round(u * 5.4))
    for cx, cy, sx, sy in ((m, m, 1, 1), (size - m, m, -1, 1),
                           (m, size - m, 1, -1), (size - m, size - m, -1, -1)):
        d.rectangle([min(cx, cx + sx * bras), min(cy, cy + sy * ep),
                     max(cx, cx + sx * bras), max(cy, cy + sy * ep)], fill=TEAL)
        d.rectangle([min(cx, cx + sx * ep), min(cy, cy + sy * bras),
                     max(cx, cx + sx * ep), max(cy, cy + sy * bras)], fill=TEAL)

    # motif QR stylise, grille 5x5 centree
    grille = [
        "11101",
        "10001",
        "11100",
        "00101",
        "10111",
    ]
    cell = int(round(u * 2.05))
    total = cell * 5
    ox = (size - total) // 2
    oy = (size - total) // 2
    for r, ligne in enumerate(grille):
        for c, v in enumerate(ligne):
            if v == "1":
                x0 = ox + c * cell
                y0 = oy + r * cell
                d.rectangle([x0, y0, x0 + cell - max(1, int(u * 0.35)),
                             y0 + cell - max(1, int(u * 0.35))], fill=SEALSALT)

    # ligne de balayage, comme le viseur de l'appli
    y = size // 2
    d.rectangle([int(u * 1.6), y - max(1, int(u * 0.22)),
                 size - int(u * 1.6), y + max(1, int(u * 0.22))], fill=MYRTLE)
    return img


(ROOT / "icons").mkdir(exist_ok=True)
for s in (180, 192, 512):
    icone(s).save(ROOT / "icons" / ("icon-%d.png" % s))

# ---------------------------------------------------- variante Artifact
# L'Artifact tourne dans une iframe : pas de service worker, pas de fichiers
# locaux, et le CSP y bloque les telechargements du moteur OCR. On retire donc
# l'OCR et on pointe les deux autres bibliotheques vers les CDN autorises.
art = src
art = art.replace('<script src="vendor/jsQR.js"></script>',
                  '<script src="%s"></script>' % CDN_JSQR)
art = art.replace('<script src="vendor/xlsx.full.min.js"></script>',
                  '<script src="%s"></script>' % CDN_XLSX)
art = art.replace('<script src="vendor/tesseract/tesseract.min.js"></script>\n', "")

bloc_sw = """
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("sw.js")["catch"](function () {});
    });
  }
"""
assert bloc_sw in art, "bloc service worker introuvable"
art = art.replace(bloc_sw, "")

# on ne garde que <title> ... </body>, l'hote fournit le reste du squelette
debut = art.index("<title>")
fin = art.index("</body>")
art = art[debut:fin]
art = art.replace('<link rel="manifest" href="manifest.webmanifest">\n', "")

# l'appli previent que l'OCR manque ici plutot que de laisser un bouton mort
art = art.replace(
    "Je lis le QR code. S\u2019il ne passe pas, je peux lire le num\u00e9ro imprim\u00e9 en dessous.",
    "Version de d\u00e9monstration : la cam\u00e9ra et la lecture du num\u00e9ro imprim\u00e9 "
    "ne fonctionnent que sur la version install\u00e9e."
)
ARTIFACT_OUT.write_text(art, encoding="utf-8")

# ------------------------------------------------------------------ README
readme = """# SCAN2000

Application web (PWA) interne : lit les QR codes d'un lot, retombe sur la
lecture optique du numero imprime quand le QR ne passe pas, et exporte le
releve en classeur Excel.

Reprend la direction artistique de PI2000 (charte MUBE 2025, interface a
reliefs, mascotte Peetoo) pour que les applis internes se ressemblent.

## Utilisation sur iPhone

1. Ouvrir l'URL GitHub Pages dans **Safari**.
2. Bouton Partager -> **Sur l'ecran d'accueil**.
3. Lancer depuis l'icone : la camera s'ouvre en plein ecran.

La camera exige HTTPS, ce que GitHub Pages fournit. Elle ne fonctionne pas
dans l'apercu Artifact, qui tourne en iframe sans permission camera.

## Fonctions

- Scan continu (`BarcodeDetector` natif si disponible, sinon jsQR).
- Alerte plein viseur quand rien n'est lu pendant 5 secondes.
- Lecture du numero imprime sous le QR (Tesseract, chiffres seuls),
  proposee a la validation et jamais ajoutee sans confirmation.
- Longueur attendue reglable : 11, 12, ou libre.
- Refus des doublons, bip et flash de confirmation.
- Export `.xlsx` : feuille de partage iOS, sinon lien de telechargement.
- Releve conserve dans le navigateur entre deux ouvertures.

## Fichiers

- `index.html` : toute l'application. **Seule source a editer.**
- `build.py` : regenere manifeste, service worker, icones, README et la
  variante Artifact depuis `index.html`.
- `vendor/` : jsQR (MIT), SheetJS (Apache-2.0), Tesseract.js (Apache-2.0).
"""
(ROOT / "README.md").write_text(readme, encoding="utf-8")

print("index.html    ", (ROOT / "index.html").stat().st_size, "octets")
print("artifact      ", ARTIFACT_OUT.stat().st_size, "octets")
print("ok")
