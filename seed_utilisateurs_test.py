"""Script de TEST uniquement — ne fait pas partie de l'application.

Insère les 11 utilisateurs initiaux (issus de 12.txt) avec un mot de passe
temporaire haché, afin de tester la grille de boutons par rôle en phase 1.
Cet outil sera remplacé par l'écran de gestion des utilisateurs (phase 4).

Usage :  python seed_utilisateurs_test.py
"""

import db
from services.authentification import hacher_mot_de_passe

# Matricule, Nom, Rôle (noms nettoyés des espaces parasites de 12.txt)
UTILISATEURS = (
    ("KE13583", "BAGGAR ABDESLAM", "Cariste_Coulage"),
    ("KE13361", "BENISSA ABDESLAM", "Cariste_Coulage"),
    ("KE13454", "HALIM EL MESHAM", "Cariste_Coulage"),
    ("KE05206", "ABDI MOUMEN MOAD", "Cariste_Coulage"),
    ("KE05031", "MANDILI MOHAMED", "Cariste_Emaillage"),
    ("KE13520", "BOUKHARI HAMID", "Cariste_Emaillage"),
    ("KE13480", "MESMOUDI ABDERAHIM", "Cariste_Emaillage"),
    ("KE13533", "NABIL ENNACIRI", "Cariste_Emaillage"),
    ("KE13517", "HAMMOU AHMED", "Utilisateur"),
    ("KE05304", "AMDAH ABDELHAK", "Cariste_Emaillage"),
    ("KE05087", "ABDESLAM EL HAOUARI", "Editeur"),
)

# Mot de passe temporaire commun (>= 8 caractères), à communiquer aux testeurs.
MOT_DE_PASSE_TEMPORAIRE = "Jacob2026!"


def main() -> None:
    db.initialiser_base()
    inseres, ignores = 0, 0
    with db.connexion() as con:
        for matricule, nom, role in UTILISATEURS:
            curseur = con.execute(
                """INSERT OR IGNORE INTO utilisateurs(matricule, nom_cariste, mot_de_passe, role)
                   VALUES (?, ?, ?, ?)""",
                (matricule, nom, hacher_mot_de_passe(MOT_DE_PASSE_TEMPORAIRE), role),
            )
            if curseur.rowcount:
                inseres += 1
            else:
                ignores += 1
    print(f"Utilisateurs insérés : {inseres} | déjà présents : {ignores}")


if __name__ == "__main__":
    main()
