"""Point d'entrée de Systeme_Chargement."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import db
from config import COLOR_BACKGROUND, COLOR_BLUE, COLOR_GOLD, COLOR_MUTED, COLOR_NAVY, COLOR_TEXT, COLOR_WHITE
from session import session
from ui.accueil import Accueil
from ui.login import FenetreConnexion, InitialisationAdmin


class Application(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Systeme de Chargement · V2026")
        self.minsize(1060, 680)
        self.configure(bg=COLOR_BACKGROUND)
        self._configurer_styles()
        db.initialiser_base()
        self.ecran = None
        self.afficher_connexion()
        if not db.administrateur_initial_existe():
            self.after(150, lambda: InitialisationAdmin(self))

    def _configurer_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=COLOR_BACKGROUND)
        style.configure("Card.TFrame", background=COLOR_WHITE)
        style.configure("TLabel", background=COLOR_BACKGROUND, foreground=COLOR_TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=COLOR_WHITE, foreground=COLOR_NAVY, font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", background=COLOR_WHITE, foreground=COLOR_MUTED, font=("Segoe UI", 11))
        style.configure("Brand.TLabel", background=COLOR_WHITE, foreground=COLOR_NAVY, font=("Segoe UI", 24, "bold"))
        style.configure("Version.TLabel", background=COLOR_WHITE, foreground=COLOR_MUTED, font=("Segoe UI", 9))
        style.configure("ReadOnly.TLabel", background=COLOR_WHITE, foreground=COLOR_NAVY, font=("Segoe UI", 11, "bold"))
        style.configure("CounterName.TLabel", background=COLOR_WHITE, foreground=COLOR_MUTED, font=("Segoe UI", 9, "bold"))
        style.configure("CounterValue.TLabel", background=COLOR_WHITE, foreground=COLOR_NAVY, font=("Segoe UI", 24, "bold"))
        style.configure("ActionTitle.TLabel", background=COLOR_WHITE, foreground=COLOR_NAVY, font=("Segoe UI", 14, "bold"))
        style.configure("ActionHint.TLabel", background=COLOR_WHITE, foreground=COLOR_MUTED, font=("Segoe UI", 9))
        style.configure("TButton", font=("Segoe UI", 11), padding=(12, 8))
        style.configure("Primary.TButton", background=COLOR_BLUE, foreground=COLOR_WHITE, borderwidth=0)
        style.map("Primary.TButton", background=[("active", "#2577AB")])
        style.configure("Gold.TButton", background=COLOR_GOLD, foreground=COLOR_NAVY, borderwidth=0)
        style.map("Gold.TButton", background=[("active", "#B8943E")])
        style.configure("TEntry", fieldbackground=COLOR_WHITE, padding=7)

    def remplacer_ecran(self, ecran) -> None:
        if self.ecran is not None:
            self.ecran.destroy()
        self.ecran = ecran
        self.ecran.pack(fill="both", expand=True)

    def afficher_connexion(self) -> None:
        self.remplacer_ecran(FenetreConnexion(self, self.ouvrir_accueil))

    def ouvrir_accueil(self, utilisateur) -> None:
        session.ouvrir(utilisateur)
        self.state("zoomed")
        self.remplacer_ecran(Accueil(self, self.deconnecter))

    def deconnecter(self) -> None:
        session.fermer()
        self.destroy()


if __name__ == "__main__":
    Application().mainloop()
