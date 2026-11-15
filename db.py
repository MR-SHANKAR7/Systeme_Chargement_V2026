"""Accès SQLite. Les écrans n'exécutent jamais de SQL directement."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime

from config import DATA_DIR, DATABASE_PATH
from services.authentification import hacher_mot_de_passe, verifier_mot_de_passe
from session import UtilisateurConnecte


@contextmanager
def connexion():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DATABASE_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA busy_timeout = 5000")
    con.execute("PRAGMA journal_mode = WAL")
    con.execute("PRAGMA synchronous = NORMAL")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def initialiser_base() -> None:
    """Crée le schéma complet sans injecter de données métier."""
    with connexion() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id_cariste INTEGER PRIMARY KEY AUTOINCREMENT,
                matricule TEXT UNIQUE NOT NULL,
                nom_cariste TEXT NOT NULL,
                mot_de_passe TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN
                    ('Admin','Editeur','Cariste_Coulage','Cariste_Emaillage','Utilisateur'))
            );
            CREATE TABLE IF NOT EXISTS reference (
                id_reference INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT UNIQUE NOT NULL,
                famille TEXT
            );
            CREATE TABLE IF NOT EXISTS chargement (
                id_chargement INTEGER PRIMARY KEY AUTOINCREMENT,
                no_wagon INTEGER NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Nouveau','Sortie','Emaillage','Vide')),
                tunnel TEXT NOT NULL CHECK(tunnel IN ('1','2','KEOS')),
                date_chargement TEXT NOT NULL,
                id_cariste INTEGER,
                coulage TEXT,
                chariot TEXT,
                FOREIGN KEY(id_cariste) REFERENCES utilisateurs(id_cariste) ON DELETE SET NULL
            );
            CREATE TABLE IF NOT EXISTS detail_chargement (
                id_detail INTEGER PRIMARY KEY AUTOINCREMENT,
                id_chargement INTEGER NOT NULL,
                id_reference INTEGER NOT NULL,
                quantite INTEGER NOT NULL CHECK(quantite > 0),
                FOREIGN KEY(id_chargement) REFERENCES chargement(id_chargement) ON DELETE CASCADE,
                FOREIGN KEY(id_reference) REFERENCES reference(id_reference)
            );
            CREATE TABLE IF NOT EXISTS archive (
                id_archive INTEGER PRIMARY KEY AUTOINCREMENT,
                no_wagon INTEGER NOT NULL,
                status TEXT NOT NULL,
                tunnel TEXT NOT NULL,
                date_chargement TEXT NOT NULL,
                date_archivage TEXT NOT NULL,
                matricule_cariste TEXT,
                coulage TEXT,
                chariot TEXT,
                reference TEXT,
                famille TEXT,
                quantite INTEGER
            );
            CREATE TABLE IF NOT EXISTS parametres (
                cle TEXT PRIMARY KEY,
                valeur TEXT NOT NULL,
                description TEXT
            );
            """
        )
        for requete in (
            "CREATE INDEX IF NOT EXISTS idx_chargement_status_date ON chargement(status, date_chargement)",
            "CREATE INDEX IF NOT EXISTS idx_chargement_no_wagon ON chargement(no_wagon)",
            "CREATE INDEX IF NOT EXISTS idx_chargement_status_tunnel ON chargement(status, tunnel)",
            "CREATE INDEX IF NOT EXISTS idx_detail_chargement ON detail_chargement(id_chargement)",
            "CREATE INDEX IF NOT EXISTS idx_detail_reference ON detail_chargement(id_reference)",
        ):
            con.execute(requete)
        con.execute(
            "INSERT OR IGNORE INTO parametres(cle, valeur, description) VALUES (?, ?, ?)",
            ("HeuresAutoSortie", "12", "Délai automatique pour les tunnels 1 et 2"),
        )
        con.execute(
            "INSERT OR IGNORE INTO parametres(cle, valeur, description) VALUES (?, ?, ?)",
            ("Cle_KEOS", "12", "Délai automatique pour le tunnel KEOS"),
        )


def administrateur_initial_existe() -> bool:
    with connexion() as con:
        ligne = con.execute("SELECT 1 FROM utilisateurs LIMIT 1").fetchone()
    return ligne is not None


