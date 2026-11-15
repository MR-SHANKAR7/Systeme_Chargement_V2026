"""Constantes visuelles et fonctionnelles de Systeme_Chargement."""

from pathlib import Path


APP_NAME = "Systeme de Chargement"
APP_VERSION = "V2026"
COMPANY_NAME = "KOHLER Co. · Jacob Delafon Africa"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "chargement.db"

COLOR_NAVY = "#1B3A5C"
COLOR_BLUE = "#2E86C1"
COLOR_GOLD = "#C9A84C"
COLOR_BACKGROUND = "#F0F4F8"
COLOR_WHITE = "#FFFFFF"
COLOR_TEXT = "#172B3A"
COLOR_MUTED = "#5E6C78"
COLOR_SUCCESS = "#2F855A"
COLOR_WARNING = "#B45309"
COLOR_DANGER = "#C53030"
COLOR_GRAY = "#6B7280"
COLOR_NAVY_HOVER = "#14293F"
COLOR_BLUE_HOVER = "#2577AB"

# Couleurs des badges de statut (contraste WCAG ≥ 4,5:1 sur fond blanc).
STATUS_COLORS = {
    "Nouveau": "#1F6FA0",   # bleu
    "Sortie": "#B45309",    # orange
    "Emaillage": "#2F855A", # vert
    "Vide": "#6B7280",      # gris
}

ALL_ROLES = (
    "Admin",
    "Editeur",
    "Cariste_Coulage",
    "Cariste_Emaillage",
    "Utilisateur",
)

ROLE_LABELS = {
    "Admin": "Administrateur",
    "Editeur": "Éditeur",
    "Cariste_Coulage": "Cariste Coulage",
    "Cariste_Emaillage": "Cariste Émaillage",
    "Utilisateur": "Utilisateur",
}

