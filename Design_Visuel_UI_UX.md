# Design visuel — Systeme_Chargement V2026
### Identité KOHLER Co. · Jacob Delafon Africa — Département Coulage Vitreous, Tanger
### Poste d'atelier (opérateur debout) · Python 3.10+ / Tkinter / ttk · Interface en français

> Document de design UI/UX (aucun code). Les noms d'éléments `ttk` et les couleurs hex sont donnés comme spécification de référence pour l'implémentation.
> Toutes les valeurs de contraste citées sont calculées selon WCAG 2.x (rapport `(L1+0.05)/(L2+0.05)`).

---

## 0. Principes directeurs

1. **Lisible à 1 mètre, debout** : gros textes, gros boutons, contrastes élevés, peu de texte.
2. **Une seule action à la fois** : l'Accueil est le hub permanent ; les écrans d'action s'ouvrent au-dessus et « Fermer » ramène à l'Accueil.
3. **Cohérence absolue** : un gabarit d'écran unique (bandeau / corps / pied) garantit le même rendu partout.
4. **Feedback sans empilement** : jamais de popups en série ; un bandeau de statut discret et des badges de couleur.
5. **Clavier d'abord** : l'opérateur doit pouvoir tout faire sans souris (Entrée, Tab, raccourcis Fn).

---

## 1. Système de couleurs

### 1.1 Palette étendue (tokens)

| Rôle | Token | Hex | Usage |
|---|---|---|---|
| **Primaire** (marine) | `primary` | `#1B3A5C` | Bandeaux, boutons principaux, titres de fenêtre |
| Primaire — survol | `primary.hover` | `#14293F` | Bouton principal survolé |
| Primaire — appui | `primary.active` | `#0F1F30` | Bouton principal enfoncé |
| **Accent** (bleu) | `accent` | `#2E86C1` | Focus, liens, icônes, bordures actives, KOES |
| Accent — survol | `accent.hover` | `#2577AB` | Élément accent survolé |
| Accent — appui | `accent.active` | `#206A9C` | Élément accent enfoncé |
| **Or** | `gold` | `#C9A84C` | Filet décoratif, séparateurs, logo sur marine |
| **Fond** | `fond` | `#F0F4F8` | Fond général de l'application |
| Surface (carte) | `surface` | `#FFFFFF` | Panneaux, cartes, formulaires |
| Surface secondaire | `surface.alt` | `#E9EFF5` | Zones d'en-tête de formulaire, fonds de compteurs |
| Survole doux (ligne) | `hover.doux` | `#DDE7F0` | Ligne de tableau survolée |
| **Texte principal** | `texte` | `#172B3A` | Textes, labels, valeurs |
| Texte secondaire | `texte.muet` | `#5E6C78` | Aides, dates, sous-titres |
| Texte sur sombre | `texte.inverse` | `#FFFFFF` | Texte sur marine / badges |
| **Bordure légère** | `bordure` | `#C9D4E0` | Contours de champs au repos, cartes |
| Bordure focus | `bordure.focus` | `#2E86C1` | Anneau de focus (3 px) |
| Bordure désactivée | `bordure.off` | `#D0DAE4` | Champ désactivé |
| **Désactivé — texte** | `off.texte` | `#9AA6B2` | Texte désactivé (non soumis à 4,5:1) |
| **Désactivé — fond** | `off.fond` | `#E5EAF0` | Fond d'élément désactivé |
| **Danger** | `danger` | `#C53030` | Suppression, erreur bloquante |
| Danger — survol | `danger.hover` | `#A62424` | — |
| Danger — appui | `danger.active` | `#8B1D1D` | — |
| **Succès** | `succes` | `#2F855A` | Validation, statut Emaillage |
| **Attention** | `attention` | `#B45309` | Alertes, retard, statut Sortie |

### 1.2 Couleurs de statut (badges) — contraste ≥ 4,5:1 avec texte blanc

Les statuts sont des **pastilles pleines** (badge), texte blanc, coins légèrement arrondis (6 px), hauteur ~28 px.