def creer_administrateur_initial(nom: str, mot_de_passe: str) -> None:
    with connexion() as con:
        con.execute(
            """INSERT INTO utilisateurs(matricule, nom_cariste, mot_de_passe, role)
               VALUES (?, ?, ?, 'Admin')""",
            ("KO05388", nom.strip(), hacher_mot_de_passe(mot_de_passe)),
        )


def authentifier(matricule: str, mot_de_passe: str) -> UtilisateurConnecte | None:
    with connexion() as con:
        ligne = con.execute(
            """SELECT id_cariste, matricule, nom_cariste, mot_de_passe, role
               FROM utilisateurs WHERE matricule = ?""",
            (matricule.strip().upper(),),
        ).fetchone()
    if ligne is None or not verifier_mot_de_passe(mot_de_passe, ligne["mot_de_passe"]):
        return None
    return UtilisateurConnecte(
        id_cariste=ligne["id_cariste"],
        matricule=ligne["matricule"],
        nom_cariste=ligne["nom_cariste"],
        role=ligne["role"],
    )


def changer_mot_de_passe(matricule: str, ancien: str, nouveau: str) -> bool:
    utilisateur = authentifier(matricule, ancien)
    if utilisateur is None:
        return False
    with connexion() as con:
        con.execute(
            "UPDATE utilisateurs SET mot_de_passe = ? WHERE id_cariste = ?",
            (hacher_mot_de_passe(nouveau), utilisateur.id_cariste),
        )
    return True


def compter_statuts() -> dict[str, int]:
    resultat = {"Nouveau": 0, "Sortie": 0, "Emaillage": 0, "Vide": 0, "Tout": 0, "Archive": 0}
    with connexion() as con:
        for ligne in con.execute("SELECT status, COUNT(*) AS total FROM chargement GROUP BY status"):
            resultat[ligne["status"]] = ligne["total"]
        resultat["Tout"] = con.execute("SELECT COUNT(*) FROM chargement").fetchone()[0]
        resultat["Archive"] = con.execute("SELECT COUNT(*) FROM archive").fetchone()[0]
    return resultat


def maintenant() -> str:
    """Date/heure courante au format 'YYYY-MM-DD HH:MM:SS' (tri chronologique)."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# --- Références -------------------------------------------------------------


def lister_references() -> list[sqlite3.Row]:
    with connexion() as con:
        return con.execute(
            "SELECT id_reference, reference, famille FROM reference ORDER BY reference"
        ).fetchall()


# --- Chargements ------------------------------------------------------------


def creer_chargement(
    no_wagon: int, tunnel: str, id_cariste: int, details, coulage: str, chariot: str
) -> int:
    """Crée un chargement 'Nouveau' et ses lignes de détail dans une transaction.

    `details` est une liste de tuples (id_reference, quantite).
    """
    with connexion() as con:
        curseur = con.execute(
            """INSERT INTO chargement(no_wagon, status, tunnel, date_chargement, id_cariste, coulage, chariot)
               VALUES (?, 'Nouveau', ?, ?, ?, ?, ?)""",
            (no_wagon, tunnel, maintenant(), id_cariste, coulage, chariot),
        )
        id_chargement = curseur.lastrowid
        for id_reference, quantite in details:
            con.execute(
                "INSERT INTO detail_chargement(id_chargement, id_reference, quantite) VALUES (?, ?, ?)",
                (id_chargement, id_reference, quantite),
            )
    return id_chargement


def trouver_wagon(no_wagon: int) -> sqlite3.Row | None:
    with connexion() as con:
        return con.execute(
            "SELECT * FROM chargement WHERE no_wagon = ?", (no_wagon,)
        ).fetchone()


def archiver_chargement(id_chargement: int) -> None:
    """Déplace un chargement (et ses détails) vers `archive`, puis le supprime."""
    with connexion() as con:
        ligne = con.execute(
            "SELECT * FROM chargement WHERE id_chargement = ?", (id_chargement,)
        ).fetchone()
        if ligne is None:
            return
        matricule = None
        if ligne["id_cariste"] is not None:
            m = con.execute(
                "SELECT matricule FROM utilisateurs WHERE id_cariste = ?",
                (ligne["id_cariste"],),
            ).fetchone()
            matricule = m["matricule"] if m else None
        details = con.execute(
            """SELECT d.quantite, r.reference, r.famille
               FROM detail_chargement d
               LEFT JOIN reference r ON r.id_reference = d.id_reference
               WHERE d.id_chargement = ?""",
            (id_chargement,),
        ).fetchall()
        if not details:
            details = [(None, None, None)]
        for quantite, reference, famille in details:
            con.execute(
                """INSERT INTO archive(no_wagon, status, tunnel, date_chargement, date_archivage,
                       matricule_cariste, coulage, chariot, reference, famille, quantite)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (ligne["no_wagon"], ligne["status"], ligne["tunnel"], ligne["date_chargement"],
                 maintenant(), matricule, ligne["coulage"], ligne["chariot"],
                 reference, famille, quantite),
            )
        con.execute("DELETE FROM chargement WHERE id_chargement = ?", (id_chargement,))


