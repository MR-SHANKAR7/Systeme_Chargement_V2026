    def show_home(self):
        user = self.current_user
        card = self.make_card(
            "Accueil",
            f"Bienvenue, {user['username']} — Atelier Coulage Vitreous",
        )

        role_label = "Administrateur" if user["role"] == "admin" else "Opérateur"
        ttk.Label(card, text=f"Rôle : {role_label}").pack(pady=(0, 18))

        # زر جديد لإدخال الصب (متاح للجميع)
        ttk.Button(
            card,
            text="Saisie du Coulage",
            command=self.show_coulage_entry,
        ).pack(fill="x", pady=4)

        if user["role"] == "admin":
            ttk.Button(
                card,
                text="Menu administrateur",
                command=self.show_admin_menu,
            ).pack(fill="x", pady=4)

        ttk.Button(
            card,
            text="Changer le mot de passe",
            command=self.show_change_password,
        ).pack(fill="x", pady=4)
        ttk.Button(card, text="Déconnexion", command=self.logout).pack(
            fill="x", pady=4
        )

    def show_coulage_entry(self):
        card = self.make_card("Saisie du Coulage", "Enregistrez une nouvelle opération de coulage.")
        
        ttk.Label(card, text="Numéro du Wagon").pack(anchor="w")
        wagon_entry = ttk.Entry(card, width=38)
        wagon_entry.pack(fill="x", pady=(4, 12))
        
        ttk.Label(card, text="Date de Coulage").pack(anchor="w")
        date_entry = ttk.Entry(card, width=38)
        date_entry.insert(0, "YYYY-MM-DD") # تلميح للتاريخ
        date_entry.pack(fill="x", pady=(4, 12))
        
        def submit():
            w_id = wagon_entry.get().strip()
            d_coul = date_entry.get().strip()
            if not w_id or not d_coul:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
                return
            
            try:
                # تحويل رقم العربة إلى رقم صحيح
                wagon_id = int(w_id)
                database.register_coulage(wagon_id, d_coul, self.current_user['id'])
                messagebox.showinfo("Succès", f"Wagon {wagon_id} enregistré avec succès.")
                self.show_home()
            except ValueError:
                messagebox.showerror("Erreur", "Le numéro du wagon doit être un nombre.")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        ttk.Button(card, text="Enregistrer", command=submit).pack(fill="x", pady=(4, 0))
        ttk.Button(card, text="Retour", command=self.show_home).pack(fill="x", pady=4)
