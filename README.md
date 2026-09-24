# Scanner Douze

Application web (PWA) qui lit des QR codes contenant un nombre a 12 chiffres
et exporte le releve en fichier Excel (.xlsx).

## Utilisation sur iPhone

1. Ouvrir l'URL GitHub Pages du depot dans **Safari**.
2. Bouton Partager -> **Sur l'ecran d'accueil**.
3. Lancer depuis l'icone : la camera s'ouvre en plein ecran.

La camera exige HTTPS, ce que GitHub Pages fournit.

## Fonctions

- Scan continu via la camera arriere (`BarcodeDetector` natif si disponible, sinon jsQR).
- Extraction de la suite de 12 chiffres, meme si le QR encode une URL.
- Refus des doublons (optionnel), bip et flash de confirmation.
- Saisie manuelle et lecture d'une photo en secours.
- Releve conserve dans le navigateur entre deux ouvertures.
- Export `.xlsx` (feuille de partage iOS) et copie CSV.

## Contenu

- `index.html` : toute l'application (structure, styles, logique).
- `vendor/jsQR.js` : decodeur QR (MIT).
- `vendor/xlsx.full.min.js` : SheetJS, ecriture du .xlsx (Apache-2.0).
- `sw.js` + `manifest.webmanifest` : installation sur l'ecran d'accueil et mode hors ligne.
