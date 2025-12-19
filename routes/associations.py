"""
Routes pour la gestion des associations entre hommes et femmes.
"""
from flask import Blueprint, request, jsonify
from storage.memory_store import store
from services.association_service import association_service
from services.gender_association_service import gender_association_service
from utils.auth import token_required

# Créer le Blueprint pour les routes des associations
associations_bp = Blueprint('associations', __name__)


@associations_bp.route('/associate', methods=['POST'])
@token_required
def create_associations():
    """
    Crée des associations aléatoires entre hommes et femmes.
    
    Utilise les hommes (participants) et femmes (gifts) déjà enregistrés en base.
    
    Règles métier:
    - Priorité: associer 1 homme + 1 femme tant que possible
    - Ensuite: associer les personnes restantes du même genre (F-F ou H-H)
    - Aucun numéro ne peut apparaître dans plus d'un couple
    
    Returns:
        JSON: Timestamp et liste des couples créés avec leur type
    """
    # Créer les associations via le service
    result = association_service.create_random_associations()
    
    # Déterminer le code de statut HTTP
    status_code = 200 if result['success'] else 400
    
    return jsonify(result), status_code


@associations_bp.route('/api/associate', methods=['POST'])
@token_required
def create_gender_associations():
    """
    Crée des associations aléatoires entre personnes (hommes et femmes).
    Version stateless - reçoit les listes directement dans le body.
    
    Règles métier:
    - Chaque numéro représente une personne unique
    - Les listes sont mélangées aléatoirement avant association
    - Priorité: associer 1 homme + 1 femme tant que possible
    - Ensuite: associer les personnes restantes du même genre (F-F ou H-H)
    - Aucun numéro ne peut apparaître dans plus d'un couple
    
    Body JSON attendu:
    {
        "femmes": [1, 2, 3, 4],
        "hommes": [10, 11]
    }
    
    Returns:
        JSON: Timestamp et liste des couples créés avec leur type
    """
    # Récupérer les données JSON
    data = request.get_json(silent=True)
    
    # Appeler le service d'association
    result = gender_association_service.associate(data)
    
    # Déterminer le code de statut HTTP
    status_code = 200 if result.get('success') else 400
    
    return jsonify(result), status_code


@associations_bp.route('/associations', methods=['GET'])
def get_associations():
    """
    Récupère toutes les associations existantes.
    
    Returns:
        JSON: Dictionnaire de toutes les associations {participant: cadeau}
    """
    associations = store.get_associations()
    
    # Transformer en liste pour une meilleure lisibilité
    associations_list = [
        {"participant": participant, "gift": gift}
        for participant, gift in associations.items()
    ]
    
    return jsonify({
        "success": True,
        "total": len(associations),
        "associations": associations,
        "associations_list": associations_list
    }), 200


@associations_bp.route('/associations/<string:participant>', methods=['DELETE'])
@token_required
def delete_association(participant):
    """
    Supprime l'association d'un participant.
    Le cadeau redevient disponible pour de nouvelles associations.
    
    Args:
        participant (str): Le participant dont l'association doit être supprimée
    
    Returns:
        JSON: Confirmation de la suppression ou erreur
    """
    # Vérifier si le participant existe dans le système
    if participant not in store.participants:
        return jsonify({
            "success": False,
            "error": f"Le participant '{participant}' n'existe pas dans le système"
        }), 404
    
    # Supprimer l'association
    if store.remove_association(participant):
        return jsonify({
            "success": True,
            "message": f"Association du participant '{participant}' supprimée avec succès. Le cadeau est maintenant disponible."
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": f"Le participant '{participant}' n'a pas d'association"
        }), 404
