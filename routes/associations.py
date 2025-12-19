"""
Routes pour la gestion des associations entre hommes et femmes.
"""
from flask import Blueprint, request, jsonify
from storage.memory_store import store
from services.association_service import association_service
from utils.auth import token_required

# Créer le Blueprint pour les routes des associations
associations_bp = Blueprint('associations', __name__)


@associations_bp.route('/associate', methods=['POST'])
@token_required
def create_associations():
    """
    Crée des associations aléatoires entre hommes et femmes.
    
    Récupère automatiquement les hommes et femmes de la base de données.
    
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


@associations_bp.route('/associations', methods=['GET'])
def get_associations():
    """
    Récupère tous les couples/associations existants.
    
    Returns:
        JSON: Liste de tous les couples
    """
    couples = store.get_couples()
    
    return jsonify({
        "success": True,
        "total": len(couples),
        "couples": couples
    }), 200


@associations_bp.route('/associations/reset', methods=['DELETE'])
@token_required
def reset_associations():
    """
    Réinitialise tous les couples/associations.
    Les hommes et femmes restent en base.
    
    Returns:
        JSON: Confirmation de la réinitialisation
    """
    count = store.reset_couples()
    
    return jsonify({
        "success": True,
        "message": f"{count} couple(s) supprimé(s)"
    }), 200