| Statut | Hex | Contraste vs blanc | Justification |
|---|---|---|---|
| **Nouveau** — bleu | `#1F6FA0` | **5,47:1** ✓ | Bleu KOHLER assombri pour lisibilité |
| **Sortie** — orange | `#B45309` | **5,02:1** ✓ | Orange « four/atelier », lisible de loin |
| **Emaillage** — vert | `#2F855A` | **4,54:1** ✓ | Variante sûre `#287A52` = 5,26:1 pour petits textes |
| **Vide** — gris | `#6B7280` | **4,83:1** ✓ | Gris ardoise neutre |

> **Règle d'or sur les couleurs** :
> - **Or `#C9A84C`** : uniquement sur marine (`#1B3A5C` → 5,09:1) ou comme filet décoratif. **Jamais** de texte or sur fond clair (2,29:1, illisible).
> - **Accent `#2E86C1`** : jamais de texte blanc dessus pour du texte courant (3,97:1) ; l'accent sert au focus, aux icônes, aux liens et aux grands chiffres (≥ 3:1 autorisé pour UI/gros texte).
> - Tout texte **normal** repose sur du `#172B3A` (14,55:1) ou du blanc (≥ 11,6:1).

### 1.3 Correspondance avec `config.py` existant (à faire évoluer)

Le fichier `config.py` actuel contient déjà la base. Recommandation de mise à niveau :

- Conserver `COLOR_NAVY #1B3A5C`, `COLOR_GOLD #C9A84C`, `COLOR_BACKGROUND #F0F4F8`.
- Remplacer dans `STATUS_COLORS` :
  - `Nouveau` : `#2E86C1` → **`#1F6FA0`** (lisibilité badge).
  - `Sortie` : `#D97706` → **`#B45309`** (3,19 → 5,02:1).
  - `Vide` : `#718096` → **`#6B7280`** (4,02 → 4,83:1).
  - `Emaillage` : conserver `#2F855A` (4,54:1 ✓), variante `#287A52` pour petits textes.

---

## 2. Typographie et dimensions

### 2.1 Famille de police

| Ordre | Police | Note |
|---|---|---|
| 1 | **Segoe UI** | Défaut Windows, excellente lisibilité écran |
| 2 | Segoe UI Variable | Windows 11 |
| 3 | Arial / sans-serif | Repli universel |

- Graisses : `Normal` (400), `Semibold` (600) pour boutons/titres, `Bold` (700) pour titres de fenêtre.
- **Mettre en majuscules** les libellés de boutons de la grille d'accueil pour la scansion rapide.

### 2.2 Échelle typographique (atelier, opérateur debout)

| Élément | Taille | Graisse | Exemple |
|---|---|---|---|
| Titre de fenêtre (bandeau) | **26–30 px** | Bold | « Saisie Coulage » |
| Titre de section / accueil | 20–22 px | Bold | « Bienvenue » |
| Bouton de grille (accueil) | **18 px** | Semibold | « VOIR SORTIE [46] » |
| Bouton standard (action) | 15–16 px | Semibold | « Enregistrer » |
| Label de champ | 13–14 px | Semibold | « Référence » |
| Valeur / champ de saisie | 15–16 px | Normal | saisie du matricule |
| Cellule de tableau | 14–15 px | Normal | colonnes de la vue |
| Compteur « [46] » | 16 px | Semibold | chiffre du compteur |
| Petit texte (version, pied) | 12 px | Normal | « V2026 », horloge |

> Note Tkinter : les tailles ci-dessus sont des **pixels** de référence. En `ttk`/`font`, déclarer `size` en pixels (positif) plutôt qu'en points pour un rendu stable d'un poste à l'autre (l'échelle de l'écran change les points).

### 2.3 Cibles tactiles et dimensions

| Élément | Dimension minimale | Recommandation |
|---|---|---|
| Cible tactile (tout bouton/champ) | **48 × 48 px** | — |
| Bouton de grille (accueil) | 64 × 88 px | **88 px de haut** (1/3 de colonne) |
| Bouton d'action standard | 48 × 52 px | 52–56 px de haut |
| Champ de saisie | 44 px de haut | 48 px |
| Pastille de statut | 28 px de haut | largeur auto selon texte |
| Ligne de tableau | 44 px de haut | 48 px |

### 2.4 Espacements et marges (grille de 4 px)

