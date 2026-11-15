# Document de Conception Architecturale et Données
## Système de Chargement — V2026 (Python 3.10+ / Tkinter / SQLite)

**Usine :** Jacob Delafon Africa (Groupe KOHLER) · Département Coulage Vitreous · Tanger
**Développeur :** YASSIN SAADI (KO05388)
**Objet :** reconstruction 100 % indépendante d'Access V17, base SQLite neuve (aucune migration).

> Ce document est la **référence de conception** : il fige l'architecture, le schéma, les règles de transition, la sécurité et les conventions. Il est écrit sans code (seuls des noms de fonctions/colonnes sont cités). Les points « À CONFIRMER » restent ouverts et doivent être tranchés par YASSIN avant la phase concernée.

---

## 0. Décisions actées (rappel)

- **Aucune migration Access** : base SQLite vierge, `reference` vide au départ (import CSV ultérieur des 167 références).
- **Aucune dépendance Access** (pas de `pyodbc`, pas de `.accdb`).
- **Stack stdlib uniquement** : `tkinter/ttk`, `sqlite3`, `datetime`, `hashlib`, `hmac`, `base64`, `os`. Packaging PyInstaller en fin de projet.
- **Interface et commentaires en français**, encodage UTF-8 (accents autorisés).
- **Peu de boîtes de confirmation** : uniquement pour les actions destructives.
- **Aucun SQL dans `ui/`** : tout accès aux données passe par `db.py` puis `services/`.

---

## 1. Architecture en couches (layered architecture)

```
┌─────────────────────────────────────────────────────────────┐
│  ui/            (présentation Tkinter, un fichier par écran) │
│     app_shell.py · login.py · accueil.py · saisie_coulage.py │
│     emaillage.py · affichages.py · parametres.py             │
│     utilisateurs.py                                          │
├─────────────────────────────────────────────────────────────┤
│  services/      (logique métier, permissions, règles)        │
│     authentification.py · chargements.py · permissions.py    │
│     auto_sortie.py · alertes.py · archivage.py               │
├─────────────────────────────────────────────────────────────┤
│  db.py          (accès données : connexion, schéma, requêtes)│
├─────────────────────────────────────────────────────────────┤
│  SQLite  (chargement.db)  — PRAGMA foreign_keys=ON, WAL      │
└─────────────────────────────────────────────────────────────┘

Couches transverses :
  config.py   (constantes, couleurs, chemins, rôles, libellés)
  session.py  (état de la session courante : utilisateur connecté)
```

### 1.1 Sens des dépendances (règle stricte)

- `ui/` → appelle `services/` **et** `config.py`, `session.py`. **N'importe jamais `db.py` ni `sqlite3`**.
- `services/` → appelle `db.py`, `config.py`, `session.py`. Ne touche jamais à Tkinter.
- `db.py` → appelle `config.py` (chemins) et `services/authentification.py` (hash). Ne connaît ni Tkinter ni la logique métier.
- `config.py` / `session.py` → n'importent rien du projet (aucune dépendance).

> **Conséquence directe de la règle « pas de SQL dans ui/ »** : un écran qui a besoin de données appelle une fonction d'un service (ex. `services.chargements.lister_nouveau()`), laquelle appelle `db.py`. L'écran ne voit jamais une chaîne SQL, un curseur ou un `sqlite3.Row` brut (il reçoit des `dict`/dataclasses).

### 1.2 Responsabilité de chaque fichier

| Fichier | Couche | Responsabilité |
|---|---|---|
| `main.py` | point d'entrée | Crée `tk.Tk`, applique le thème KOHLER, initialise la base, gère la navigation globale (login → accueil → déconnexion), déclenche la fenêtre `InitialisationAdmin` si aucun utilisateur n'existe. |
| `config.py` | transverse | Constantes : `APP_NAME`, `APP_VERSION` (« V2026 »), `COMPANY_NAME`, chemins (`BASE_DIR`, `DATA_DIR`, `DATABASE_PATH`), palette KOHLER (`COLOR_NAVY #1B3A5C`, `COLOR_BLUE #2E86C1`, `COLOR_GOLD #C9A84C`, `COLOR_BACKGROUND #F0F4F8`), couleurs par statut (`STATUS_COLORS`), liste et libellés des rôles. |
| `db.py` | données | Connexion (contexte `connexion()`), `PRAGMA`, création du schéma (`initialiser_base`), seed des `parametres` par défaut, et **toutes** les requêtes (lectures/écritures/agrégats). Seul endroit où du SQL existe. |
| `session.py` | transverse | `UtilisateurConnecte` (dataclass : `id_cariste`, `matricule`, `nom_cariste`, `role`) et `Session` (ouvrir/fermer, `est_connectee`). Objet singleton `session`. |
| `services/authentification.py` | service | Hash/verification PBKDF2 (`hacher_mot_de_passe`, `verifier_mot_de_passe`) + règles de robustesse (longueur minimale). |
| `services/permissions.py` | service | **Source unique de vérité** des autorisations : `AUTORISATIONS` (dictionnaire action → ensemble de rôles) et `est_autorise(role, action)`. |
| `services/chargements.py` | service | Règles métier des chargements : création (saisie), réutilisation de `no_wagon`, transitions `Sortie→Emaillage`, `Emaillage→Vide`, lectures filtrées, recherche rapide wagon, compteurs. |
| `services/auto_sortie.py` | service | Logique du passage automatique `Nouveau→Sortie` : lecture des délais dans `parametres`, calcul de la date limite en Python, UPDATE conditionnel, retour du nombre de wagons basculés. **Aucun popup.** |
| `services/alertes.py` | service | Détection des retards (Sortie > 5 j, Emaillage > 2 j), construction des deux listes et des compteurs, calcul des jours d'écart. |
| `services/archivage.py` | service | Auto Cull / archivage des wagons `Vide` vers `archive` (structure prête, comportement « à confirmer »). |
| `ui/app_shell.py` | présentation | Canevas de navigation commun : plein écran, en-tête (nom/matricule/rôle/logos), remplacement d'écran, barre « Déconnexion ». |
| `ui/login.py` | présentation | Écran « Bienvenue » (matricule + mot de passe, Connexion / Changer MDP / Annuler, étiquette V2026), `InitialisationAdmin` (premier lancement), `ChangementMotDePasse`. |
| `ui/accueil.py` | présentation | Grille de boutons 3 colonnes réorganisée selon le rôle (sans trou), bouton KOES centré, compteurs rafraîchis toutes les 30 s, zone de recherche wagon colorée, label discret AutoSortie, boutons Auto Cull / Paramètre / Menu / ChangerMDP. |
| `ui/saisie_coulage.py` | présentation | Formulaire Saisie Coulage (Référence combobox, Famille auto lecture seule, Qty, Coulage, Chariot, Status=Nouveau auto, Tunnel 1/2/KEOS), navigation Entrée → champ suivant, boutons Fermer/Nouveau/Enregistrer/Voir Nouveau/Voir Tout. |
| `ui/emaillage.py` | présentation | Écran Émaillage : NomCariste + Matricule lecture seule, champ `no_wagon`, boutons Enregistrer/Nouveau/Fermer (transition Sortie→Emaillage). |
| `ui/affichages.py` | présentation | Vues Nouveau / Sortie / Emaillage / Vide / Complet / KOES / Archive : liste (Date, Référence, Qty, no_wagon, status coloré, Tunnel) triée par date croissante ; vue Sortie avec filtre Tunnel et bouton « Emaillage » par ligne. |
| `ui/parametres.py` | présentation | Deux écrans (Système tunnels 1/2 et Système KEOS) : valeur actuelle + nouvelle, boutons +/− par pas de 1 h, limites 1–168 h, bouton « Appliquer maintenant ». |
| `ui/utilisateurs.py` | présentation | Gestion utilisateurs : formulaire d'ajout (Matricule, Nom, MDP, Confirmer, Rôle), liste avec MDP masqué ****, Modifier/Supprimer par ligne, fenêtre de modification. |

