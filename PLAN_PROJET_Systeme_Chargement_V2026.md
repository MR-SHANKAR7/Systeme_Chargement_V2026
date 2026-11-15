# Plan de projet — Systeme_Chargement V2026

> Reconstruction de l'application Access V17 (suivi des wagons de production, usine Jacob Delafon Africa / Groupe KOHLER, Tanger) en Python 3.10+ / Tkinter / ttk / SQLite.
> Document de pilotage : **plan de phases + registre des risques + points à confirmer**.
> Rédigé sans code, en français.

---

## 0. État des lieux constaté (base de ce plan)

Avant de planifier, j'ai vérifié l'état réel des fichiers :

| Élément | Constat |
|---|---|
| `12.txt` (cahier des charges) | Présent à la racine de `Python System  de Chargement`. Contient le schéma SQLite, les règles métier, les rôles, les écrans, **la liste des ~167 références** et **les 12 utilisateurs initiaux** (dont l'Admin KO05388). |
| Dossier frère `Systeme_Chargement` | **Projet complet de la V17 reconstruite** (main, config, db, session, `services/` avec audit/parametres/auto_sortie/alertes/archivage…, `ui/` avec saisie/emaillage/affichage/utilisateurs/auto_cull/menu_admin…, `data/references.csv`, `data/utilisateurs.csv`, `data/chargement.db`, `assets/Logos.txt`). |
| Dossier de travail `Systeme_Chargement_V2026_Phase1` | **N'est pas vide** : contient déjà une implémentation Phase 1 (config.py, db.py, session.py, main.py, `services/authentification.py`, `services/permissions.py`, `ui/login.py`, `ui/accueil.py`, `Lancer_Systeme_Chargement.bat`, `data/chargement.db`). |
| `data/chargement.db` (Phase1) | **Déjà initialisée** : Admin `KO05388` déjà créé (mot de passe haché), 0 référence, 0 chargement, 0 archive, paramètres `HeuresAutoSortie=12` et `Cle_KEOS=12` présents. |

**Conséquence pour le plan** : la Phase 1 est en grande partie déjà codée. La stratégie recommandée (section 5) n'est pas « repartir de zéro », mais **valider/consolider ce qui existe, corriger les écarts au cahier des charges, et repartir d'une base SQLite vierge pour le test de premier lancement.**

### Écarts déjà repérés entre le code actuel et le cahier des charges
1. **Table `chargement`** : le code actuel contient `date_coulage` (un champ *date*) au lieu des champs `coulage` et `chariot` demandés → lié au point à confirmer (c).
2. **Accueil** : il n'existe pas de carte « Voir Emaillage » (vue d'affichage) ; seule l'action « Émaillage » (passage Sortie→Emaillage) est présente. Le cahier demande pourtant les vues *Nouveau, Sortie, Emaillage, Vide, Tout, KOES, Archive*.
3. **Logos** : l'en-tête affiche le texte « KOHLER » mais aucune image de logo n'est chargée (`assets/` absent dans Phase1).
4. **Liste des références de 12.txt** : elle contient des **doublons** (ex. `GE Lavabo`, `GG Lavabo` ×3, `1080`, `1061`, `1238`, `1345`) et des libellés « famille » (`Réservoirs`, `Colonnes`) → conflit avec la contrainte `UNIQUE` de `reference.reference`.
5. **Mots de passe initiaux** : les 11 utilisateurs de `12.txt` ont `000000` (6 caractères), alors que le code impose un minimum de 8 caractères à la création Admin et au changement de mot de passe.

---

## 1. Plan détaillé de la Phase 1

**Périmètre** : `db.py` + `session.py` + `services/authentification.py` + `services/permissions.py` + `ui/login.py` + `ui/accueil.py` + `main.py` + lanceur. Seule cette phase est à exécuter maintenant, **après accord**.

### 1.1 Fichiers à créer / modifier