def passer_statut(no_wagon: int, statut_attendu: str, nouveau_statut: str) -> bool:
    """Transition gardée : ne s'applique que si le wagon est dans `statut_attendu`."""
    with connexion() as con:
        curseur = con.execute(
            "UPDATE chargement SET status = ?, date_chargement = ? WHERE no_wagon = ? AND status = ?",
            (nouveau_statut, maintenant(), no_wagon, statut_attendu),
        )
        return curseur.rowcount > 0


def lister_chargements(status=None, tunnel=None) -> list[sqlite3.Row]:
    """Liste aplatie (une ligne par référence) triée par date croissante."""
    requete = """
        SELECT c.id_chargement, c.no_wagon, c.status, c.tunnel, c.date_chargement,
               c.coulage, c.chariot, r.reference, r.famille, d.quantite
        FROM chargement c
        LEFT JOIN detail_chargement d ON d.id_chargement = c.id_chargement
        LEFT JOIN reference r ON r.id_reference = d.id_reference
        WHERE 1 = 1
    """
    parametres: list = []
    if status is not None:
        requete += " AND c.status = ?"
        parametres.append(status)
    if tunnel is not None:
        requete += " AND c.tunnel = ?"
        parametres.append(tunnel)
    requete += " ORDER BY c.date_chargement ASC, c.no_wagon ASC"
    with connexion() as con:
        return con.execute(requete, parametres).fetchall()


def lister_archive() -> list[sqlite3.Row]:
    with connexion() as con:
        return con.execute(
            "SELECT * FROM archive ORDER BY date_archivage ASC, date_chargement ASC"
        ).fetchall()


# --- Paramètres -------------------------------------------------------------


def lire_parametre_int(cle: str, defaut: int = 0) -> int:
    with connexion() as con:
        ligne = con.execute("SELECT valeur FROM parametres WHERE cle = ?", (cle,)).fetchone()
    if ligne is None:
        return defaut
    try:
        return int(ligne["valeur"])
    except (TypeError, ValueError):
        return defaut


def enregistrer_parametre(cle: str, valeur, description: str | None = None) -> None:
    """UPDATE si la clé existe, sinon INSERT."""
    with connexion() as con:
        curseur = con.execute(
            "UPDATE parametres SET valeur = ? WHERE cle = ?", (str(valeur), cle)
        )
        if curseur.rowcount == 0:
            con.execute(
                "INSERT INTO parametres(cle, valeur, description) VALUES (?, ?, ?)",
                (cle, str(valeur), description),
            )


# --- AutoSortie -------------------------------------------------------------


def basculer_nouveau_vers_sortie(tunnels, limite: datetime) -> int:
    """Transition auto Nouveau → Sortie pour les tunnels donnés si date <= limite."""
    limite_str = limite.strftime("%Y-%m-%d %H:%M:%S")
    marqueurs = ",".join("?" * len(tunnels))
    with connexion() as con:
        curseur = con.execute(
            f"""UPDATE chargement SET status = 'Sortie', date_chargement = ?
                WHERE status = 'Nouveau' AND tunnel IN ({marqueurs}) AND date_chargement <= ?""",
            (maintenant(), *tunnels, limite_str),
        )
        return curseur.rowcount


# --- Alertes ----------------------------------------------------------------


def wagons_en_retard(status: str, limite: datetime) -> list[sqlite3.Row]:
    limite_str = limite.strftime("%Y-%m-%d %H:%M:%S")
    with connexion() as con:
        return con.execute(
            """SELECT no_wagon, tunnel, date_chargement
               FROM chargement
               WHERE status = ? AND date_chargement <= ?
               ORDER BY date_chargement ASC""",
            (status, limite_str),
        ).fetchall()
