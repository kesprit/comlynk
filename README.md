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
│   └── img/
│       ├── fr/             les captures en français
│       ├── en/             les mêmes en anglais
│       └── …               icône et images de partage, communes
├── tools/
│   ├── visuels.py          génère assets/img/{fr,en}
│   └── source/scene.jpg    la table, sans carte ni texte
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

Chaque langue a son propre jeu de captures : sur la page anglaise, l'interface
montrée dans les copies d'écran est en anglais. Les images font 601 px de large
et sont affichées entre 215 et 324 px, donc nettes sur écran Retina. Le châssis
d'iPhone du héro et de la fiche avec plan est **dessiné en CSS** (`.device`)
plutôt que figé dans l'image.

**Aucune donnée réelle.** Personnes, cartes, numéros, domaines et adresse sont
inventés. Les numéros utilisent la plage `06 39 98 xx xx` que l'ARCEP réserve à
la fiction.

### Régénérer les captures

```bash
python3 -m pip install Pillow
python3 tools/visuels.py
```

Le script écrit les deux dossiers et les deux images de partage. Tout le texte
affiché est regroupé dans le dictionnaire `T` en haut du fichier : pour corriger
une formulation ou ajouter une langue, c'est le seul endroit à toucher.

Deux techniques coexistent. Les écrans d'interface (liste, fiches) sont
redessinés avec SF Pro à partir des mesures relevées sur les captures
d'origine. Les écrans de scan partent de `tools/source/scene.jpg` — la photo
réelle de la table, vidée de sa carte et de ses textes : on y projette une
carte en perspective, rééclairée d'après la luminance de la scène, puis on
écrit les textes de l'appareil photo dans la langue voulue.

Le script a besoin des polices de macOS (SF Pro, Didot, Baskerville,
Avenir Next). Sur un autre système, adapter les chemins en haut du fichier.

## Points à relire

- **Les pages légales** (`confidentialite`, `conditions`, `assistance` et leurs
  équivalents anglais) sont un premier jet. Apple exige une URL de politique de
  confidentialité à la soumission : faites relire le texte avant.
- **Le canal d'assistance** pointe vers les issues GitHub de ce dépôt. À
  remplacer par une adresse e-mail si vous préférez.
- **Les textes anglais de l'interface** dans les captures (« Business cards »,
  « Recognised text », « Shutter »…) sont une traduction faite pour la page. Si
  l'application est un jour localisée, aligner le dictionnaire `T` de
  `tools/visuels.py` sur ses chaînes réelles.

## Crédits

Icône issue du projet iOS. Captures d'écran reconstruites avec des personnes
et des cartes fictives. Typographies
[Inter et Inter Tight](https://rsms.me/inter/), servies par Google Fonts.
