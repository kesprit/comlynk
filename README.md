# Comlynk — landing page

Page de présentation de **Comlynk**, l'application iPhone qui enregistre les
cartes de visite que vous photographiez.

En ligne : <https://kesprit.github.io/comlynk/>

- Français : <https://kesprit.github.io/comlynk/fr/>
- English : <https://kesprit.github.io/comlynk/en/>

## Ce que c'est

Du HTML et du CSS statiques. Pas de framework, pas d'étape de build, pas de
dépendance à installer. Le seul JavaScript du site tient en quelques lignes
et sert à rediriger la racine vers la bonne langue.

## Structure

```
.
├── index.html              redirection vers /fr/ ou /en/ selon le navigateur
├── 404.html
├── favicon.png
├── fr/
│   ├── index.html          la landing page
│   ├── confidentialite.html
│   ├── conditions.html
│   └── assistance.html
├── en/
│   ├── index.html
│   ├── privacy.html
│   ├── terms.html
│   └── support.html
├── assets/
│   ├── css/site.css        feuille unique, variables CSS en haut
│   ├── js/site.js
│   └── img/                visuels extraits de la maquette
└── .nojekyll               GitHub Pages sert les fichiers tels quels
```

Les chemins sont tous relatifs : le site s'ouvre aussi bien depuis un serveur
local que directement dans un navigateur.

## Travailler dessus en local

```bash
python3 -m http.server 4321
```

Puis <http://localhost:4321/fr/>.

## Les deux langues

Chaque langue a sa propre page, indexable et partageable. Les deux fichiers ont
la même structure : pour modifier une section, la même modification s'applique
dans `fr/index.html` et dans `en/index.html`.

La racine redirige selon la langue du navigateur et mémorise le dernier choix
du visiteur (`localStorage`, clé `comlynk-lang`). Le lien `FR · EN` du header et
du footer permet de basculer à tout moment.

## Lien App Store

Comlynk est en ligne sur l'App Store :
<https://apps.apple.com/fr/app/comlynk/id6815378106>

Le lien est écrit en dur dans les boutons de `fr/index.html` et `en/index.html`
(héro et appel final). La page anglaise utilise l'URL sans code pays, qu'Apple
redirige vers le store du visiteur.

## Les visuels

Les captures d'écran viennent de l'iPhone, en pleine définition (601 px de large),
et sont affichées entre 250 et 324 px : elles restent nettes sur écran Retina.
Le châssis d'iPhone autour du héro et de la fiche avec plan est **dessiné en CSS**
(`.device`) plutôt que figé dans l'image, pour que tous les pixels servent à l'écran.

Deux captures manquent encore et restent en basse définition, extraites de la
maquette : `hard-scan.png` et `hard-record.png`, la carte noire à dorure de la
section « Fond noir, dorure, texte fin. ». À remplacer par des captures iPhone
au même format que les autres.

Les fiches affichent les coordonnées réelles des personnes dont les cartes ont
servi aux essais, désormais lisibles. À remplacer par des cartes fictives avant
toute campagne, ou à flouter.

## Points à relire

- **Les pages légales** (`confidentialite`, `conditions`, `assistance` et leurs
  équivalents anglais) sont un premier jet. Apple exige une URL de politique de
  confidentialité à la soumission : faites relire le texte avant.
- **Le canal d'assistance** pointe vers les issues GitHub de ce dépôt. À
  remplacer par une adresse e-mail si vous préférez.

## Crédits

Icône issue du projet iOS, captures d'écran prises sur iPhone. Typographies
[Inter et Inter Tight](https://rsms.me/inter/), servies par Google Fonts.
