# Carte de voyage — Géorgie 2026

Carte interactive (style carnet de croquis) pour le voyage en Géorgie,
du **16 juin au 4 juillet 2026**. Tout tient dans `index.html`.

## Mettre en ligne sur GitHub Pages

1. Créez un dépôt GitHub et déposez‑y **tout le contenu de ce dossier**.
2. Dépôt → **Settings → Pages** → *Build and deployment* → **Deploy from a branch**,
   branche `main`, dossier `/ (root)`. Validez.
3. Au bout d'une minute, la carte est en ligne à l'adresse indiquée
   (`https://<votre-compte>.github.io/<nom-du-depot>/`).

Le fichier `.nojekyll` (déjà présent) évite que GitHub ignore certains dossiers.

## Les photos (« Voir les photos »)

Par défaut, le bouton **« Voir les photos »** va chercher les images **en direct
sur Wikimedia Commons** (il faut donc être en ligne).

Pour **embarquer les photos dans le dépôt** (et les avoir aussi hors ligne) :

```bash
python3 download_media.py
```

Le script télécharge les photos dans `photos/<lieu>/`, récupère leur crédit et
leur licence, et (re)génère `photos-data.js`. Ensuite, **committez** `photos/`
et `photos-data.js`. La page affichera en priorité ces photos locales.

> Aucune dépendance : juste Python 3. Les photos viennent de Wikimedia Commons
> (licences libres) ; le crédit et la licence s'affichent au clic sur chaque image.

## Les menus des restaurants

Les menus ne sont pas sur Wikimedia. Pour chaque restaurant, le bouton
**« Voir le menu & les photos »** ouvre la fiche **Google Maps** (menu + photos).

Si vous avez le **PDF** d'un menu, déposez‑le dans `menus/` en le nommant avec
l'identifiant du lieu, par ex. `menus/tb-hide.pdf`. Relancez `download_media.py`
(ou ajoutez l'entrée à la main dans `photos-data.js`, clé `window.MENUS`) : le
bouton proposera alors directement le PDF.

## Structure

```
index.html         La carte (à ouvrir / servir)
photos-data.js     Catalogue des photos & menus (généré par le script)
download_media.py  Télécharge les photos depuis Wikimedia Commons
photos/            Photos téléchargées (un sous-dossier par lieu)
menus/             Vos PDF de menus (optionnel)
```

## Crédits

Carte réalisée par **Georges SYSAATH** pour ses amis Daniel, Terence, Eddy,
Tatia, Andy, Caroline et Oriane.

Notes et avis : Google (indicatifs) · horaires et tarifs à reconfirmer sur place ·
1 € ≈ 3 GEL · photos : Wikimedia Commons.
