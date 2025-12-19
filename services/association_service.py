"""
Service gérant la logique d'association aléatoire entre hommes et femmes.
"""
import random
from datetime import datetime
from storage.memory_store import store


class AssociationService:
    """
    Service pour gérer les associations aléatoires entre hommes et femmes.
    
    Règles:
    - Priorité: associer 1 homme + 1 femme tant que possible
    - Ensuite: associer les personnes restantes du même genre (F-F ou H-H)
    - Aucun numéro ne peut apparaître dans plus d'un couple
    """
    
    @staticmethod
    def create_random_associations():
        """
        Crée des associations aléatoires entre hommes et femmes.
        Récupère les listes directement depuis la base de données.
        
        Algorithme:
        1. Récupérer les hommes et femmes de la base de données
        2. Mélanger les deux listes aléatoirement
        3. Associer H-F tant que les deux listes contiennent des éléments
        4. Associer les femmes restantes entre elles (F-F)
        5. Associer les hommes restants entre eux (H-H)
        
        Returns:
            dict: Résultat de l'opération avec les couples créés
        """
        # Récupérer les hommes et femmes de la base de données
        hommes = store.get_hommes_numeros()
        femmes = store.get_femmes_numeros()
        
        # Vérifier qu'il y a des éléments à associer
        if not hommes and not femmes:
            return {
                "success": False,
                "error": "Aucune personne à associer. Ajoutez des hommes et/ou des femmes d'abord.",
                "timestamp": datetime.now().isoformat(timespec='seconds'),
                "couples": [],
                "statistiques": {
                    "total_personnes": 0,
                    "total_couples": 0,
                    "couples_H-F": 0,
                    "couples_F-F": 0,
                    "couples_H-H": 0,
                    "personnes_non_associees": 0
                }
            }
        
        # Copier les listes pour ne pas modifier les originales
        hommes_list = hommes.copy()
        femmes_list = femmes.copy()
        
        # Mélanger les deux listes aléatoirement
        random.shuffle(hommes_list)
        random.shuffle(femmes_list)
        
        couples = []
        
        # Étape 1: Associer H-F tant que possible
        while hommes_list and femmes_list:
            homme = hommes_list.pop()
            femme = femmes_list.pop()
            
            # Enregistrer dans la base de données
            store.add_couple("H-F", homme, femme)
            
            couples.append({
                "type": "H-F",
                "personne1": homme,
                "personne2": femme
            })
        
        # Étape 2: Associer les femmes restantes entre elles (F-F)
        while len(femmes_list) >= 2:
            femme1 = femmes_list.pop()
            femme2 = femmes_list.pop()
            
            store.add_couple("F-F", femme1, femme2)
            
            couples.append({
                "type": "F-F",
                "personne1": femme1,
                "personne2": femme2
            })
        
        # Étape 3: Associer les hommes restants entre eux (H-H)
        while len(hommes_list) >= 2:
            homme1 = hommes_list.pop()
            homme2 = hommes_list.pop()
            
            store.add_couple("H-H", homme1, homme2)
            
            couples.append({
                "type": "H-H",
                "personne1": homme1,
                "personne2": homme2
            })
        
        # Calculer les statistiques
        total_initial = len(hommes) + len(femmes)
        hf_count = sum(1 for c in couples if c['type'] == 'H-F')
        ff_count = sum(1 for c in couples if c['type'] == 'F-F')
        hh_count = sum(1 for c in couples if c['type'] == 'H-H')
        personnes_restantes = len(femmes_list) + len(hommes_list)
        
        return {
            "success": True,
            "message": f"{len(couples)} couple(s) créé(s)",
            "timestamp": datetime.now().isoformat(timespec='seconds'),
            "couples": couples,
            "statistiques": {
                "total_personnes": total_initial,
                "total_couples": len(couples),
                "couples_H-F": hf_count,
                "couples_F-F": ff_count,
                "couples_H-H": hh_count,
                "personnes_non_associees": personnes_restantes
            }
        }
    
    @staticmethod
    def validate_association_possible():
        """
        Vérifie si une association est possible.
        
        Returns:
            tuple: (bool, str) - (est_possible, message)
        """
        hommes = store.get_hommes_numeros()
        femmes = store.get_femmes_numeros()
        
        if not hommes and not femmes:
            return False, "Aucune personne disponible"
        
        return True, f"Association possible: {len(hommes)} homme(s) et {len(femmes)} femme(s)"


# Instance du service
association_service = AssociationService()
