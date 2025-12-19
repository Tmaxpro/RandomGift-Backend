"""
Service gérant la logique d'association aléatoire entre hommes et femmes.
Implémente l'algorithme de tirage au sort avec priorité H-F, puis même genre.
"""
import random
from datetime import datetime
from typing import List, Dict, Any, Tuple


class GenderAssociationService:
    """
    Service pour gérer les associations aléatoires entre personnes.
    
    Règles:
    - Priorité: associer 1 homme + 1 femme tant que possible
    - Ensuite: associer les personnes restantes du même genre
    - Aucun numéro ne peut apparaître dans plus d'un couple
    """
    
    @staticmethod
    def validate_input(data: Dict) -> Tuple[bool, str, Dict]:
        """
        Valide les données d'entrée de l'API.
        
        Args:
            data: Données JSON reçues
            
        Returns:
            Tuple: (is_valid, error_message, validated_data)
        """
        if not data:
            return False, "Données JSON manquantes", {}
        
        # Vérifier la présence des deux listes
        if 'femmes' not in data:
            return False, "La liste 'femmes' est requise", {}
        
        if 'hommes' not in data:
            return False, "La liste 'hommes' est requise", {}
        
        femmes = data.get('femmes', [])
        hommes = data.get('hommes', [])
        
        # Vérifier que ce sont des listes
        if not isinstance(femmes, list):
            return False, "Le champ 'femmes' doit être une liste", {}
        
        if not isinstance(hommes, list):
            return False, "Le champ 'hommes' doit être une liste", {}
        
        # Vérifier que les listes ne sont pas vides
        if len(femmes) == 0 and len(hommes) == 0:
            return False, "Au moins une des listes doit contenir des participants", {}
        
        # Vérifier que tous les éléments sont des nombres
        for i, num in enumerate(femmes):
            if not isinstance(num, (int, float)) or isinstance(num, bool):
                return False, f"L'élément à l'index {i} de 'femmes' doit être un nombre", {}
        
        for i, num in enumerate(hommes):
            if not isinstance(num, (int, float)) or isinstance(num, bool):
                return False, f"L'élément à l'index {i} de 'hommes' doit être un nombre", {}
        
        # Convertir en entiers
        femmes = [int(f) for f in femmes]
        hommes = [int(h) for h in hommes]
        
        # Vérifier l'unicité dans chaque liste
        if len(femmes) != len(set(femmes)):
            return False, "La liste 'femmes' contient des doublons", {}
        
        if len(hommes) != len(set(hommes)):
            return False, "La liste 'hommes' contient des doublons", {}
        
        # Vérifier qu'il n'y a pas de numéros en commun entre les deux listes
        common = set(femmes) & set(hommes)
        if common:
            return False, f"Les numéros suivants apparaissent dans les deux listes: {list(common)}", {}
        
        return True, "", {"femmes": femmes, "hommes": hommes}
    
    @staticmethod
    def create_associations(femmes: List[int], hommes: List[int]) -> List[Dict[str, Any]]:
        """
        Crée des associations selon l'algorithme spécifié.
        
        Algorithme:
        1. Copier et mélanger les deux listes aléatoirement
        2. Associer H-F tant que les deux listes contiennent des éléments
        3. Associer les femmes restantes entre elles (F-F)
        4. Associer les hommes restants entre eux (H-H)
        
        Args:
            femmes: Liste des numéros représentant les femmes
            hommes: Liste des numéros représentant les hommes
            
        Returns:
            Liste de couples avec leur type d'association
        """
        # Copier les listes pour ne pas modifier les originales
        femmes_list = femmes.copy()
        hommes_list = hommes.copy()
        
        # Mélanger les deux listes aléatoirement
        random.shuffle(femmes_list)
        random.shuffle(hommes_list)
        
        couples = []
        
        # Étape 1: Associer H-F tant que possible
        while femmes_list and hommes_list:
            homme = hommes_list.pop()
            femme = femmes_list.pop()
            couples.append({
                "type": "H-F",
                "personne1": homme,
                "personne2": femme
            })
        
        # Étape 2: Associer les femmes restantes entre elles (F-F)
        while len(femmes_list) >= 2:
            femme1 = femmes_list.pop()
            femme2 = femmes_list.pop()
            couples.append({
                "type": "F-F",
                "personne1": femme1,
                "personne2": femme2
            })
        
        # Étape 3: Associer les hommes restants entre eux (H-H)
        while len(hommes_list) >= 2:
            homme1 = hommes_list.pop()
            homme2 = hommes_list.pop()
            couples.append({
                "type": "H-H",
                "personne1": homme1,
                "personne2": homme2
            })
        
        # Note: S'il reste une personne seule (nombre impair total),
        # elle ne sera pas associée
        
        return couples
    
    def associate(self, data: Dict) -> Dict[str, Any]:
        """
        Point d'entrée principal pour l'association.
        Valide les données et exécute l'algorithme d'association.
        
        Args:
            data: Données JSON de la requête
            
        Returns:
            Résultat structuré avec timestamp et couples
        """
        # Valider les données d'entrée
        is_valid, error_msg, validated_data = self.validate_input(data)
        
        if not is_valid:
            return {
                "success": False,
                "error": error_msg
            }
        
        femmes = validated_data['femmes']
        hommes = validated_data['hommes']
        
        # Créer les associations
        couples = self.create_associations(femmes, hommes)
        
        # Calculer les statistiques
        total_personnes = len(femmes) + len(hommes)
        personnes_associees = len(couples) * 2
        personne_seule = total_personnes - personnes_associees
        
        # Compter les types
        hf_count = sum(1 for c in couples if c['type'] == 'H-F')
        ff_count = sum(1 for c in couples if c['type'] == 'F-F')
        hh_count = sum(1 for c in couples if c['type'] == 'H-H')
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(timespec='seconds'),
            "couples": couples,
            "statistiques": {
                "total_personnes": total_personnes,
                "total_couples": len(couples),
                "couples_H-F": hf_count,
                "couples_F-F": ff_count,
                "couples_H-H": hh_count,
                "personnes_non_associees": personne_seule
            }
        }


# Instance du service pour import facile
gender_association_service = GenderAssociationService()
