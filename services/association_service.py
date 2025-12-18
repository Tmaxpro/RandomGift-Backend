"""
Service gérant la logique d'association aléatoire entre participants et cadeaux.
"""
import random
from storage.memory_store import store


class AssociationService:
    """
    Service pour gérer les associations aléatoires entre participants et cadeaux.
    """
    
    @staticmethod
    def create_random_associations():
        """
        Crée des associations aléatoires entre participants et cadeaux non associés.
        
        Règles:
        - Seuls les participants et cadeaux non associés sont utilisés
        - Le nombre de participants non associés doit être ≤ au nombre de cadeaux non associés
        - Les associations existantes ne sont jamais modifiées
        
        Returns:
            dict: Résultat de l'opération avec nouvelles associations et total
            
        Raises:
            ValueError: Si pas assez de cadeaux disponibles
        """
        # Récupérer les éléments non associés
        unassociated_participants = store.get_unassociated_participants()
        unassociated_gifts = store.get_unassociated_gifts()
        
        # Vérifier qu'il y a des éléments à associer
        if not unassociated_participants:
            return {
                "success": True,
                "message": "Aucun participant à associer",
                "new_associations": [],
                "total_associations": store.get_associations()
            }
        
        if not unassociated_gifts:
            return {
                "success": False,
                "message": "Aucun cadeau disponible pour l'association",
                "new_associations": [],
                "total_associations": store.get_associations()
            }
        
        # Vérifier qu'il y a assez de cadeaux
        if len(unassociated_participants) > len(unassociated_gifts):
            return {
                "success": False,
                "message": f"Pas assez de cadeaux disponibles. Participants: {len(unassociated_participants)}, Cadeaux: {len(unassociated_gifts)}",
                "new_associations": [],
                "total_associations": store.get_associations()
            }
        
        # Mélanger les cadeaux pour assurer le caractère aléatoire
        shuffled_gifts = unassociated_gifts.copy()
        random.shuffle(shuffled_gifts)
        
        # Créer les associations
        new_associations = []
        for i, participant in enumerate(unassociated_participants):
            gift = shuffled_gifts[i]
            store.add_association(participant, gift)
            new_associations.append({
                "participant": participant,
                "gift": gift
            })
        
        return {
            "success": True,
            "message": f"{len(new_associations)} nouvelle(s) association(s) créée(s)",
            "new_associations": new_associations,
            "total_associations": store.get_associations()
        }
    
    @staticmethod
    def validate_association_possible():
        """
        Vérifie si une association est possible.
        
        Returns:
            tuple: (bool, str) - (est_possible, message)
        """
        unassociated_participants = store.get_unassociated_participants()
        unassociated_gifts = store.get_unassociated_gifts()
        
        if not unassociated_participants:
            return False, "Aucun participant non associé disponible"
        
        if not unassociated_gifts:
            return False, "Aucun cadeau non associé disponible"
        
        if len(unassociated_participants) > len(unassociated_gifts):
            return False, f"Pas assez de cadeaux. Participants: {len(unassociated_participants)}, Cadeaux: {len(unassociated_gifts)}"
        
        return True, "Association possible"


# Instance du service
association_service = AssociationService()
