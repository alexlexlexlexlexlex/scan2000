# SCAN2000

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
