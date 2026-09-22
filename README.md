# Comlynk — landing page

Page de présentation de **Comlynk**, l'application iPhone qui enregistre les
cartes de visite que vous photographiez.

En ligne : <https://kesprit.github.io/comlynk/>

- Français : <https://kesprit.github.io/comlynk/fr/>
- English : <https://kesprit.github.io/comlynk/en/>

## Ce que c'est

Du HTML et du CSS statiques. Pas de framework, pas d'étape de build, pas de
dépendance à installer. Le seul JavaScript du site tient en une trentaine de
lignes et sert à deux choses : rediriger la racine vers la bonne langue, et
activer les boutons App Store le jour de la publication.

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

## Le jour de la publication sur l'App Store

Ouvrir `assets/js/site.js` et renseigner l'URL de la fiche App Store :

```js
var APP_STORE_URL = "https://apps.apple.com/app/idXXXXXXXXX";
```

C'est la seule ligne à modifier. Les quatre boutons (héro et appel final, dans
les deux langues) deviennent cliquables et les mentions « Bientôt sur l'App
Store » disparaissent.

## Points à relire

- **Les pages légales** (`confidentialite`, `conditions`, `assistance` et leurs
  équivalents anglais) sont un premier jet. Apple exige une URL de politique de
  confidentialité à la soumission : faites relire le texte avant.
- **Le canal d'assistance** pointe vers les issues GitHub de ce dépôt. À
  remplacer par une adresse e-mail si vous préférez.

## Crédits

Visuels et captures d'écran issus de la maquette du projet. Typographies
[Inter et Inter Tight](https://rsms.me/inter/), servies par Google Fonts.
