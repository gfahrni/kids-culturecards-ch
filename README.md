# Culture générale — base de données de cartes à collectionner

Base de données de contenu pour un système de **cartes à collectionner** destinées aux enfants en Suisse.
Chaque carte présente un sujet de culture générale : une image, un titre et une courte description de deux lignes.

## Structure

La base est organisée en **7 thèmes**, chacun divisé en **sous-thèmes** :

| N° | Thème | Sous-thèmes |
|----|-------|-------------|
| 1 | `drapeaux` | `suisse`, `europe`, `monde` |
| 2 | `capitales-chefs-lieux` | `suisse`, `europe`, `monde` |
| 3 | `montagnes` | `suisse`, `europe`, `monde` |
| 4 | `lacs-mers-oceans-rivieres` | `lacs`, `mers-et-oceans`, `fleuves-et-rivieres` |
| 5 | `monuments` | `suisse`, `europe`, `monde` |
| 6 | `merveilles-naturelles` | `suisse`, `monde` |
| 7 | `espace` | `systeme-solaire`, `au-dela`, `exploration` |

Un fichier Markdown correspond à une carte :
`<theme>/<sous-theme>/<theme-sous-theme-numero>_<nom>.md`

## Identifiant unique

L'identifiant d'une carte est de la forme `theme-sous-theme-numero` :

- `1-1-001` → thème 1 (`drapeaux`), sous-thème 1 (`suisse`), première carte.
- `3-2-004` → thème 3 (`montagnes`), sous-thème 2 (`europe`), quatrième carte.

La numérotation redémarre à `001` dans chaque sous-thème.

## Format d'une carte

```md
# Titre

Suisse

# Description

Croix blanche sur fond rouge, l'un des deux seuls drapeaux nationaux carrés.

# Image
```

La section `# Image` est volontairement laissée vide pour le moment : les visuels seront ajoutés plus tard.

## Slots non définis

Chaque sous-thème contient un fichier placeholder `041_undefined.md` qui marque un emplacement libre non encore défini. Il sert de modèle pour ajouter de futures cartes.

## Conventions

- Un dossier par thème, un dossier par sous-thème.
- Un fichier Markdown par carte.
- Pas d'emoji dans les fichiers.
- Noms de fichiers en minuscules, sans accents, séparés par des tirets.