### 1.3 Convention de typage et de retour des données

Le projet **n'utilise pas d'objets « ligne SQL » exposés à l'UI**. Convention sur trois niveaux :

1. **`db.py` (données)** — retourne des types simples et dict-like :
   - lecture unique → `sqlite3.Row` (dict-like, via `row_factory = sqlite3.Row`) ou `dict`, `None` si introuvable ;
   - liste → liste de `Row`/`dict` ;
   - agrégat → scalaire (`int`, `str`) ;
   - écriture → identifiant créé (`id_chargement`, `id_detail`) ou `None`.
   `db.py` **ne lève pas d'exception métier** (les violations de règles sont du ressort des services).

2. **`services/` (métier)** — retourne des **dataclasses du domaine** (ex. `Chargement`, `DetailChargement`) ou un objet résultat dédié aux mutations : `Resultat(ok: bool, message: str, donnees: …)`. Il **lève des exceptions typées** pour les violations : `AccesRefuse`, `ErreurMetier` (ex. « wagon introuvable ou pas en Sortie »), `SaisieInvalide`.

3. **`ui/` (présentation)** — appelle les services, **intercepte** `AccesRefuse`/`ErreurMetier`/`SaisieInvalide` pour afficher une `messagebox` (action manuelle), et consomme les dataclasses/dicts. Il **n'importe jamais `sqlite3` ni `db`**.

> Ce choix (dataclasses + `Resultat` + exceptions typées) est préféré aux `tuple` : il est auto-documenté, évite les erreurs d'ordre de colonnes et rend les contrôles de permission explicites dans chaque service.

---

## 2. Modèle de données SQLite final

### 2.1 PRAGMA obligatoires

