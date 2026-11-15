"""Import des références depuis data/references.csv (INSERT OR IGNORE = dédoublonnage).

Usage :  python importer_references.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import db

CSV_PATH = Path(__file__).resolve().parent / "data" / "references.csv"


def importer() -> tuple[int, int]:
    db.initialiser_base()
    inseres, ignores = 0, 0
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as fichier:
        lecteur = csv.DictReader(fichier)
        with db.connexion() as con:
            for ligne in lecteur:
                reference = (ligne.get("Reference") or "").strip()
                famille = (ligne.get("Famille") or "").strip()
                if not reference:
                    continue
                curseur = con.execute(
                    "INSERT OR IGNORE INTO reference(reference, famille) VALUES (?, ?)",
                    (reference, famille or None),
                )
                if curseur.rowcount:
                    inseres += 1
                else:
                    ignores += 1
    return inseres, ignores


if __name__ == "__main__":
    inseres, ignores = importer()
    print(f"Références insérées : {inseres} | ignorées (doublons) : {ignores}")
