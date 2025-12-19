"""
Module de stockage en base de données pour l'application d'association.
Gère les hommes, femmes et leurs associations (couples).
"""
from storage.database import db, Homme, Femme, Couple


class DatabaseStore:
    """
    Classe pour gérer le stockage en base de données des données.
    Terminologie: Homme et Femme (représentés par des identifiants ex: H1, F2)
    """
    
    # ==================== GESTION DES HOMMES ====================
    
    def add_homme(self, numero):
        """
        Ajoute un homme à la base de données s'il n'existe pas déjà.
        
        Args:
            numero (str): L'identifiant de l'homme à ajouter (ex: H1)
            
        Returns:
            bool: True si ajouté, False si déjà existant
        """
        existing = Homme.query.filter_by(numero=numero, is_archived=False).first()
        if existing:
            return False
        
        new_homme = Homme(numero=numero)
        db.session.add(new_homme)
        db.session.commit()
        return True
    
    def add_hommes_bulk(self, numeros):
        """
        Ajoute plusieurs hommes en une seule opération.
        
        Args:
            numeros (list): Liste des identifiants à ajouter (ex: ["H1", "H2"])
            
        Returns:
            dict: Résultat avec hommes ajoutés et ignorés
        """
        added = []
        ignored = []
        
        for numero in numeros:
            if self.add_homme(numero):
                added.append(numero)
            else:
                ignored.append(numero)
        
        return {"added": added, "ignored": ignored}
    
    def remove_homme(self, numero):
        """
        Archive un homme (soft delete).
        
        Args:
            numero (str): L'identifiant de l'homme à archiver (ex: H1)
            
        Returns:
            bool: True si archivé, False si non trouvé
        """
        homme = Homme.query.filter_by(numero=numero, is_archived=False).first()
        if not homme:
            return False
        
        homme.is_archived = True
        db.session.commit()
        return True
    
    def get_hommes(self):
        """
        Retourne tous les hommes non archivés.
        
        Returns:
            list: Liste de dictionnaires avec les données des hommes
        """
        hommes = Homme.query.filter_by(is_archived=False).all()
        return [homme.to_dict() for homme in hommes]
    
    def get_hommes_numeros(self):
        """
        Retourne uniquement les identifiants des hommes non archivés.
        
        Returns:
            list: Liste des identifiants (ex: ["H1", "H2"])
        """
        hommes = Homme.query.filter_by(is_archived=False).all()
        return [homme.numero for homme in hommes]
    
    # ==================== GESTION DES FEMMES ====================
    
    def add_femme(self, numero):
        """
        Ajoute une femme à la base de données si elle n'existe pas déjà.
        
        Args:
            numero (str): L'identifiant de la femme à ajouter (ex: F1)
            
        Returns:
            bool: True si ajoutée, False si déjà existante
        """
        existing = Femme.query.filter_by(numero=numero, is_archived=False).first()
        if existing:
            return False
        
        new_femme = Femme(numero=numero)
        db.session.add(new_femme)
        db.session.commit()
        return True
    
    def add_femmes_bulk(self, numeros):
        """
        Ajoute plusieurs femmes en une seule opération.
        
        Args:
            numeros (list): Liste des identifiants à ajouter (ex: ["F1", "F2"])
            
        Returns:
            dict: Résultat avec femmes ajoutées et ignorées
        """
        added = []
        ignored = []
        
        for numero in numeros:
            if self.add_femme(numero):
                added.append(numero)
            else:
                ignored.append(numero)
        
        return {"added": added, "ignored": ignored}
    
    def remove_femme(self, numero):
        """
        Archive une femme (soft delete).
        
        Args:
            numero (str): L'identifiant de la femme à archiver (ex: F1)
            
        Returns:
            bool: True si archivée, False si non trouvée
        """
        femme = Femme.query.filter_by(numero=numero, is_archived=False).first()
        if not femme:
            return False
        
        femme.is_archived = True
        db.session.commit()
        return True
    
    def get_femmes(self):
        """
        Retourne toutes les femmes non archivées.
        
        Returns:
            list: Liste de dictionnaires avec les données des femmes
        """
        femmes = Femme.query.filter_by(is_archived=False).all()
        return [femme.to_dict() for femme in femmes]
    
    def get_femmes_numeros(self):
        """
        Retourne uniquement les identifiants des femmes non archivées.
        
        Returns:
            list: Liste des identifiants (ex: ["F1", "F2"])
        """
        femmes = Femme.query.filter_by(is_archived=False).all()
        return [femme.numero for femme in femmes]
    
    # ==================== GESTION DES COUPLES ====================
    
    def add_couple(self, type_couple, personne1, personne2):
        """
        Crée un couple/association.
        
        Args:
            type_couple (str): Type de couple ('H-F', 'H-H', 'F-F')
            personne1 (str): Identifiant de la première personne (ex: H1)
            personne2 (str): Identifiant de la deuxième personne (ex: F1)
            
        Returns:
            bool: True si créé
        """
        new_couple = Couple(
            type_couple=type_couple,
            personne1=personne1,
            personne2=personne2
        )
        db.session.add(new_couple)
        db.session.commit()
        return True
    
    def get_couples(self):
        """
        Retourne tous les couples non archivés.
        
        Returns:
            list: Liste des couples
        """
        couples = Couple.query.filter_by(is_archived=False).all()
        return [couple.to_dict() for couple in couples]
    
    def get_status(self):
        """
        Retourne l'état complet du système.
        
        Returns:
            dict: Statistiques et détails des données
        """
        all_hommes = Homme.query.filter_by(is_archived=False).all()
        all_femmes = Femme.query.filter_by(is_archived=False).all()
        all_couples = Couple.query.filter_by(is_archived=False).all()
        
        # Compter les types de couples
        hf_count = sum(1 for c in all_couples if c.type_couple == 'H-F')
        hh_count = sum(1 for c in all_couples if c.type_couple == 'H-H')
        ff_count = sum(1 for c in all_couples if c.type_couple == 'F-F')
        
        return {
            "participants": {
                "total": len(all_hommes),
                "list": [h.numero for h in all_hommes]
            },
            "gifts": {
                "total": len(all_femmes),
                "list": [f.numero for f in all_femmes]
            },
            "associations": {
                "total": len(all_couples),
                "H-F": hf_count,
                "H-H": hh_count,
                "F-F": ff_count,
                "details": [c.to_dict() for c in all_couples]
            }
        }
    
    def reset(self):
        """Réinitialise toutes les données."""
        Couple.query.delete()
        Homme.query.delete()
        Femme.query.delete()
        db.session.commit()
    
    def reset_couples(self):
        """Réinitialise uniquement les couples."""
        couples_count = Couple.query.filter_by(is_archived=False).count()
        Couple.query.filter_by(is_archived=False).delete()
        db.session.commit()
        return couples_count
    
    # ==================== PROPRIÉTÉS DE COMPATIBILITÉ ====================
    
    @property
    def hommes(self):
        """Retourne la liste des numéros d'hommes."""
        return self.get_hommes_numeros()
    
    @property
    def femmes(self):
        """Retourne la liste des numéros de femmes."""
        return self.get_femmes_numeros()
    
    # Aliases pour compatibilité avec les anciennes routes
    def add_participant(self, numero):
        """Alias pour add_homme (compatibilité route /participants)."""
        return self.add_homme(int(numero) if isinstance(numero, str) and numero.isdigit() else numero)
    
    def add_participants_bulk(self, numeros):
        """Alias pour add_hommes_bulk."""
        return self.add_hommes_bulk(numeros)
    
    def remove_participant(self, numero):
        """Alias pour remove_homme."""
        return self.remove_homme(int(numero) if isinstance(numero, str) and numero.isdigit() else numero)
    
    def get_participants(self):
        """Alias pour get_hommes."""
        return self.get_hommes()
    
    def add_gift(self, numero):
        """Alias pour add_femme (compatibilité route /gifts)."""
        return self.add_femme(numero)
    
    def add_gifts_bulk(self, numeros):
        """Alias pour add_femmes_bulk."""
        return self.add_femmes_bulk(numeros)
    
    def remove_gift(self, numero):
        """Alias pour remove_femme."""
        return self.remove_femme(numero)
    
    def get_gifts(self):
        """Alias pour get_femmes."""
        return self.get_femmes()
    
    @property
    def participants(self):
        """Alias pour hommes."""
        return self.hommes
    
    @property
    def gifts(self):
        """Alias pour femmes."""
        return self.femmes


# Instance du store
store = DatabaseStore()