- `PRAGMA foreign_keys = ON` : activé **à chaque connexion** (non persistant). Le contexte `connexion()` de `db.py` l'exécute systématiquement avant toute requête.
- `PRAGMA journal_mode = WAL` : **persistant** (réglé une fois à l'initialisation). Apporte la sécurité en cas d'arrêt brutal (usine, coupure secteur) et évite les verrous bloquants. Compagnon recommandé : `PRAGMA synchronous = NORMAL` (équilibre performance/intégrité, adapté au WAL).
- Conséquence pratique : WAL crée des fichiers `-wal` et `-shm` à côté de `chargement.db` ; ils doivent être inclus dans toute sauvegarde du fichier.

### 2.2 Table `utilisateurs`

| Colonne | Type | Contraintes | Sémantique |
|---|---|---|---|
| `id_cariste` | INTEGER | `PRIMARY KEY AUTOINCREMENT` | Identifiant interne. |
| `matricule` | TEXT | `UNIQUE NOT NULL` | Matricule cariste (ex. `KO05388`). Normalisé en majuscules + `strip` à l'écriture. |
| `nom_cariste` | TEXT | `NOT NULL` | Nom complet. |
| `mot_de_passe` | TEXT | `NOT NULL` | **Hash PBKDF2-SHA256 avec sel**, format auto-descriptif `pbkdf2_sha256$iterations$sel_b64$hash_b64`. Jamais en clair. |
| `role` | TEXT | `NOT NULL CHECK(role IN ('Admin','Editeur','Cariste_Coulage','Cariste_Emaillage','Utilisateur'))` | Rôle applicatif. |

> Extension recommandée (optionnelle, sans impact sur le schéma actuel) : colonne booléenne `doit_changer_mdp` (0/1) pour forcer le changement de mot de passe temporaire au premier login. À décider en phase Utilisateurs.

### 2.3 Table `reference`

| Colonne | Type | Contraintes | Sémantique |
|---|---|---|---|
| `id_reference` | INTEGER | `PRIMARY KEY AUTOINCREMENT` | Identifiant interne. |
| `reference` | TEXT | `UNIQUE NOT NULL` | Code article (ex. `1002`, `4383 grés`, `GE`). |
| `famille` | TEXT | (nullable) | Famille produit (ex. `Lavabo`, `Cuvette robots`). Normalisée en casse « Titre ». |

### 2.4 Table `chargement`

| Colonne | Type | Contraintes | Sémantique |
|---|---|---|---|
| `id_chargement` | INTEGER | `PRIMARY KEY AUTOINCREMENT` | Identifiant interne du wagon chargé. |
| `no_wagon` | INTEGER | `NOT NULL` | Numéro de wagon (entier). |
| `status` | TEXT | `NOT NULL CHECK(status IN ('Nouveau','Sortie','Emaillage','Vide'))` | État courant (machine à états, §3). |
| `tunnel` | TEXT | `NOT NULL CHECK(tunnel IN ('1','2','KEOS'))` | Tunnel de séchage ; pilote le canal AutoSortie. |
| `date_chargement` | TEXT | `NOT NULL` (format `YYYY-MM-DD HH:MM:SS`) | **Heure du dernier événement d'état** (création puis chaque transition). Voir §2.8. |
| `id_cariste` | INTEGER | `NULL` + `REFERENCES utilisateurs(id_cariste) ON DELETE SET NULL` | Cariste ayant créé/dernier modifié le wagon. |
| `coulage` | TEXT | `NULL` | Emplacement/poste de coulage (à confirmer, §2.9). |
| `chariot` | TEXT | `NULL` | N° de chariot / emplacement (à confirmer, §2.9). |

> **Alignement requis avec le cahier des charges** : le squelette actuel contient `date_coulage` (à la place de `coulage`) et n'a pas `chariot`. Il faut renommer `date_coulage → coulage` et ajouter `chariot` pour être conforme.

### 2.5 Table `detail_chargement` (relation 1-N)

| Colonne | Type | Contraintes | Sémantique |
|---|---|---|---|
| `id_detail` | INTEGER | `PRIMARY KEY AUTOINCREMENT` | Identifiant de ligne. |
| `id_chargement` | INTEGER | `NOT NULL REFERENCES chargement(id_chargement) ON DELETE CASCADE` | Wagon parent. La suppression du wagon supprime ses lignes. |
| `id_reference` | INTEGER | `NOT NULL REFERENCES reference(id_reference)` | Référence chargée. `ON DELETE` par défaut (`NO ACTION`) : on ne supprime pas une référence encore référencée. |
| `quantite` | INTEGER | `NOT NULL CHECK(quantite > 0)` | Quantité pour cette référence. |

> La famille n'est **pas** stockée ici : elle se déduit par jointure vers `reference`. On évite la redondance et la désynchronisation.

### 2.6 Table `archive` (structure prête, comportement différé)

Le cahier des charges décrit « structure de `chargement` + `reference, famille, quantite` + `date_archivage` ». On adopte une **table aplatie : une ligne par (wagon × référence)** — c'est la forme la plus simple et suffisante pour la vue Archive et les futurs rapports.

| Colonne | Type | Contraintes | Sémantique |
|---|---|---|---|
| `id_archive` | INTEGER | `PRIMARY KEY AUTOINCREMENT` | Identifiant d'archive. |
| `no_wagon` | INTEGER | `NOT NULL` | Wagon archivé. |
| `status` | TEXT | `NOT NULL CHECK(status IN ('Nouveau','Sortie','Emaillage','Vide'))` | Statut au moment de l'archivage (normalement `Vide`). |
| `tunnel` | TEXT | `NOT NULL` | Tunnel d'origine. |
| `date_chargement` | TEXT | `NOT NULL` | Dernière date d'état au moment de l'archivage. |
| `date_archivage` | TEXT | `NOT NULL` | Horodatage de l'archivage. |
| `id_cariste` | INTEGER | `NULL` | Auteur de l'archivage (référence lâche, pas de FK forte pour ne pas bloquer la purge). |
| `coulage` | TEXT | `NULL` | Conservé pour traçabilité. |
| `chariot` | TEXT | `NULL` | Conservé pour traçabilité. |
| `reference` | TEXT | `NOT NULL` | Référence (dénormalisée pour lecture directe). |
| `famille` | TEXT | `NULL` | Famille (dénormalisée). |
| `quantite` | INTEGER | `NOT NULL` | Quantité archivée. |

> Alternative (non retenue par défaut) : deux tables normalisées `archive` + `detail_archive` miroir de `chargement`/`detail_chargement`. Elle préserve mieux la 1-N, mais la forme aplatie ci-dessus correspond exactement à l'indication du cahier des charges et à l'affichage demandé. Si un besoin de statistiques fines apparaît, la migration est simple.

### 2.7 Table `parametres` (clé → valeur)

| Colonne | Type | Contraintes | Sémantique |
|---|---|---|---|
| `cle` | TEXT | `PRIMARY KEY` | Clé de paramètre (`HeuresAutoSortie`, `Cle_KEOS`). |
| `valeur` | TEXT | `NOT NULL` | Valeur texte (convertie en `int` à l'usage). |
| `description` | TEXT | (nullable) | Libellé humain. |

**Valeurs par défaut (seed à l'init)** : `HeuresAutoSortie = 12`, `Cle_KEOS = 12`, insérées en `INSERT OR IGNORE`.

### 2.8 Sémantique précise de `date_chargement`

La colonne, malgré son nom, est **« date/heure du dernier événement d'état »** : elle est posée à `now` à la saisie (création) puis **réécrite à chaque transition** (Sortie→Emaillage, Emaillage→Vide). C'est ce que permet l'AutoSortie : pour un wagon `Nouveau`, `date_chargement` est son heure de création, comparée à la date limite.

**Point crucial de format** : stocker la valeur en **`YYYY-MM-DD HH:MM:SS`** rend la **comparaison lexicographique identique à la comparaison chronologique**. On peut donc écrire, côté SQL, `date_chargement <= ?` (limite calculée en Python) **sans parse ni conversion**, ce qui est rapide et indexable. Fuseau : heure locale (Africa/Casablanca, sans changement d'heure) — suffisant pour un poste local ; si le multi-postes est un jour envisagé, passer à un format ISO avec fuseau (migration à prévoir).

### 2.9 Sémantique de `coulage` et `chariot` (emplacement « à confirmer »)

Les deux champs sont vus dans `Frm_Saisie` et marqués « emplacement à confirmer ». **Recommandation (option retenue)** :

- **`coulage`** = **poste / ligne de coulage** (texte libre, exemple `Ligne 3`, `Poste A`). Contexte : département *Coulage* Vitreous — c'est un repère humain de localisation du moulage.
- **`chariot`** = **identifiant du chariot** porteur du wagon (texte libre, ex. `CH-12`), c'est-à-dire le support mobile, pas un emplacement fixe.

**Justification** :
1. Ni l'un ni l'autre n'est utilisé par la machine à états ni par l'AutoSortie (seul `tunnel` et `status` le sont). Ils sont **descriptifs/traçabilité**, donc **NULL autorisé, sans CHECK ni UNIQUE**, pour ne jamais bloquer la saisie tant que leur sémantique n'est pas confirmée.
2. Les laisser en **texte libre nullable** évite toute migration si on décide plus tard d'en faire des listes déroulantes : on pourra ajouter une table `emplacements` (ou `chariots`) sans casser les enregistrements existants.
3. S'ils avaient un rôle de routage, ils auraient été modélisés comme `tunnel` (CHECK contraint). Leur caractère optionnel et « à confirmer » indique une donnée de contexte.

**À confirmer** (avant la phase 2) : faut-il en faire des **combobox à vocabulaire contrôlé** ou un simple **champ libre** ? Dans les deux cas le schéma ci-dessus reste valide.

### 2.10 Index recommandés

| Index | Table / colonnes | Justification |
|---|---|---|
| (implicite) `UNIQUE(matricule)` | `utilisateurs` | Unicité des matricules. |
| (implicite) `UNIQUE(reference)` | `reference` | Déduplication à l'import. |
| `idx_chargement_status_date` | `chargement(status, date_chargement)` | **Critique** : sert à la fois l'AutoSortie (`WHERE status='Nouveau' AND date_chargement <= limite`) et les vues/compteurs par statut. |
| `idx_chargement_no_wagon` | `chargement(no_wagon)` | Recherche rapide wagon + règle de réutilisation. |
| `idx_chargement_status_tunnel` | `chargement(status, tunnel)` | Filtre Tunnel de la vue Sortie. |
| `idx_detail_chargement` | `detail_chargement(id_chargement)` | Jointure/agrégation des références d'un wagon (JOIN 1-N). |
| `idx_detail_reference` | `detail_chargement(id_reference)` | Recherche inverse (optionnel). |
| `idx_archive_no_wagon` | `archive(no_wagon)` | Consultation d'un wagon archivé. |
| `idx_archive_date_archivage` | `archive(date_archivage)` | Purge/rapports chronologiques. |

---

## 3. Machine à états (cycle Nouveau → Sortie → Emaillage → Vide)

```
        ┌───────────┐   AutoSortie (timer)   ┌────────┐  Émaillage  ┌───────────┐  Vide  ┌──────┐
(saisie)│  Nouveau  │ ──────────────────────►│ Sortie │────────────►│ Emaillage │───────►│ Vide │
   ────►│           │                        │        │             │           │        │      │
        └───────────┘                        └────────┘             └───────────┘        └──────┘
                                                                                        (Auto Cull,
                                                                                         à confirmer)
                                                                                             │
                                                                                             ▼
                                                                                         archive
```

### 3.1 Tableau des transitions

| # | Transition | Déclencheur | Acteur | Garde (vérification avant) | Effet |
|---|---|---|---|---|---|
| T0 | — → `Nouveau` | Saisie Coulage · bouton « Enregistrer » | Cariste_Coulage / Editeur / Admin | tunnel obligatoire ; ≥ 1 détail ; règle de réutilisation de `no_wagon` respectée | `INSERT chargement` + `INSERT detail_chargement` (transaction), `date_chargement = now`. |
| T1a | `Nouveau` → `Sortie` | Timer AutoSortie (30 s), tunnel `1`/`2` | Système | `status='Nouveau'` ET `tunnel IN ('1','2')` ET `date_chargement <= now − HeuresAutoSortie` | `UPDATE` conditionnel, `date_chargement = now`. |
| T1b | `Nouveau` → `Sortie` | Timer AutoSortie (30 s), tunnel `KEOS` | Système | idem avec `tunnel='KEOS'` et `Cle_KEOS` | idem. |
| T2 | `Sortie` → `Emaillage` | Écran Emaillage (saisie `no_wagon`) **ou** bouton « Emaillage » d'une ligne de la vue Sortie | Cariste_Emaillage / Editeur / Admin | `status='Sortie'` | `UPDATE`, `date_chargement = now`, rafraîchissement de la liste. |
| T3 | `Emaillage` → `Vide` | Écran/bouton **à confirmer** (§4 de 12.txt) | à confirmer | `status='Emaillage'` | `UPDATE`, `date_chargement = now`. |
| T4 | `Vide` → `archive` | Auto Cull **à confirmer** (archivage vs détection) | Système / Admin | `status='Vide'` | `INSERT archive` puis `DELETE chargement` (CASCADE des détails). |

### 3.2 Vérification de l'état avant chaque transition (garde)

Chaque transition **relit l'état en base** avant d'agir, puis applique un **UPDATE conditionnel** (clause `WHERE` portant sur le statut attendu) et **contrôle `rowcount`** :

- **Transition manuelle (T2, T3)** : si `rowcount == 0`, le wagon est introuvable **ou** n'est pas dans l'état attendu → lever `ErreurMetier` (« Wagon N introuvable ou pas en Sortie ») → `messagebox` (action manuelle, donc popup autorisé).
- **Transition automatique (T1a/T1b)** : même principe, mais **sans popup** (cf. §4) — le nombre de lignes mises à jour alimente uniquement le label discret.

Ce motif « UPDATE … WHERE status = attendu » garantit l'**atomicité du contrôle** : même en cas de double-clic ou de chevauchement timer/manuel, un seul des deux gagne (l'autre reçoit `rowcount == 0`). C'est la défense principale contre un wagon basculé deux fois.

### 3.3 `date_chargement` mise à jour à chaque transition

T0, T2, T3 écrivent `date_chargement = now` (horodatage local `YYYY-MM-DD HH:MM:SS`). T1a/T1b écrivent aussi `date_chargement = now` **lors du basculement** (la nouvelle heure de sortie devient la nouvelle référence). Conséquence (documentée §2.8) : `date_chargement` = heure du **dernier** événement, pas l'heure de création d'origine.

### 3.4 Règle de réutilisation de `no_wagon` (À CONFIRMER)

Comportement de l'ancienne version, repris à valider :

1. **`no_wagon` existe en `Nouveau`** → **bloquer** avec message (« Wagon N déjà chargé, en attente de sortie »). Aucune écriture.
2. **`no_wagon` existe en `Sortie`/`Emaillage`/`Vide`** → **supprimer l'ancien enregistrement** (et ses détails via CASCADE) puis **créer un nouveau `Nouveau`**.

**Risques identifiés** :
- **Perte de traçabilité** : l'historique du wagon précédent disparaît (sauf s'il est archivé avant suppression).
- **Erreur opérateur** : une faute de frappe sur un `no_wagon` actif écrase un wagon en cours de cycle.
- **Incohérence de compteurs** : le remplacement change les compteurs `Sortie/Emaillage/Vide` sans transition explicite.

**Recommandation** : puisque c'est une **action destructive**, la confirmer par `messagebox` (conforme à la règle « popup uniquement pour les actions destructives ») et, idéalement, **archiver l'ancien wagon avant suppression**. À trancher avec YASSIN avant la phase 2.

---

## 4. Conception d'AutoSortie et du minuteur

### 4.1 Pourquoi `root.after(30000, …)` dans le fil principal plutôt que `threading`

1. **Tkinter n'est pas thread-safe** : toute interaction avec un widget (même lire une variable) depuis un thread secondaire risque des plantages non déterministes. Le label discret AutoSortie, les compteurs d'accueil et le rafraîchissement des vues sont tous des widgets.
2. **SQLite en fil unique est plus simple** : un thread secondaire imposerait une connexion dédiée + verrous, pour un bénéfice nul ici.
3. **Le travail périodique est minuscule** : quelques `SELECT`/`UPDATE` indexés (cf. §2.10), donc < 50 ms. Exécuté dans la boucle d'événements entre deux `mainloop` itérations, il **ne gèle pas** l'interface.
4. **`after` se ré-arme tout seul** : le callback se reprogramme (`root.after(30000, …)` en fin de tick), ce qui boucle sans `while True` ni thread.

### 4.2 Éviter le gel de l'interface

- Callback **court et borné** : uniquement des requêtes indexées, aucune boucle Python lourde, aucun accès réseau.
- Le calcul lourd (date limite) est un simple `datetime.now() - timedelta(hours=h)`, puis **formatage en chaîne** — le SQL ne fait qu'une comparaison de chaînes indexée.
- Les compteurs d'accueil sont rafraîchis dans le **même** tick (30 s), pas plus souvent.

### 4.3 Deux canaux séparés

| Canal | Tunnels concernés | Clé `parametres` |
|---|---|---|
| 1 | `1` et `2` | `HeuresAutoSortie` |
| 2 | `KEOS` | `Cle_KEOS` |

Les deux sont **relus à chaque exécution** (`parametres` → `int`), jamais mis en cache. Ainsi un changement dans l'écran Paramètres prend effet au tick suivant (≤ 30 s). Chaque canal produit son propre `UPDATE` conditionnel et son propre compte de basculement ; le label peut additionner les deux.

### 4.4 Calcul de la date limite **en Python**, comparaison **dans le WHERE**

- Python : `limite = datetime.now() - timedelta(hours=heures)` puis `limite_texte = limite.strftime('%Y-%m-%d %H:%M:%S')`.
- SQL : `UPDATE chargement SET status='Sortie', date_chargement=? WHERE status='Nouveau' AND tunnel IN ('1','2') AND date_chargement <= ?`.
- **Pourquoi ça marche** : le format ISO `YYYY-MM-DD HH:MM:SS` trie dans l'ordre chronologique (lexicographique = chronologique, §2.8), donc aucune conversion SQL de date n'est nécessaire — l'index `idx_chargement_status_date` est pleinement exploité.

### 4.5 « Pas de popup depuis le minuteur » — label discret

- Aucun `messagebox` dans le tick (il s'empilerait et interromprait l'opérateur debout).
- Après un tick ayant basculé `N > 0` wagons, un **label** de l'accueil affiche : `"hh:mm - AutoSortie : N wagon(s) -> Sortie"`.
- Ce label **disparaît seul après 5 minutes** : au moment de l'affichage, on arme un `root.after(300000, …)` qui efface le texte ; si un nouveau tick survient avant l'échéance, on annule/relance le minuteur d'effacement.
- Toute **erreur** dans le tick est **avalée silencieusement** (consignée en log, jamais en popup) pour ne pas perturber la production.

---

## 5. Modèle de sécurité

### 5.1 Hash des mots de passe

- **PBKDF2-HMAC-SHA256** avec **sel aléatoire de 16 octets** par utilisateur et **310 000 itérations** (valeur déjà en place dans `services/authentification.py` ; on peut monter à 600 000 si les postes le permettent — à valider au packaging).
- Format stocké **auto-descriptif** : `pbkdf2_sha256$iterations$sel_b64$hash_b64`, pour pouvoir revérifier et migrer plus tard.
- **Comparaison en temps constant** (`hmac.compare_digest`) contre les attaques temporelles.
- **Jamais de clair** : les valeurs du fichier source `000000` / `admin123` ne sont **pas** reprises telles quelles (voir §8.2).
- Politique de robustesse : mot de passe ≥ 8 caractères (déjà appliqué dans `login.py`), confirmation identique obligatoire.

### 5.2 Initialisation du premier Admin

- Au premier lancement, si `utilisateurs` est vide, la fenêtre `InitialisationAdmin` s'ouvre : matricule **`KO05388`** figé, nom `YASSIN SAADI`, mot de passe **choisi à ce moment** (≥ 8 caractères), rôle `Admin`.
- L'Admin n'est **pas** seedé depuis la liste (aucun mot de passe par défaut connu).

### 5.3 Permissions appliquées dans le code, pas seulement par masquage

- **`services/permissions.py`** est la source unique : `est_autorise(role, action)` consulte `AUTORISATIONS[action]` (ensemble de rôles).
- Chaque **service** qui expose une action protégée appelle `est_autorise` **en tête de fonction** et lève `AccesRefuse` si le rôle n'est pas admis.
- L'**UI** utilise aussi `est_autorise` pour **construire la grille** (boutons visibles) — mais c'est un simple confort : même si un bouton était forcé/affiche par erreur, le service re-bloquerait.
- « Bouton KOES » et « Paramètres » suivent la même règle (KOES visible pour tous, Paramètres `Admin` uniquement, vérifié côté service).

### 5.4 Matrice des rôles

Légende : ✔ = autorisé ; ✘ = refusé.

| Action / Écran | Admin | Editeur | Cariste_Coulage | Cariste_Emaillage | Utilisateur |
|---|:-:|:-:|:-:|:-:|:-:|
| Saisie Coulage (créer wagon) | ✔ | ✔ | ✔ | ✘ | ✘ |
| Émaillage (transition Sortie→Emaillage) | ✔ | ✔ | ✘ | ✔ | ✘ |
| Voir Nouveau | ✔ | ✔ | ✔ | ✔ | ✔ |
| Voir Sortie | ✔ | ✔ | ✔ | ✔ | ✘ |
| Voir Emaillage | ✔ | ✔ | ✘ | ✔ | ✘ |
| Voir Vide | ✔ | ✔ | ✔ | ✔ | ✔ |
| Voir Tout (Complet) | ✔ | ✔ | ✔ | ✔ | ✔ |
| Voir Archive | ✔ | ✔ | ✔ | ✔ | ✔ |
| Voir KOES | ✔ | ✔ | ✔ | ✔ | ✔ |
| Utilisateurs (gestion) | ✔ | ✘ | ✘ | ✘ | ✘ |
| Paramètres (Système / KEOS) | ✔ | ✘ | ✘ | ✘ | ✘ |
| Auto Cull | ✔ | à confirmer | à confirmer | à confirmer | à confirmer |
| Menu admin | ✔ | à confirmer | à confirmer | à confirmer | à confirmer |
| Changer mot de passe | ✔ | ✔ (soi) | ✔ (soi) | ✔ (soi) | ✔ (soi) |

> La lecture seule d'`Utilisateur` (Nouveau, Vide, Tout, Archive) est cohérente avec la règle 75 de 12.txt. Les cases « à confirmer » (Auto Cull, Menu, ChangerMDP) reprennent la remarque du cahier des charges (dans V17 aucun contrôle de rôle n'existait sur Auto Cull et Menu).

---

## 6. Flux de données et appels

### 6.1 Chaîne générale (un bouton jusqu'à la base)

```
[ui] widget → callback (collecte + validation de surface)
        → [services] fonction métier (vérifie permission + règles)
            → [db] requête SQL (transaction)
            → [services] retourne dataclass / Resultat
        → [ui] met à jour l'écran (+ messagebox si action manuelle)
```

Règle : **l'UI ne fait pas de SQL, les services ne font pas de Tkinter, db.py ne fait pas de logique métier.**

### 6.2 Exemple 1 — « Enregistrer un chargement » (saisie Coulage)

1. `ui/saisie_coulage.py` : l'opérateur choisit la référence (combobox), la famille se remplit **automatiquement** (lecture seule), saisit Qty, Coulage, Chariot, Tunnel ; `status` est affiché « Nouveau » en lecture seule ; l'utilisateur courant et la date/heure sont affichés.
2. Au clic « Enregistrer », l'écran **valide la surface** (tunnel choisi, au moins une ligne de détail, quantités > 0) et construit une liste de détails `[(id_reference, quantite), …]`.
3. L'écran appelle `services.chargements.enregistrer_chargement(no_wagon, tunnel, id_cariste, details, coulage, chariot)`.
4. Le service : `est_autorise(role, 'saisie')` (sinon `AccesRefuse`) → applique la règle de réutilisation de `no_wagon` (blocage en `Nouveau`, suppression+recréation sinon, §3.4) → appelle `db.creer_chargement(...)`.
5. `db.creer_chargement` ouvre une transaction unique : `INSERT chargement` puis `INSERT detail_chargement` pour chaque ligne ; retourne le `id_chargement` créé (ou `None`).
6. Le service retourne un `Resultat(ok=True, …)` ; l'UI affiche une `messagebox` de succès (action manuelle) et/ou réinitialise le formulaire et rafraîchit les compteurs.

### 6.3 Exemple 2 — « Passer Sortie → Emaillage »

1. `ui/emaillage.py` (saisie `no_wagon`) **ou** le bouton « Emaillage » d'une ligne de `ui/affichages.py` (vue Sortie) appelle `services.chargements.passer_en_emaillage(no_wagon, id_cariste)`.
2. Le service : `est_autorise(role, 'emaillage')` → exécute l'`UPDATE` conditionnel `SET status='Emaillage', date_chargement=now WHERE no_wagon=? AND status='Sortie'`.
3. Contrôle de `rowcount` : si `0`, lever `ErreurMetier` (« Wagon introuvable ou pas en Sortie ») ; sinon succès.
4. L'UI : en cas d'erreur → `messagebox` (action manuelle) ; en succès → rafraîchit la liste de la vue Sortie (le wagon disparaît de Sortie et apparaît en Emaillage) et met à jour les compteurs.

### 6.4 Exemple 3 — « AutoSortie (tick de 30 s) »

1. `ui/accueil.py` (via `main.py`) arme `root.after(30000, tick)`.
2. `tick` appelle `services.auto_sortie.executer(now)`.
3. Le service lit `HeuresAutoSortie` et `Cle_KEOS` dans `parametres` (chaque fois), calcule `limite` en Python, exécute deux `UPDATE` conditionnels (tunnels 1/2 puis KEOS), totalise les `rowcount`.
4. Retourne `N` (nombre de wagons basculés) ; l'accueil met à jour le **label discret** (si `N>0`) et **arme son effacement après 5 min**. **Aucun popup.**

---

## 7. Gestion des erreurs et journalisation

### 7.1 Quand afficher une `messagebox`

- **Uniquement pour les actions manuelles** : connexion refusée, saisie invalide, enregistrement, transition manuelle (Sortie→Emaillage, Emaillage→Vide), sauvegarde de paramètre, « Appliquer maintenant », ajout/modification/suppression d'utilisateur, confirmation d'action destructive (réutilisation de `no_wagon`, Auto Cull).
- **Jamais** depuis le minuteur AutoSortie ni depuis les compteurs automatiques (§4.5).

### 7.2 Quand ne pas afficher (arrière-plan)

- AutoSortie, rafraîchissement des compteurs, alertes (l'ouverture des alertes se fait à la connexion, via l'écran, pas en popup parasite), ticks périodiques.
- Ces chemins consignent les erreurs en log et poursuivent (échec silencieux, au plus un état visuel discret).

### 7.3 Capture des erreurs

- Les **violations métier** sont des exceptions typées (`ErreurMetier`, `AccesRefuse`, `SaisieInvalide`) levées par les services et interceptées par l'UI pour un message précis.
- Les **erreurs inattendues** (SQLite, I/O) sont attrapées à la frontière UI/service pour éviter un plantage brutal : message générique à l'utilisateur, détail consigné en log. Le contexte `connexion()` de `db.py` fait `rollback` puis relève l'exception (aucune écriture à moitié validée).

### 7.4 Journalisation et audit (structure proposée, **différée** — phase 6)

- **Log applicatif** : utiliser `logging` vers un fichier rotatif (`logs/systeme_chargement.log`) pour les erreurs d'exécution, avec niveau et horodatage.
- **Audit métier** (table `log_audit`, future) : `id_log`, `horodatage`, `matricule`, `action`, `detail`, `niveau`. Fonction `ajouter_log(...)` appelée depuis **chaque action importante** des services (connexion, saisie, transition, paramètre modifié, suppression d'utilisateur). **Purge automatique au-delà de 90 jours.**
- Ce couple (log technique + audit métier) est préparé conceptuellement maintenant mais **pas codé** avant la phase 6.

---

## 8. Points précis : import des références et seed des utilisateurs

### 8.1 Import des 167 références (avec doublons)

La liste de 12.txt (lignes 110–277) contient **167 lignes** mais **7 doublons**, soit **160 références uniques**. Doublons vérifiés :

| Référence | Occurrences | Famille(s) constatée(s) |
|---|---|---|
| `GE` | 2 | `Lavabo` (identiques) |
| `GG` | 3 | `Lavabo` (identiques) |
| `1061` | 2 | `Vasque` (identiques) |
| `1080` | 2 | `Cuvette robots` (identiques) |
| `1238` | 2 | `Vasque` (identiques) |
| `1345` | 2 | `lavabo robots` **vs** `Lavabo` (famille incohérente) |

> Note : la mention « 256 » du brief correspond à la **ligne 256** du fichier, qui est précisément le second doublon de `1345` ; aucun code référence « 256 » n'existe dans la liste.

**Stratégie d'import (recommandée)** :
1. **Normalisation** avant insertion : `strip` des espaces, suppression des espaces multiples, casse « Titre » pour la famille.
2. **Déduplication** : s'appuyer sur `UNIQUE(reference)` via `INSERT OR IGNORE` (ou `INSERT … ON CONFLICT(reference) DO NOTHING`). La **première occurrence gagne** par défaut.
3. **Traiter l'incohérence `1345`** : préférer la famille **canonique** (`Lavabo`, la forme corrigée en casse) plutôt que la première rencontrée (`lavabo robots`) — à confirmer, mais recommandé.
4. **Compter et rapporter** : après import, afficher « N insérées / M ignorées (doublons) » pour vérification.
5. **Signaler les anomalies à YASSIN** (données douteuses, à confirmer avant import) :
   - `Réservoirs` (ligne 261) et `Colonnes` (ligne 262) — ressemblent à des **familles** saisies par erreur dans la colonne référence ;
   - `4101 HPC` et `4383 grés` — sont des **codes distincts** (à conserver), mais confirmer qu'ils ne devraient pas fusionner avec `4101`/`4383` ;
   - casse incohérente : `GB → lave-main`, `4834 → bidet suspendu`, `1282/1345/2005 → lavabo robots` (normalisation « Titre »).
6. **Support CSV** : import dédié (phase 5) lisant deux colonnes `Reference; Famille`, appelant la même fonction de normalisation + `INSERT OR IGNORE`.

### 8.2 Seed des utilisateurs (sans mot de passe en clair)

La liste de 12.txt (lignes 280–293) contient **12 utilisateurs** (dont l'Admin). Les valeurs `000000` et `admin123` **ne doivent jamais être stockées**.

**Répartition recommandée** :
- **Admin `KO05388` YASSIN SAADI** : créé **interactivement** au premier lancement (mot de passe choisi, jamais seedé).
- **11 autres comptes** (4 Cariste_Coulage, 6 Cariste_Emaillage, 1 Utilisateur, 1 Editeur) : **seedés à l'initialisation** avec un **mot de passe temporaire haché** via PBKDF2, jamais `000000` en clair.

| Matricule | Nom | Rôle |
|---|---|---|
| KE13583 | BAGGAR ABDESLAM | Cariste_Coulage |
| KE13361 | BENISSA ABDESLAM | Cariste_Coulage |
| KE13454 | HALIM EL MESHAM | Cariste_Coulage |
| KE05206 | ABDI MOUMEN MOAD | Cariste_Coulage |
| KE05031 | MANDILI MOHAMED | Cariste_Emaillage |
| KE13520 | BOUKHARI HAMID | Cariste_Emaillage |
| KE13480 | MESMOUDI ABDERAHIM | Cariste_Emaillage |
| KE13533 | NABIL ENNACIRI | Cariste_Emaillage |
| KE05304 | AMDAH ABDELHAK | Cariste_Emaillage |
| KE13517 | HAMMOU AHMED | Utilisateur |
| KE05087 | ABDESLAM EL HAOUARI | Editeur |

**Choix du mot de passe temporaire** (à trancher) :
- **(a) recommandé** — mot de passe temporaire **aléatoire par utilisateur**, affiché une seule fois à l'Admin (ou consigné dans un rapport initial) ; l'utilisateur le change via « Changer Mot De Passe » (accessible sans connexion). Sécurité maximale.
- **(b)** — mot de passe temporaire **unique commun** (ex. `Jacob2026!`), communiqué en interne, à changer impérativement. Plus simple mais plus risqué.
- Dans les deux cas, seuls les **hash** sont stockés. Si l'option `doit_changer_mdp` (§2.2) est retenue, forcer le changement au premier login.

**Nettoyage** : appliquer `strip` aux matricules et noms (plusieurs noms de la source ont des espaces parasites, ex. `BENISSA ABDESLAM `, `HALIM  EL MESHAM`).

---

## 9. Récapitulatif des points à confirmer (avant la phase concernée)

| # | Point | Phase concernée | Décision proposée |
|---|---|---|---|
| 1 | Sémantique exacte de `coulage` / `chariot` | 2 | Texte libre nullable (poste de coulage / n° de chariot) ; envisager combobox plus tard. |
| 2 | Règle de réutilisation de `no_wagon` | 2 | Suppression de l'ancien **avec confirmation + archivage** avant recréation. |
| 3 | Écran/bouton `Emaillage → Vide` | 2–3 | Ajouter un bouton « Vide » (à valider). |
| 4 | Visibilité Auto Cull / Menu / ChangerMDP | 1–4 | Auto Cull et Menu = Admin ; ChangerMDP = soi-même pour tous. |
| 5 | Auto Cull : archivage vs détection de wagons perdus | 4 | Archivage des `Vide` vers `archive` (structure prête). |
| 6 | Mot de passe temporaire du seed | 1 | Aléatoire par utilisateur (option a) ou commun (option b). |
| 7 | Incohérences de la liste des références (`Réservoirs`, `Colonnes`, `1345`, casse) | 5 | Normalisation + signalement avant import. |

---

## 10. Synthèse des invariants de conception

1. **Couches strictes** : `ui/` → `services/` → `db.py` → SQLite ; `config.py` et `session.py` transverses ; **aucun SQL dans `ui/`**.
2. **Retours typés** : `db` → Row/dict/scalaire ; `services` → dataclasses + `Resultat` + exceptions typées ; `ui` → consomme et affiche.
3. **Données** : `PRAGMA foreign_keys=ON` (par connexion) + `journal_mode=WAL` (persistant) ; `date_chargement` en `YYYY-MM-DD HH:MM:SS` (tri chronologique = tri lexicographique) ; clés étrangères avec `ON DELETE CASCADE` (détails) et `ON DELETE SET NULL` (cariste).
4. **État** : transitions gardées par `UPDATE … WHERE status = attendu` + contrôle de `rowcount` ; `date_chargement` réécrite à chaque transition.
5. **AutoSortie** : `root.after(30000)` fil principal, deux canaux (HeuresAutoSortie / Cle_KEOS) relus à chaque tick, date limite calculée en Python, **aucun popup**, label discret qui s'efface après 5 min.
6. **Sécurité** : PBKDF2-SHA256 + sel (310 k itérations), Admin `KO05388` créé au premier lancement, permissions vérifiées **dans les services** (pas seulement par masquage).
7. **Références** : 167 lignes → 160 uniques ; import normalisé + `INSERT OR IGNORE` ; doublons GE/GG/1061/1080/1238/1345.
8. **Utilisateurs** : seed des 11 non-admin avec **hash** de mot de passe temporaire, jamais `000000`/`admin123` en clair.
