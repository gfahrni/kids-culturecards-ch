# Culture générale — cartes à collectionner

Base de **500 cartes** de culture générale destinées aux enfants en Suisse.
Chaque carte associe une **image**, un **titre** et une **courte description**.

Un site statique permet de parcourir la collection : onglets par thème,
sous-onglets par sous-thème, recherche instantanée et vue agrandie navigable.

## Thèmes

| N° | Thème | Sous-thèmes | Cartes |
|----|-------|-------------|-------:|
| 1 | `drapeaux` | `suisse`, `europe`, `monde` | 121 |
| 2 | `capitales-chefs-lieux` | `suisse`, `europe`, `monde` | 55 |
| 3 | `montagnes` | `suisse`, `europe`, `monde` | 35 |
| 4 | `lacs-mers-oceans-rivieres` | `lacs`, `mers-et-oceans`, `fleuves-et-rivieres` | 55 |
| 5 | `monuments` | `suisse`, `europe`, `monde` | 54 |
| 6 | `merveilles-et-espace` | `suisse`, `monde`, `espace` | 75 |
| 7 | `animaux` | `suisse`, `europe`, `monde` | 105 |
| | | **Total** | **500** |

## Arborescence

```
cartes-500/        un fichier Markdown par carte (source)
images/
  cartes-500/      une image WebP par carte (nom = identifiant de carte)
  _flags.json      source et licence des drapeaux
  _resolution.json source et licence des autres images
site/index.html    site généré (versionné pour aperçu local)
scripts/           outils Python (stdlib + Pillow)
.github/workflows/ déploiement GitHub Pages
```

## Format d'une carte

Un fichier par carte : `cartes-500/<theme>/<sous-theme>/<id>_<nom>.md`

```md
# Titre

Suisse

# Description

Croix blanche sur fond rouge, l'un des deux seuls drapeaux nationaux carrés.

# Image
```

L'identifiant a la forme `theme-sous-theme-numero` (ex. `1-1-001`), séquentiel et
redémarrant à `001` dans chaque sous-thème. La section `# Image` est laissée vide :
le visuel est associé par convention via `images/cartes-500/<id>.webp`.

## Images

Les images proviennent de **Wikimedia Commons** (photos, vignettes de Wikipédia)
et de **Wikidata** (propriété P41 pour les drapeaux), converties en **WebP**
(largeur max 1024 px, qualité 82). Les licences et auteurs sont conservés dans
`images/_flags.json` et `images/cartes-500/_manifest.csv`. Projet non commercial.

## Site

Aperçu local : ouvrir `site/index.html` (aucun serveur requis).

Régénérer après modification des cartes :

```
python scripts/build_site.py
```

Options : `--out <fichier>` et `--img <base-url>` (utiles pour la CI).

## Déploiement

Publié sur **GitHub Pages** via `.github/workflows/deploy.yml` à chaque `push`
sur `main`. La CI assemble le site et les images dans `_site/` puis déploie
l'artefact, sans dupliquer les images dans le dépôt.

Site : https://gfahrni.github.io/kids-culturecards-ch/

## Conventions

- Pas d'emoji dans les fichiers.
- Noms de fichiers en minuscules, sans accents, séparés par des tirets.
- Un dossier par thème, un dossier par sous-thème.
