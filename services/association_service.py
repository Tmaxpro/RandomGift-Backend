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
        - Chaque cadeau disponible est associé à un participant aléatoire
        - Si il y a plus de participants que de cadeaux, seuls certains participants seront associés
        - Les associations existantes ne sont jamais modifiées
        
        Returns:
            dict: Résultat de l'opération avec nouvelles associations et total
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
        
        # Mélanger les participants pour choisir aléatoirement
        shuffled_participants = unassociated_participants.copy()
        random.shuffle(shuffled_participants)
        
        # Créer les associations: on associe tous les cadeaux disponibles
        # à des participants choisis aléatoirement
        new_associations = []
        num_associations = min(len(unassociated_gifts), len(unassociated_participants))
        
        for i in range(num_associations):
            participant = shuffled_participants[i]
            gift = unassociated_gifts[i]
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
        
        return True, f"Association possible: {len(unassociated_gifts)} cadeau(x) seront associés"


# Instance du service
association_service = AssociationService()