| Fichier | Action | Contenu attendu |
|---|---|---|
| `config.py` | conserver/valider | Constantes, couleurs KOHLER, rôles, libellés, chemins `data/` et `data/chargement.db`. |
| `session.py` | conserver/valider | `UtilisateurConnecte` (id, matricule, nom, rôle) + `Session` (ouvrir/fermer/est_connectee). |
| `services/authentification.py` | conserver/valider | Hash PBKDF2-SHA256 + sel + `hmac.compare_digest` ; jamais de mot de passe en clair. |
| `db.py` | **corriger/compléter** | Schéma 7 tables conforme au cahier ; corriger `coulage`/`chariot` (selon décision c) ; fonctions init/auth/changement/compteurs. |
| `services/permissions.py` | conserver/valider | Matrice d'autorisations par action ; `est_autorise(role, action)`. |
| `ui/login.py` | conserver/valider | Fenêtre connexion + `InitialisationAdmin` + `ChangementMotDePasse`. |
| `ui/accueil.py` | **corriger/compléter** | En-tête, grille dynamique 3 colonnes, compteurs, KOES centré, recherche (désactivée), déconnexion. |
| `main.py` | conserver/valider | Point d'entrée, styles, séquence login→accueil→déconnexion, init Admin si base vide. |
| `Lancer_Systeme_Chargement.bat` | conserver | Lance `python main.py`, pause en cas d'erreur. |
| `data/` | **réinitialiser** | Supprimer `chargement.db` pour un test de premier lancement propre. |
| `assets/` | créer (vide ou logos) | Prévoir le dépôt des logos KOHLER (voir section 5). |

### 1.2 Critères d'acceptation (par composant)

**db.py**
- La base `data/chargement.db` est créée automatiquement au premier lancement.
- `PRAGMA foreign_keys = ON` actif ; contraintes `CHECK` sur `status`, `tunnel`, `role`.
- Les paramètres par défaut `HeuresAutoSortie=12` et `Cle_KEOS=12` sont insérés une seule fois (INSERT OR IGNORE).
- `compter_statuts()` renvoie les compteurs Nouveau/Sortie/Emaillage/Vide/Tout/Archive exacts.
- Aucune donnée métier (références, chargements) n'est injectée par le code.

**session.py**
- Après connexion, `session.utilisateur` est l'objet utilisateur correct.
- Après déconnexion, `session.utilisateur` est `None`.

**services/authentification.py**
- Le mot de passe n'apparaît jamais en clair dans la base (vérification : le champ commence par `pbkdf2_sha256$`).
- `verifier_mot_de_passe` accepte le bon mot de passe, refuse un mauvais, et refuse un hash corrompu sans lever d'exception.

