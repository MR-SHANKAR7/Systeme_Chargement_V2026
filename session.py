"""État de la session applicative courante."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UtilisateurConnecte:
    id_cariste: int
    matricule: str
    nom_cariste: str
    role: str


class Session:
    def __init__(self) -> None:
        self.utilisateur: UtilisateurConnecte | None = None

    def ouvrir(self, utilisateur: UtilisateurConnecte) -> None:
        self.utilisateur = utilisateur

    def fermer(self) -> None:
        self.utilisateur = None

    @property
    def est_connectee(self) -> bool:
        return self.utilisateur is not None


session = Session()
