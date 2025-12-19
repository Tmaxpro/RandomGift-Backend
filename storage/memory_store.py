"""
Module de stockage en base de données pour l'application d'association.
Gère les participants, cadeaux et leurs associations avec SQLite.
"""
from storage.database import db, Participant, Gift, Association


class DatabaseStore:
    """
    Classe pour gérer le stockage en base de données des données.
    """
    
    def add_participant(self, participant):
        """
        Ajoute un participant à la base de données s'il n'existe pas déjà.
        
        Args:
            participant (str): Le participant à ajouter
            
        Returns:
            bool: True si ajouté, False si déjà existant
        """
        existing = Participant.query.filter_by(participant=participant, is_archived=False).first()
        if existing:
            return False
        
        new_participant = Participant(participant=participant)
        db.session.add(new_participant)
        db.session.commit()
        return True
    
    def add_participants_bulk(self, participants):
        """
        Ajoute plusieurs participants en une seule opération.
        
        Args:
            participants (list): Liste des participants à ajouter
            
        Returns:
            dict: Résultat avec participants ajoutés et ignorés
        """
        added = []
        ignored = []
        
        for participant in participants:
            if self.add_participant(participant):
                added.append(participant)
            else:
                ignored.append(participant)
        
        return {"added": added, "ignored": ignored}
    
    def remove_participant(self, participant):
        """
        Archive un participant (soft delete) et son association éventuelle.
        
        Args:
            participant (str): Le participant à archiver
            
        Returns:
            bool: True si archivé, False si non trouvé
        """
        participant_obj = Participant.query.filter_by(participant=participant, is_archived=False).first()
        if not participant_obj:
            return False
        
        # Archiver le participant
        participant_obj.is_archived = True
        
        # Archiver son association si elle existe
        association = Association.query.filter_by(participant=participant, is_archived=False).first()
        if association:
            association.is_archived = True
        
        db.session.commit()
        return True
    
    def get_participants(self):
        """
        Retourne tous les participants non archivés avec leur statut d'association.
        
        Returns:
            list: Liste de dictionnaires avec participant et statut
        """
        participants = Participant.query.filter_by(is_archived=False).all()
        return [participant.to_dict() for participant in participants]
    
    def add_gift(self, gift):
        """
        Ajoute un cadeau à la base de données s'il n'existe pas déjà.
        
        Args:
            gift (int): Le cadeau à ajouter
            
        Returns:
            bool: True si ajouté, False si déjà existant
        """
        existing = Gift.query.filter_by(gift=gift, is_archived=False).first()
        if existing:
            return False
        
        new_gift = Gift(gift=gift)
        db.session.add(new_gift)
        db.session.commit()
        return True
    
    def add_gifts_bulk(self, gifts):
        """
        Ajoute plusieurs cadeaux en une seule opération.
        
        Args:
            gifts (list): Liste des cadeaux à ajouter
            
        Returns:
            dict: Résultat avec cadeaux ajoutés et ignorés
        """
        added = []
        ignored = []
        
        for gift in gifts:
            if self.add_gift(gift):
                added.append(gift)
            else:
                ignored.append(gift)
        
        return {"added": added, "ignored": ignored}
    
    def remove_gift(self, gift):
        """
        Archive un cadeau (soft delete) et son association éventuelle.
        
        Args:
            gift (int): Le cadeau à archiver
            
        Returns:
            bool: True si archivé, False si non trouvé
        """
        gift_obj = Gift.query.filter_by(gift=gift, is_archived=False).first()
        if not gift_obj:
            return False
        
        # Archiver le cadeau
        gift_obj.is_archived = True
        
        # Archiver son association si elle existe
        association = Association.query.filter_by(gift=gift, is_archived=False).first()
        if association:
            association.is_archived = True
        
        db.session.commit()
        return True
    
    def get_gifts(self):
        """
        Retourne tous les cadeaux non archivés avec leur statut d'association.
        
        Returns:
            list: Liste de dictionnaires avec cadeau et statut
        """
        gifts = Gift.query.filter_by(is_archived=False).all()
        return [gift.to_dict() for gift in gifts]
    
    def get_unassociated_participants(self):
        """
        Retourne les participants non encore associés et non archivés.
        
        Returns:
            list: Liste des participants non associés
        """
        # Requête pour trouver les participants non archivés sans association non archivée
        participants = Participant.query.filter_by(is_archived=False).outerjoin(
            Association, 
            (Participant.participant == Association.participant) & (Association.is_archived == False)
        ).filter(Association.id == None).all()
        return [participant.participant for participant in participants]
    
    def get_unassociated_gifts(self):
        """
        Retourne les cadeaux non encore associés et non archivés.
        
        Returns:
            list: Liste des cadeaux non associés
        """
        # Requête pour trouver les cadeaux non archivés sans association non archivée
        gifts = Gift.query.filter_by(is_archived=False).outerjoin(
            Association,
            (Gift.gift == Association.gift) & (Association.is_archived == False)
        ).filter(Association.id == None).all()
        return [gift.gift for gift in gifts]
    
    def add_association(self, participant, gift):
        """
        Crée une association entre un participant et un cadeau.
        
        Args:
            participant (str): Le participant
            gift (int): Le cadeau
            
        Returns:
            bool: True si créée, False si déjà existante
        """
        existing = Association.query.filter_by(participant=participant, is_archived=False).first()
        if existing:
            return False
        
        new_association = Association(participant=participant, gift=gift)
        db.session.add(new_association)
        db.session.commit()
        return True
    
    def remove_association(self, participant):
        """
        Archive l'association d'un participant (soft delete).
        
        Args:
            participant (str): Le participant dont l'association doit être archivée
            
        Returns:
            bool: True si archivée, False si non trouvée
        """
        association = Association.query.filter_by(participant=participant, is_archived=False).first()
        if not association:
            return False
        
        association.is_archived = True
        db.session.commit()
        return True
    
    def get_associations(self):
        """
        Retourne toutes les associations non archivées.
        
        Returns:
            dict: Dictionnaire des associations {participant: cadeau}
        """
        associations = Association.query.filter_by(is_archived=False).all()
        return {assoc.participant: assoc.gift for assoc in associations}
    
    def get_status(self):
        """
        Retourne l'état complet du système (seulement éléments non archivés).
        
        Returns:
            dict: Statistiques et détails des données
        """
        all_participants = Participant.query.filter_by(is_archived=False).all()
        all_gifts = Gift.query.filter_by(is_archived=False).all()
        all_associations = Association.query.filter_by(is_archived=False).all()
        
        associated_participants = [assoc.participant for assoc in all_associations]
        associated_gifts = [assoc.gift for assoc in all_associations]
        
        unassociated_participants = [participant.participant for participant in all_participants if participant.participant not in associated_participants]
        unassociated_gifts = [gift.gift for gift in all_gifts if gift.gift not in associated_gifts]
        
        return {
            "participants": {
                "total": len(all_participants),
                "associated": len(associated_participants),
                "unassociated": len(unassociated_participants),
                "list_associated": associated_participants,
                "list_unassociated": unassociated_participants
            },
            "gifts": {
                "total": len(all_gifts),
                "associated": len(associated_gifts),
                "unassociated": len(unassociated_gifts),
                "list_associated": associated_gifts,
                "list_unassociated": unassociated_gifts
            },
            "associations": {
                "total": len(all_associations),
                "details": {assoc.participant: assoc.gift for assoc in all_associations}
            }
        }
    
    def reset(self):
        """Réinitialise toutes les données."""
        # Supprimer toutes les associations d'abord (à cause des contraintes de clés étrangères)
        Association.query.delete()
        # Puis supprimer les participants et cadeaux
        Participant.query.delete()
        Gift.query.delete()
        db.session.commit()
    
    def reset_associations(self):
        """Réinitialise uniquement les associations (les participants et cadeaux sont conservés)."""
        associations_count = Association.query.filter_by(is_archived=False).count()
        # Supprimer toutes les associations non archivées (hard delete pour permettre la réattribution)
        Association.query.filter_by(is_archived=False).delete()
        db.session.commit()
        return associations_count
    
    @property
    def participants(self):
        """Propriété pour compatibilité - retourne la liste des participants non archivés."""
        return [participant.participant for participant in Participant.query.filter_by(is_archived=False).all()]
    
    @property
    def gifts(self):
        """Propriété pour compatibilité - retourne la liste des cadeaux non archivés."""
        return [gift.gift for gift in Gift.query.filter_by(is_archived=False).all()]
    
    @property
    def associations(self):
        """Propriété pour compatibilité - retourne le dictionnaire des associations."""
        return self.get_associations()


# Instance du store
store = DatabaseStore()