**services/permissions.py**
- Matrice conforme au tableau des rôles du cahier des charges.
- Chaque accès réservé est **vérifié côté code**, pas seulement masqué (tentative d'appel direct → « Accès refusé »).

**ui/login.py**
- « Bienvenue » + Matricule + Mot de passe + boutons Connexion / Changer Mot De Passe / Annuler + étiquette `V2026`.
- `InitialisationAdmin` : matricule fixe `KO05388`, nom pré-rempli, mot de passe + confirmation, minimum 8 caractères.
- Échec de connexion → message clair, champ mot de passe vidé.

**ui/accueil.py**
- En-tête : nom, matricule, rôle.
- Compteurs Nouveau / Sortie / Emaillage / Vide / Tout / Archive, rafraîchis toutes les 30 s, exacts.
- Grille de boutons **3 colonnes, sans trou**, réorganisée selon le rôle.
- Bouton **KOES centré** en dernière ligne, visible pour tous les rôles.
- Barre « Déconnexion » en bas ; confirmation ; fermeture de toutes les fenêtres.
- Label discret AutoSortie (placeholder en Phase 1).

**main.py**
- L'application démarre sans erreur, passe en plein écran à la connexion.
- `InitialisationAdmin` ne s'affiche **que** si la table `utilisateurs` est vide.

### 1.3 Ordre d'exécution dans la phase
1. `config.py` (fondations : constantes, chemins).
2. `session.py` (types).
3. `services/authentification.py` (hash).
4. `db.py` (schéma + requêtes) — **corriger coulage/chariot selon décision (c)**.
5. `services/permissions.py` (matrice).
6. `ui/login.py` (connexion + init Admin + changement MDP).
7. `ui/accueil.py` (grille, compteurs, permissions).
8. `main.py` (assemblage + styles).
9. `Lancer_Systeme_Chargement.bat`.
10. Réinitialisation de `data/chargement.db` puis **test utilisateur** (ci-dessous).

### 1.4 Procédure de test utilisateur (pas à pas)

**Prérequis** : supprimer `data/chargement.db` (ou la renommer) pour un premier lancement vierge.

**Étape A — Premier lancement / initialisation Admin**
1. Double-cliquer `Lancer_Systeme_Chargement.bat`.
2. Vérifier que la fenêtre « Première configuration » s'ouvre avec le matricule **KO05388** (non modifiable).
3. Saisir le nom (ex. `YASSIN SAADI`) et un mot de passe ≥ 8 caractères, puis confirmation identique.
4. Tester le refus : mot de passe court (< 8) ou confirmation différente → message d'avertissement, pas de création.
5. Créer le compte → message de confirmation → retour à l'écran de connexion.

**Étape B — Connexion Admin**
1. Se connecter avec `KO05388` + le mot de passe choisi.
2. Vérifier l'accueil : en-tête avec nom/matricule/rôle **Administrateur**.
3. Vérifier que **tous** les boutons du rôle Admin sont visibles (Saisie, Émaillage, Voir Nouveau, Voir Sortie, Voir Vide, Voir Tout, Archive, Utilisateurs) + Auto Cull / Paramètres / Menu / Changer MDP + KOES centré en dernière ligne.
4. Vérifier les 6 compteurs à **0**.

**Étape C — Connexion de chaque rôle (grille dynamique et compteurs)**
> Pour tester les autres rôles en Phase 1, il faut des comptes : insérer temporairement les 11 utilisateurs initiaux de `12.txt` (matricule, nom, rôle, mot de passe `000000`) via un script de test jetable ou un import SQLite — **hors code applicatif**. Ces comptes serviront de base pour les phases suivantes. Voir aussi le point (d)/(f) et le risque R9.

Pour chaque rôle, se connecter puis vérifier l'affichage attendu :

| Rôle | Boutons attendus | Boutons à vérifier absents |
|---|---|---|
| Admin | Tout + Utilisateurs + Paramètres + Auto Cull + Menu | — |
| Cariste_Coulage | Saisie, Voir Nouveau, Voir Sortie, Voir Vide, Voir Tout, Archive | Émaillage, Utilisateurs, Paramètres |
| Cariste_Emaillage | Émaillage, Voir Nouveau, Voir Sortie, Voir Vide, Voir Tout, Archive | Saisie, Utilisateurs, Paramètres |
| Editeur | Saisie, Émaillage, tous les affichages, Archive | Utilisateurs, Paramètres |
| Utilisateur | Voir Nouveau, Voir Vide, Voir Tout, Archive (lecture seule) | Saisie, Émaillage, Utilisateurs, Paramètres |

Pour chaque rôle, vérifier en plus :
- Le bouton **KOES** est toujours visible et centré.
- Aucun « trou » dans la grille (les boutons se suivent en 3 colonnes).
- Les compteurs affichent les mêmes valeurs quel que soit le rôle (cohérence des données).

**Étape D — Contrôle des accès forcés**
1. Connecté en rôle `Utilisateur`, tenter d'accéder à une fonction réservée (ex. Saisie ou Utilisateurs) par un appel direct → message « Accès refusé ».
2. Vérifier que le masquage n'est pas la seule protection.

**Étape E — Changer mot de passe**
1. Depuis l'écran de connexion : bouton « Changer Mot De Passe » → Matricule + Ancien + Nouveau + Confirmation.
2. Test refus : ancien mot de passe faux → erreur ; nouveau < 8 → avertissement ; confirmation différente → avertissement.
3. Test succès puis reconnexion avec le nouveau mot de passe.

**Étape F — Déconnexion**
1. Bouton « Déconnexion » → confirmation demandée.
2. Valider → toutes les fenêtres se ferment et l'application quitte proprement.
3. Relancer et vérifier que la base est toujours cohérente (pas de corruption).

**Critère de sortie de la Phase 1** : toutes les étapes A→F passent pour au moins les 5 rôles, sans erreur de console et sans blocage.

---

## 2. Feuille de route — Phases 2 à 6 (résumé)

Chaque phase se termine par un **point d'arrêt** : l'utilisateur teste, donne son retour, et on ne démarre la suivante qu'après validation.

| Phase | Périmètre | Point d'arrêt (test utilisateur) |
|---|---|---|
| **2 — Saisie + Émaillage + vues + filtre tunnel** | Écrans Saisie Coulage (référence→famille auto, multi-références `detail_chargement`, Coulage/Chariot selon décision (c), Tunnel 1/2/KEOS, statut Nouveau auto, cariste connecté) ; Émaillage (no_wagon, Sortie→Emaillage) ; transition Emaillage→Vide selon décision (b) ; vues Nouveau/Sortie/Emaillage/Vide/Complet/KOES/Archive (tri date croissant, statut coloré) ; filtre tunnel sur la vue Sortie ; bouton « Emaillage » par ligne. | Saisir des wagons réels, passer Nouveau→Sortie→Emaillage→Vide, vérifier les vues, le filtre tunnel et les couleurs. |
| **3 — AutoSortie + Paramètres + Alertes** | Timer `root.after(30000)`, Nouveau→Sortie quand l'âge dépasse le délai ; deux traitements séparés (tunnels 1/2 = `HeuresAutoSortie`, KEOS = `Cle_KEOS`) ; délais relus à chaque exécution ; **aucun popup** dans le timer (label discret 5 min) ; écrans Paramètres « Système » (1/2) et « Système KEOS » (+/− par pas de 1 h, 1–168 h, « Appliquer maintenant ») ; alertes à la connexion (Sortie > 5 j, Emaillage > 2 j). | Laisser des wagons vieillir (ou forcer les dates) et vérifier le passage automatique, le label discret, les deux délais KEOS/1-2, et l'ouverture des alertes au login. |
| **4 — Utilisateurs + Recherche wagon + Auto Cull/Archive** | Gestion utilisateurs (ajout/modif/suppression, mot de passe masqué) ; recherche rapide wagon (numérique, résultat coloré par statut, messages « invalide »/« introuvable ») ; Auto Cull selon décision (a) ; archivage vers `archive`. | Créer/modifier/supprimer un utilisateur, rechercher des wagons, exécuter l'Auto Cull et vérifier le compteur avant/après. |
| **5 — Import CSV références + PyInstaller** | Import des ~167 références (Reference + Famille) depuis CSV ; gestion des doublons (décision, risque R5) ; packaging `.exe` PyInstaller (zéro dépendance Access). | Importer le CSV réel, vérifier le dédoublonnage et le rapport d'import ; lancer le `.exe` sur le poste d'atelier. |
| **6 — Futur (non planifié dans l'immédiat)** | Journal d'audit (`log_audit`, purge > 90 j) ; sauvegarde hebdomadaire auto du SQLite ; sécurité (verrouillage après X échecs, déconnexion après inactivité) ; table de configuration (durée de cycle, nom société) ; export Excel/PDF ; rapports imprimables ; statistiques/graphiques ; multi-postes (partage réseau, à étudier). | À définir au moment voulu. |

---

## 3. Registre des risques

Légende : **P** = probabilité, **I** = impact (Élevé / Moyen / Faible).

| # | Risque | Type | P | I | Atténuation |
|---|---|---|---|---|---|
| R1 | **Mise en cache/verrouillage du fichier SQLite par OneDrive** (le dossier est sur OneDrive) : corruption, verrou, conflits de synchronisation, fichiers `-journal`/`-wal` répliqués. | Technique | Élevée | Élevé | « Toujours conserver sur cet appareil » sur le dossier ; `busy_timeout` ; mode WAL maîtrisé ; fermeture propre de la connexion ; interdire le multi-instance ; sauvegarde hebdomadaire (Phase 6) ; à terme, envisager un emplacement hors OneDrive. |
| R2 | **Gel/ralentissement de l'interface par le timer** (`root.after(30000)` pour les compteurs puis AutoSortie). | Technique | Moyenne | Moyen | Traitements courts, requêtes indexées, `try/except` autour du timer, **aucun popup** dans le timer (label discret), resynchronisation à 30 s uniquement. |
| R3 | **Accumulation de fenêtres** (plusieurs Toplevel ouverts, instabilité). | Technique | Moyenne | Moyen | `transient` + `grab_set` ; une seule fenêtre modale à la fois ; fermeture de **toutes** les fenêtres à la déconnexion. |
| R4 | **Perte de données lors de la migration / réutilisation du no_wagon** (suppression d'un enregistrement existant). | Fonctionnel | Moyenne | Élevé | Décision (e) ; **archiver l'ancien enregistrement plutôt que supprimer** ; confirmation avant action destructive ; sauvegarde avant test. |
| R5 | **Doublons dans la liste des références** (12.txt en contient, ex. `GE Lavabo`, `GG Lavabo`, `1080`, `1061`) → conflit `UNIQUE` à l'import. | Données | Élevée | Moyen | Dédoublonnage avant import ; règle de choix (garder la 1re ligne / fusion) ; rapport d'import (lignes ignorées) ; nettoyage des libellés « famille » (`Réservoirs`, `Colonnes`). |
| R6 | **Règle de réutilisation d'un no_wagon ambiguë** (bloquer si Nouveau, supprimer sinon) → incohérence ou perte silencieuse. | Fonctionnel | Moyenne | Élevé | Décision (e) explicite ; messages clairs ; traçabilité (archive). |
| R7 | **Écart de précision de l'horloge** (calcul de la date limite AutoSortie). | Technique | Faible | Moyen | Utiliser une **source unique** `datetime.now()` ; stocker `YYYY-MM-DD HH:MM:SS` ; comparaison `date_chargement <= limite` en Python ; usage local (pas de comparaison inter-postes). |
| R8 | **Perte du mot de passe Admin KO05388** (aucune récupération prévue). | Fonctionnel | Moyenne | Élevé | Procédure de réinitialisation documentée (réinitialiser la base / script hors-ligne) ; ne jamais stocker en clair ; conserver une trace sécurisée hors application. |
| R9 | **Mots de passe initiaux faibles** (`000000`, 6 caractères) pour les 11 utilisateurs. | Sécurité | Élevée | Moyen | Forcer le changement au premier login (à planifier) ; politique 8 caractères minimum ; alerte à l'administrateur. |
| R10 | **Élévation de privilèges / accès forcé** à une fonction réservée. | Sécurité | Faible | Élevé | Vérification **côté code** (pas seulement masquage) ; matrice centralisée `permissions.py` ; test de contournement (Étape D). |
| R11 | **Corruption SQLite après arrêt brutal** (coupure de courant). | Technique | Moyenne | Élevé | Commit fréquents ; `PRAGMA` adapté ; WAL ; sauvegarde hebdo (Phase 6) ; fermeture propre à la déconnexion. |
| R12 | **Encodage/délimiteurs du CSV des références** (BOM UTF-8, espaces, tabulations). | Technique | Moyenne | Moyen | Lecture `utf-8-sig` ; `strip()` des valeurs ; validation des colonnes ; rapport d'import. |
| R13 | **Lisibilité insuffisante sur le poste d'atelier** (opérateur debout, haute résolution). | Fonctionnel | Faible | Moyen | Gros boutons, police Segoe UI, plein écran, thème KOHLER contrasté (navy #1B3A5C / accent #2E86C1 / or #C9A84C). |

---

## 4. Points à confirmer (avec recommandation par défaut)

### A. Bloquants pour la Phase 1 (à trancher avant de finaliser)

**(d) Visibilité de Auto Cull / Menu / ChangerMDP par rôle**
- Énoncé : dans la V17, aucun contrôle de rôle n'existait sur Auto Cull et Menu.
- **Recommandation** : `Auto Cull` = **Admin uniquement** ; `Menu` = **Admin uniquement** ; `Changer MDP` = **tous les rôles** (chacun doit pouvoir changer son propre mot de passe). `Paramètres` reste Admin (déjà acté).
- Justification : ces fonctions sont administratives ; les exposer aux caristes est inutile et risqué. Le code actuel de `permissions.py` fait déjà ce choix (`auto_cull`/`menu`/`parametres` = Admin).
- Impact si non tranché : l'en-tête de l'accueil (Phase 1) serait livré avec une règle arbitraire.

**(f) Champs de « Changer mot de passe »**
- Énoncé : quels champs pour la fenêtre de changement de mot de passe ?
- **Recommandation** : **Matricule + Ancien + Nouveau + Confirmation** (4 champs), accessible **sans connexion** (depuis l'écran de login) et **depuis l'accueil** (matricule pré-rempli si connecté).
- Justification : le champ Matricule est nécessaire pour le changement « sans connexion » ; pré-rempli quand on est connecté. C'est déjà ce que fait `ui/login.py`.
- Impact si non tranché : l'écran ChangerMDP (Phase 1) serait incomplet.

### B. Différés à une phase ultérieure

**(a) Auto Cull — archivage vs détection de wagons perdus**
- **Recommandation** : **archivage des wagons « Vide » vers `archive`**, avec compteur affiché avant exécution.
- Justification : cohérent avec le compteur « Archive » déjà présent et avec l'usage V17 ; la « détection de wagons perdus » est un besoin distinct qui peut devenir un item de Phase 6.
- Phase concernée : **4** (ne bloque pas la Phase 1).

**(b) Emaillage → Vide (qui / depuis quel écran)**
- **Recommandation** : un écran/bouton dédié, accessible à **Cariste_Emaillage + Admin + Editeur**, par **saisie du no_wagon**, avec vérification `status = 'Emaillage'` avant validation (symétrique de Sortie→Emaillage).
- Justification : symétrie et simplicité ; la vérification du statut évite les transitions invalides.
- Phase concernée : **2**.

**(c) Emplacement des champs Coulage et Chariot**
- **Recommandation** : les conserver comme **colonnes de `chargement`** (`coulage` et `chariot`), conformément au schéma du cahier des charges.
- Justification : une table séparée n'apporte rien (relation 1-1) ; deux colonnes sont plus simples. **À corriger** dans le `db.py` actuel qui a mis `date_coulage` à la place.
- Phase concernée : **2** (écran Saisie), mais la correction du schéma doit être faite dès la Phase 1 pour éviter une migration de schéma plus tard.

**(e) Règle de réutilisation d'un no_wagon**
- **Recommandation** : conserver le comportement V17 (bloquer si `Nouveau` ; sinon réutiliser) **mais** archiver l'ancien enregistrement au lieu de le supprimer définitivement.
- Justification : préserve la traçabilité et évite la perte de données (risque R4).
- Phase concernée : **2** (Saisie).

---

## 5. Stratégie de gestion des fichiers existants

### 5.1 Dossier frère `Systeme_Chargement` (projet complet V17)
- **Ne pas modifier ni supprimer.** C'est la référence métier (règles, écrans, structure) et la source des données (références, utilisateurs).
- **Archiver en lecture seule** : renommer en `Systeme_Chargement_archive_V17` (ou compresser en `.zip`) pour éviter toute confusion avec la nouvelle version.
- À conserver explicitement comme source : `data/references.csv`, `data/utilisateurs.csv`, `assets/Logos.txt` (pour les logos), et le schéma des écrans.

### 5.2 Dossier de travail `Systeme_Chargement_V2026_Phase1`
- **Constats** : il contient déjà une Phase 1 cohérente ; le dossier n'est **pas** vide comme supposé.
- **Recommandation** : **ne pas tout supprimer** ; conserver le code Phase 1 existant comme socle, et :
  1. **Corriger les écarts** listés en section 0 (coulage/chariot, vue « Voir Emaillage », logos).
  2. **Réinitialiser `data/chargement.db`** (supprimer ou renommer) pour permettre le test de premier lancement (Étape A). La base actuelle contient déjà KO05388.
  3. **Créer `data/` et `assets/`** propres : `data/` pour la base, `assets/` pour les logos (à importer depuis `assets/Logos.txt` du projet frère).
- Si le mandataire souhaite malgré tout un départ « de zéro », déplacer le contenu actuel dans `_archive_phase1/` (et non le supprimer) avant de recréer la structure.

### 5.3 Ce qu'il ne faut **pas** toucher
- `12.txt` (cahier des charges source).
- Le dossier frère `Systeme_Chargement` une fois archivé (référence).
- Les données réelles de production éventuelles (aucune migration Access n'est prévue : base SQLite neuve — décision actée).
- Les fichiers `__pycache__/` et `*.pyc` (ignorables, à ne pas versionner).

### 5.4 Rappel sur les données initiales
- `12.txt` contient **déjà** les ~167 références (avec doublons, voir R5) et les **12 utilisateurs initiaux** (1 Admin, 1 Editeur, 1 Utilisateur, 4 Cariste_Coulage, 5 Cariste_Emaillage). Ces données servent aux tests des phases 1 à 5 ; **aucun fichier externe n'est nécessaire dans l'immédiat**.

---

## 6. Stratégie de test générale

### 6.1 Approche par phase
- **Tester à chaque point d'arrêt**, jamais en fin de tout le projet.
- Chaque phase se teste selon des **scénarios utilisateur** (pas seulement « ça ne plante pas ») :
  - **Phase 1** : premier lancement → init Admin → connexion des 5 rôles → vérification boutons/compteurs → accès forcé refusé → changement MDP → déconnexion (voir 1.4).
  - **Phase 2** : cycle complet Nouveau → Sortie → Emaillage → Vide avec des wagons réels ; multi-références ; familles auto ; filtre tunnel ; couleurs des statuts.
  - **Phase 3** : vieillissement (forcer des dates) → AutoSortie 1/2 vs KEOS ; label discret sans popup ; modification des paramètres ; alertes au login.
  - **Phase 4** : CRUD utilisateurs ; recherche wagon (valide/invalide/introuvable) ; Auto Cull avec compteur.
  - **Phase 5** : import CSV réel (dédoublonnage, rapport) ; exécution du `.exe`.
- **Fiche de test type** : pour chaque fonction → *donnée d'entrée, action, résultat attendu, résultat obtenu, statut (OK/KO)*.
- **Tests de régression** : à chaque nouvelle phase, rejouer le test de connexion et de grille de la Phase 1 pour vérifier l'absence de régression.

### 6.2 Effet secondaire du SQLite sous OneDrive
- OneDrive peut **verrouiller, mettre en cache ou repliquer** le fichier SQLite (et ses fichiers `-journal` / `-wal`), provoquant des erreurs « database is locked », des lenteurs ou de la corruption.
- **Mesures** :
  - Marquer le dossier `Systeme_Chargement_V2026_Phase1` en **« Toujours conserver sur cet appareil »**.
  - Ne **jamais** lancer deux instances simultanément.
  - Toujours quitter par la déconnexion (fermeture propre) plutôt que de tuer le processus.
  - Pendant les tests, **mettre OneDrive en pause** si possible.
  - Sauvegarder `chargement.db` avant chaque session de test (copie datée).
  - Surveiller la présence de fichiers `chargement.db-journal` résiduels après fermeture (signe de problème).
- **Décision à moyen terme** : déplacer la base hors de OneDrive (ex. `C:\ProgramData\...` ou un dossier local non synchronisé) et ne laisser dans OneDrive que les sources — à étudier avant la mise en production.

---

## Annexe — Synthèse des décisions à rendre

| # | Point | Recommandation | Échéance |
|---|---|---|---|
| (d) | Visibilité Auto Cull / Menu / ChangerMDP | Auto Cull & Menu = Admin ; ChangerMDP = tous | **Phase 1** |
| (f) | Champs Changer MDP | Matricule + Ancien + Nouveau + Confirmation | **Phase 1** |
| (c) | Emplacement Coulage / Chariot | Colonnes de `chargement` | Phase 2 (corriger le schéma dès Phase 1) |
| (a) | Auto Cull | Archivage des wagons « Vide » + compteur | Phase 4 |
| (b) | Emaillage → Vide | Écran dédié, no_wagon, Cariste_Emaillage/Admin/Editeur | Phase 2 |
| (e) | Réutilisation no_wagon | V17 + archiver au lieu de supprimer | Phase 2 |