| Token | Valeur | Usage |
|---|---|---|
| `space.xs` | 4 px | intra-élément |
| `space.s` | 8 px | entre label et champ |
| `space.m` | 16 px | gap de grille, padding des cartes |
| `space.l` | 24 px | padding des panneaux/bandeau |
| `space.xl` | 32 px | marges de l'accueil |

- Padding du bandeau : 16–20 px vertical.
- Gap de la grille d'accueil : 16 px.
- Marges latérales du contenu : 32 px.

---

## 3. Gabarit général (app_shell)

### 3.1 Structure plein écran

```
┌──────────────────────────────────────────────────────────────────────┐
│ BANDEAU SUPÉRIEUR (marine #1B3A5C, hauteur ~88 px)                    │
│  [KOHLER] [Jacob Delafon]  │  Titre / contexte  │  Nom · Matricule · Rôle │
│                            │                    │  [Auto Cull][Paramètre] │
│                            │                    │  [Menu][ChangerMDP]     │
├──────────────────────────────────────────────────────────────────────┤
│ ZONE CONTENU (fond #F0F4F8) — zone échangeable                        │
│   · Accueil (hub) OU contenu de l'écran actif                        │
├──────────────────────────────────────────────────────────────────────┤
│ BARRE INFÉRIEURE (marine #1B3A5C, hauteur ~56 px)                     │
│  [Déconnexion]                                       hh:mm:ss · V2026 │
└──────────────────────────────────────────────────────────────────────┘
```

- **Bandeau supérieur** : à gauche les deux logos côte à côte (KOHLER + Jacob Delafon, espace réservé **fixe**, voir §5.6) ; au centre le titre contextuel ; à droite l'identité de l'opérateur (`Nom`, `Matricule`, `Rôle` sur 2 lignes) puis les boutons d'en-tête.
- **Zone contenu** : une seule `Frame` remplie/détruite à chaque navigation.
- **Barre inférieure** : bouton **Déconnexion** à gauche (grand, lisible), horloge + version à droite.

### 3.2 Gestion des fenêtres (décision)

| Écran | Type | Comportement |
|---|---|---|
| **Login** | Fenêtre racine (avant shell) | Centrée, ~760×620, puis passage plein écran après connexion |
| **Accueil** | Contenu de l'écran racine | Hub permanent, **jamais fermé** |
| **Saisie Coulage** | `Toplevel` | Centré, **modal** (`grab_set`), ~900×560 |
| **Emaillage** | `Toplevel` | Centré, modal, ~720×420 |
| **Vues (Nouveau, Sortie, Emaillage, Vide, Complet, KOES, Archive)** | `Toplevel` | Centré, modal, ~1000×620 |
| **Utilisateurs** | `Toplevel` | Centré, modal, ~1000×620 |
| **Paramètres (Système / KEOS)** | `Toplevel` | Centré, modal, ~720×420 |
| **Changer MDP** | `Toplevel` | Centré, modal, ~560×420 |
| **Menu admin** | `Toplevel` | Centré, modal, ~520×480 |
| **Alertes (retard)** | `Toplevel` | Ouvert automatiquement à la connexion, modal |

