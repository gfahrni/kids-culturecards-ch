# Culture générale — base de données de cartes à collectionner

Base de données de contenu pour un système de **cartes à collectionner** destinées aux enfants en Suisse.
Chaque carte présente un sujet de culture générale : une image, un titre et une courte description de deux lignes.

La base compte **999 cartes**, réparties en **7 thèmes**.

## Structure

| N° | Thème | Sous-thèmes | Cartes |
|----|-------|-------------|-------:|
| 1 | `drapeaux` | `suisse`, `europe`, `monde` | 121 |
| 2 | `capitales-chefs-lieux` | `suisse`, `europe`, `monde` | 121 |
| 3 | `montagnes` | `suisse`, `europe`, `monde` | 106 |
| 4 | `lacs-mers-oceans-rivieres` | `lacs`, `mers-et-oceans`, `fleuves-et-rivieres` | 142 |
| 5 | `monuments` | `suisse`, `europe`, `monde` | 116 |
| 6 | `merveilles-et-espace` | `suisse`, `monde`, `espace` | 160 |
| 7 | `animaux` | `mammiferes`, `oiseaux`, `poissons`, `reptiles-et-amphibiens`, `insectes-et-araignees`, `races-suisses` | 233 |

Un fichier Markdown correspond à une carte :
`<theme>/<sous-theme>/<theme-sous-theme-numero>_<nom>.md`

## Identifiant unique

L'identifiant d'une carte est de la forme `theme-sous-theme-numero` :

- `1-1-001` → thème 1 (`drapeaux`), sous-thème 1 (`suisse`), première carte.
- `7-2-004` → thème 7 (`animaux`), sous-thème 2 (`oiseaux`), quatrième carte.

La numérotation est séquentielle et redémarre à `001` dans chaque sous-thème.

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

Chaque sous-thème contient un fichier placeholder `_undefined.md` portant le numéro du prochain emplacement libre.
Il sert de modèle pour ajouter de futures cartes (par exemple `1-1-028_undefined.md`).

## Contenu

- Drapeaux et chefs-lieux : les **26 cantons suisses** sont complets.
- Le thème 6 fusionne les **merveilles naturelles** et l'**espace**.
- Le thème 7 regroupe les **animaux suisses** : mammifères, oiseaux, poissons, reptiles, amphibiens, insectes, araignées et races d'élevage.
- Les principaux pays d'Europe et du monde sont traités du point de vue suisse.

## Conventions

- Un dossier par thème, un dossier par sous-thème.
- Un fichier Markdown par carte.
- Pas d'emoji dans les fichiers.
- Noms de fichiers en minuscules, sans accents, séparés par des tirets.