**Règles** :
1. **Un seul `Toplevel` actif à la fois** : ouvrir un écran ferme (ou bloque) le précédent via `grab_set` + `wait_window`, afin d'éviter les fenêtres empilées.
2. **L'Accueil reste la racine** ; les écrans d'action sont des fenêtres secondaires (fidèle au modèle des formulaires Access V17).
3. **Déconnexion** ferme **tous** les `Toplevel`, réinitialise la session et revient au Login (ou quitte selon la règle métier).
4. **Gabarit unique** : chaque `Toplevel` est construit par une même fabrique (bandeau navy + corps blanc + pied d'actions), ce qui garantit l'uniformité (cf. §3.3).

### 3.3 Fabrique d'écran unique (pour uniformiser)

Chaque fenêtre secondaire est composée de trois zones standardisées :

1. **Bandeau** (marine) : titre à gauche (26–30 px), identité utilisateur + date/heure à droite (14 px).
2. **Corps** (blanc `#FFFFFF`, padding 24 px) : le contenu spécifique de l'écran.
3. **Pied d'actions** (fond `#F0F4F8`, bordure haute légère) : boutons alignés à **droite**, l'action principale à droite en marine, actions secondaires en gris/neutre.

Ordre des boutons du pied (convention) : `[Fermer/Annuler] … [Action principale]` — l'action principale **toujours à droite**.

---

## 4. Wireframes par écran

### 4.1 Login

```
┌───────────────────────────────────────────────────────────────┐
│  fond #F0F4F8 plein écran                                      │
│                                                                │
│        ┌──────────────────────────────────────────┐            │
│        │ ████████████████████████████████████████ │            │
│        │ █ [KOHLER]   Systeme de Chargement  [JDF]█ │ marine    │
│        │ ████████████████████████████████████████ │            │
│        │                                            │            │
│        │              BIENVENUE                     │ 22 px bold │
│        │   Suivi des wagons — Coulage Vitreous     │ 14 px muet │
│        │                                            │            │
│        │  Matricule      [______________________]   │            │
│        │  Mot de passe   [______________________]   │  (masqué ●)│
│        │                                            │            │
│        │  [  CONNEXION  ] [Changer MDP] [Annuler]   │            │
│        │                                            │            │
│        │                            V2026           │ 12 px muet │
│        └──────────────────────────────────────────┘            │
└───────────────────────────────────────────────────────────────┘
```

- **« Bienvenue »** en grand, sous-titre discret.
- **Connexion** : bouton marine pleine largeur (blanc). **Changer Mot De Passe** et **Annuler** : boutons neutres (contour).
- « Changer MDP » accessible **sans connexion** (ouvre l'écran §4.8).
- `V2026` en bas, discret.
- **Ordre de focus** : Matricule → Mot de passe → Connexion. **Entrée** dans Mot de passe = Connexion.
- Logo : les deux marques sur le bandeau marine, or `#C9A84C` autorisé ici (sur marine).

### 4.2 Accueil (hub)

```
┌══════════════════════════════════════════════════════════════════════┐
║ BANDEAU marine : [KOHLER][JDF]  Systeme de Chargement   YASSIN SAADI  ║
║                                                    KO05388 · Admin    ║
║ [Auto Cull]  [Paramètre]  [Menu]  [ChangerMDP]                        ║
╠══════════════════════════════════════════════════════════════════════╣
║ COMPTEURS (badges) :  Nouveau 12 · Sortie 46 · Emaillage 8 · Vide 120 ║
║                       Tout 186 · Archive 34        (rafraîchis /30 s)  ║
╠══════════════════════════════════════════════════════════════════════╣
║ Recherche wagon :  [____ n° ____]  [Rechercher]   →  ⚑ badge coloré   ║
║   résultat :  Statut · Tunnel · Référence · Cariste · Date            ║
║   label AutoSortie : « 14:05 — AutoSortie : 3 wagon(s) → Sortie »     ║
╠══════════════════════════════════════════════════════════════════════╣
║ GRILLE 3 colonnes — réorganisée selon rôle, SANS TROU                 ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 ║
║  │   SAISIE     │  │  EMAILLAGE   │  │ VOIR NOUVEAU │                 ║
║  │   (icône)    │  │   (icône)    │  │    [12]      │                 ║
║  └──────────────┘  └──────────────┘  └──────────────┘                 ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 ║
║  │ VOIR SORTIE  │  │  VOIR VIDE   │  │  VOIR TOUT   │                 ║
║  │    [46]      │  │    [120]     │  │    [186]     │                 ║
║  └──────────────┘  └──────────────┘  └──────────────┘                 ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 ║
║  │  EMAILLAGE   │  │   ARCHIVE    │  │              │                 ║
║  │   [vue]      │  │    [34]      │  │   (vide si   │                 ║
║  └──────────────┘  └──────────────┘  │  non requis) │                 ║
║                     ┌──────────────────────┐                          ║
║                     │         KOES         │   ← centré, dernier rang │
║                     └──────────────────────┘                          ║
╠══════════════════════════════════════════════════════════════════════╣
║ BARRE BAS : [Déconnexion]                                 hh:mm:ss    ║
╚══════════════════════════════════════════════════════════════════════╝
```

- **Grille dynamique** : la liste des boutons autorisés est calculée selon le rôle (voir §5.7) et **reconstruite** en flux pour ne **jamais** laisser de trou ; le **KOES** est ajouté **en dernier**, centré sur sa propre ligne.
- **Compteurs dans les libellés** : « VOIR SORTIE **[46]** » — chiffre en `texte.inverse` sur fond accent ou en gras.
- **Recherche wagon** : champ numérique (saisie filtrée chiffres uniquement), bouton + **Entrée** ; résultat en badge coloré selon le statut ; messages « N° wagon invalide » / « Wagon N introuvable » en rouge discret sous le champ.
- **Label AutoSortie** : texte discret (14 px, `texte.muet`), affiché 5 minutes puis masqué ; jamais de popup (règle métier §6).
- **Boutons d'en-tête** (`Auto Cull`, `Paramètre`, `Menu`, `ChangerMDP`) : visibilité selon rôle ; `Paramètre` **Admin uniquement** (contrôle côté code, pas seulement masqué).

### 4.3 Saisie Coulage

```
┌───────────────────────────────────────────────────────────────────────┐
│ BANDEAU marine : Saisie Coulage                [user] · dd/mm hh:mm:ss │
├───────────────────────────────────────────────────────────────────────┤
│  Référence   [ v combobox ______________________________ ]            │
│  Famille     [ Lavabo  (lecture seule, auto, fond grisé) ]            │
│  Qty         [ ____ ]    Coulage  [ ________ ]   Chariot [ ________ ]  │
│  Status      [ ● Nouveau  (badge bleu, auto, lecture seule) ]         │
│  Tunnel      (•) 1    ( ) 2    ( ) KEOS                                │
├───────────────────────────────────────────────────────────────────────┤
│  [Fermer] [Nouveau] [Enregistrer] [Voir Nouveau] [Voir Tout]          │
└───────────────────────────────────────────────────────────────────────┘
```

- **Référence** : `ttk.Combobox` avec auto-complétion ; **Famille** remplie automatiquement (lecture seule, fond `surface.alt`).
- **Status** : badge « Nouveau » **automatique**, non modifiable.
- **Tunnel** : boutons radio grands (48 px) — `1`, `2`, `KEOS` — obligatoire.
- **Ordre de focus / Entrée** : Référence → Qty → Coulage → Chariot → Tunnel → **Enregistrer**. « Entrée » passe au champ suivant ; sur le dernier champ, « Entrée » = Enregistrer.
- **Raccourcis** : `F2` Nouveau, `Échap` Fermer.
- Pied : `Enregistrer` à droite (marine), `Fermer`/`Nouveau`/`Voir Nouveau`/`Voir Tout` en neutres.

### 4.4 Emaillage

```
┌───────────────────────────────────────────────────────────────────────┐
│ BANDEAU marine : Emaillage                     [user] · dd/mm hh:mm:ss │
├───────────────────────────────────────────────────────────────────────┤
│  Nom Cariste  [ BAGGAR ABDESLAM   (lecture seule) ]                    │
│  Matricule    [ KE13583           (lecture seule) ]                    │
│  N° wagon     [ ______________ ]                                       │
├───────────────────────────────────────────────────────────────────────┤
│  [Enregistrer]   [Nouveau]   [Fermer]                                  │
└───────────────────────────────────────────────────────────────────────┘
```

- **NomCariste** et **Matricule** pré-remplis depuis la session (lecture seule, fond grisé).
- **N° wagon** : champ numérique ; **Entrée** = Enregistrer.
- Validation : vérifier `status = 'Sortie'` avant mise à jour ; rafraîchir la vue Sortie après.
- `Nouveau` vide le champ et remet le focus sur `N° wagon`.

### 4.5 Vues d'affichage (Nouveau, Sortie, Emaillage, Vide, Complet, KOES, Archive)

```
┌───────────────────────────────────────────────────────────────────────┐
│ BANDEAU marine : Vue Sortie                  [user] · dd/mm hh:mm:ss   │
│  (Vue Sortie uniquement)  Tunnel [ Tous v ] [Filtrer]                 │
├───────────────────────────────────────────────────────────────────────┤
│  Date_Chargement │ Reference │ Qty │ N° wagon │ Statut   │ Tunnel      │
│  ────────────────┼───────────┼─────┼──────────┼──────────┼──────────── │
│  2026-11-15 08:10│ 1002      │ 12  │ 105      │(Sortie)  │ 1           │
│  2026-11-15 09:02│ 1061      │ 8   │ 106      │(Sortie)  │ 2           │
│  … (tri par date croissante)                                              │
├───────────────────────────────────────────────────────────────────────┤
│  [Actualiser] [Fermer]        (Vue Sortie : [Emaillage] par ligne)     │
└───────────────────────────────────────────────────────────────────────┘
```

- **Tableau** `ttk.Treeview` : 6 colonnes — `Date_Chargement`, `Reference`, `Qty`, `no_wagon`, `status` (badge coloré), `Tunnel`. Tri **date croissante**.
- **Statut coloré** : tag de ligne ou colonne avec la couleur de statut (§1.2) + texte blanc.
- **Vue Sortie** : `Combobox` filtre Tunnel (`Tous / 1 / 2 / KEOS`) + bouton `Filtrer`, et un bouton **« Emaillage »** sur **chaque ligne**.
- **Vue KOES** : filtre tunnel `KEOS` forcé, pas de sélecteur.
- **États vides** : voir §5.4.
- **Raccourcis** : `F5` Actualiser, `Échap` Fermer, double-clic sur une ligne = action contextuelle (Emaillage en vue Sortie).

### 4.6 Utilisateurs

```
┌───────────────────────────────────────────────────────────────────────┐
│ BANDEAU marine : Gestion des utilisateurs                              │
├───────────────────────────────────────────────────────────────────────┤
│  Matricule [____]  Nom [__________]  MDP [____]  Confirmer [____]      │
│  Rôle      [ v combobox ________________ ]   [Ajouter]                │
├───────────────────────────────────────────────────────────────────────┤
│  Matricule │ Nom              │ MotDePasse │ Rôle              │ Act.  │
│  ──────────┼──────────────────┼────────────┼───────────────────┼─────── │
│  KE13583   │ BAGGAR ABDESLAM  │ ******     │ Cariste Coulage   │[Mod][Supp]│
│  KO05388   │ YASSIN SAADI     │ ******     │ Administrateur    │[Mod][Supp]│
├───────────────────────────────────────────────────────────────────────┤
│  [Fermer]                                                             │
└───────────────────────────────────────────────────────────────────────┘
```

- **Mot de passe masqué** (`******`) dans la liste ; jamais affiché en clair.
- **Modifier** : ouvre une **fenêtre dédiée** (même structure de formulaire) avec bouton `Annuler` ; les champs y sont pré-remplis.
- **Supprimer** : bouton rouge `danger` ; **confirmation** requise (action destructive uniquement).
- Taille de liste : hauteur ~ 8 lignes visibles, défilement vertical.

### 4.7 Paramètres (Système — tunnels 1 & 2 / Système KEOS)

```
┌───────────────────────────────────────────────────────────────────────┐
│ BANDEAU marine : Paramètres — Système (tunnels 1 & 2)                  │
├───────────────────────────────────────────────────────────────────────┤
│  Passage automatique  Nouveau  →  Sortie  après  N  heure(s)           │
│                                                                        │
│   Valeur actuelle :  12 h                                              │
│   Nouvelle valeur :  [ 12 ]      [ − ]  [ + ]     (pas de 1 h)         │
│   Limites : 1 à 168 h                                                   │
├───────────────────────────────────────────────────────────────────────┤
│  [Appliquer maintenant]   [Enregistrer]   [Fermer]                     │
└───────────────────────────────────────────────────────────────────────┘
```

- **Deux écrans identiques** : « Système » (clé `HeuresAutoSortie`, tunnels 1 & 2) et « Système KEOS » (clé `Cle_KEOS`).
- Boutons **`+` / `−`** (48×48 px) par pas de 1 h ; bornes **1–168** (boutons désactivés aux bornes).
- Texte exact : « Passage automatique Nouveau -> Sortie après N heure(s) ».
- **Appliquer maintenant** : déclenche le traitement immédiat (popup autorisé, action manuelle) ; **Enregistrer** : `UPDATE` sinon `INSERT` de la clé.
- Titre du bandeau change selon l'écran (« …— Système KEOS »).

### 4.8 Changer mot de passe

```
┌───────────────────────────────────────────────────────────────────────┐
│ BANDEAU marine : Changer mot de passe                                  │
├───────────────────────────────────────────────────────────────────────┤
│  Matricule           [ ______________ ]                                │
│  Ancien mot de passe [ ______________ ]  (masqué)                      │
│  Nouveau mot de passe[ ______________ ]  (masqué)                      │
│  Confirmation        [ ______________ ]  (masqué)                      │
├───────────────────────────────────────────────────────────────────────┤
│  [Valider]   [Annuler]                                                 │
└───────────────────────────────────────────────────────────────────────┘
```

- Depuis le Login : ouvert **sans connexion**. Depuis l'Accueil : matricule pré-rempli depuis la session.
- Vérification : ancien correct, nouveau = confirmation, longueur minimale (à confirmer).
- `Valider` à droite (marine), `Annuler` neutre.

### 4.9 Menu admin (centralisateur)

```
┌───────────────────────────────────────────────────────────────────────┐
│ BANDEAU marine : Menu administration                                   │
├───────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐                            │
│  │  Utilisateurs    │  │  Paramètres      │                            │
│  └──────────────────┘  └──────────────────┘                            │
│  ┌──────────────────┐  ┌──────────────────┐                            │
│  │  Auto Cull       │  │  Import CSV      │                            │
│  └──────────────────┘  └──────────────────┘                            │
├───────────────────────────────────────────────────────────────────────┤
│  [Fermer]                                                             │
└───────────────────────────────────────────────────────────────────────┘
```

- Grille 2 colonnes de grands boutons (88 px), centralise les fonctions d'administration.

### 4.10 Alertes de retard (ouverture à la connexion)

```
┌───────────────────────────────────────────────────────────────────────┐
│ BANDEAU danger (#C53030) :  ⚠ ATTENTION : 4 wagon(s) en retard !       │
├───────────────────────────────────────────────────────────────────────┤
│  Sortie depuis plus de 5 jours       (n)                              │
│   · Wagon 102 — 7 jours — Tunnel 1                                     │
│   · Wagon 118 — 6 jours — Tunnel 2                                     │
│  Emaillage depuis plus de 2 jours    (n)                              │
│   · Wagon 99 — 3 jours — Tunnel KEOS                                   │
├───────────────────────────────────────────────────────────────────────┤
│  [Fermer]                                                             │
└───────────────────────────────────────────────────────────────────────┘
```

- Bandeau **rouge** pour attirer l'œil, listes avec compteurs par catégorie.

---

## 5. Améliorations d'expérience utilisateur industrielle

### 5.1 Navigation clavier complète

| Touche | Comportement |
|---|---|
| `Tab` / `Maj+Tab` | Déplace le focus selon l'ordre déclaré (avant ⇄ arrière) |
| `Entrée` | Passe au **champ suivant** (ou valide si dernier champ) |
| `F2` | Nouveau (vider le formulaire) |
| `F5` | Actualiser (vues) |
| `Échap` | Fermer / Annuler |
| `Alt+D` | Déconnexion (à confirmer) |

**Ordres de focus recommandés** (définis explicitement par `focus_set` successifs) :
- Login : Matricule → Mot de passe → Connexion.
- Saisie : Référence → Qty → Coulage → Chariot → Tunnel → Enregistrer.
- Emaillage : N° wagon → Enregistrer.
- Vues : filtre (si présent) → tableau → Actualiser → Fermer.
- Utilisateurs : Matricule → Nom → MDP → Confirmer → Rôle → Ajouter.

### 5.2 Légende des couleurs de statut (permanente)

Une **légende compacte** est affichée dans le bandeau de l'Accueil (ou en bas du bandeau) :

```
● Nouveau (bleu)   ● Sortie (orange)   ● Emaillage (vert)   ● Vide (gris)
```

Elle est reproduite en en-tête de chaque vue d'affichage pour que l'opérateur n'ait jamais à mémoriser la correspondance.

### 5.3 Feedback visuel sans empilement

- **Jamais de popups en série** (AutoSortie, minuteurs) : utiliser le **label AutoSortie discret** sur l'Accueil (disparaît après 5 min).
- **Bandeau de statut** en bas des écrans d'action (petit texte vert/rouge) pour les confirmations/erreurs : « Wagon 105 → Emaillage ✓ », « N° wagon invalide ✗ ».
- **Bouton principal désactivé** tant que le formulaire est incomplet (ex. Tunnel non choisi).
- **Popup de confirmation uniquement** pour les actions destructives (Supprimer un utilisateur, Déconnexion, « Appliquer maintenant »).

### 5.4 États vides

- **Tableau vide** : message centré « Aucun wagon dans cet état » + icône, au lieu d'une grille vide.
- **Recherche wagon sans résultat** : « Wagon N introuvable » en rouge sous le champ.
- **Combobox sans référence** (table `reference` vide) : message d'aide « Aucune référence — importer le CSV ».
- **Compteurs à zéro** : afficher « [0] » (toujours visible, pas de trou).

### 5.5 Adaptation 24″ / écrans plus petits

- Taille de référence : **1920×1080** (24″). Plancher : **1280×720**.
- **Grille d'accueil** : largeur des colonnes en % de la zone contenu (3 colonnes fluides) ; les boutons se redimensionnent.
- **Vues** : `Treeview` avec **défilement** (vertical + horizontal) ; les colonnes se resserrent, la colonne « Statut » reste à largeur fixe.
- **Fenêtres secondaires** : dimensions exprimées en % de l'écran ou centrées avec `minsize` ; `minsize` ~ (900×540) pour Saisie/Vues.
- **Plein écran** : `root.attributes('-fullscreen', True)` ou état zoomé, avec repli fenêtré si l'écran < 1280 px.

### 5.6 Réservation d'espace pour les deux logos

- Le bandeau supérieur réserve une **zone fixe à gauche (~320 px)** pour les deux logos côte à côte : KOHLER puis Jacob Delafon, séparés par un filet or `#C9A84C` de 1 px.
- En l'absence de fichiers image, afficher des **libellés texte** (`KOHLER` + `Jacob Delafon Africa`) dans cette même zone pour ne pas casser la mise en page.
- Les logos sont **centrés verticalement**, hauteur maximale ~48 px.

### 5.7 Matrice des boutons de l'accueil par rôle

| Rôle | Saisie | Emaillage | Nouveau | Sortie | Emaillage(vue) | Vide | Tout | Archive | Utilisateurs | KOES |
|---|---|---|---|---|---|---|---|---|---|---|
| Admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Editeur | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| Cariste_Coulage | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ |
| Cariste_Emaillage | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| Utilisateur | — | — | ✓ | — | — | ✓ | ✓ | ✓ | — | ✓ |

> **Réorganisation sans trou** : la grille 3 colonnes est remplie en séquence avec les boutons autorisés ; `KOES` est toujours placé **en dernier, centré** sur sa propre ligne. Chaque accès réservé est **revérifié côté code**.

---

## 6. Récapitulatif des contrastes (contrôle qualité)

| Élément | Couleur | Fond | Contraste | Conformité |
|---|---|---|---|---|
| Texte principal | `#172B3A` | blanc | 14,55:1 | ✓ AA/AAA |
| Texte sur bandeau | blanc | `#1B3A5C` | 11,63:1 | ✓ AA/AAA |
| Texte secondaire | `#5E6C78` | blanc | 5,40:1 | ✓ AA |
| Badge Nouveau | blanc | `#1F6FA0` | 5,47:1 | ✓ AA |
| Badge Sortie | blanc | `#B45309` | 5,02:1 | ✓ AA |
| Badge Emaillage | blanc | `#2F855A` | 4,54:1 | ✓ AA |
| Badge Vide | blanc | `#6B7280` | 4,83:1 | ✓ AA |
| Danger | blanc | `#C53030` | 5,47:1 | ✓ AA |
| Or sur marine | `#C9A84C` | `#1B3A5C` | 5,09:1 | ✓ AA |
| Focus/Accent (UI) | `#2E86C1` | blanc | 3,97:1 | ✓ ≥3:1 (UI/gros texte) |
| Or sur blanc | `#C9A84C` | blanc | 2,29:1 | ✗ interdit pour texte |

---

*Document de design visuel — Systeme_Chargement V2026 · Identité KOHLER Co. / Jacob Delafon Africa. Prêt pour implémentation dans `config.py` et les écrans de `ui/`.*
