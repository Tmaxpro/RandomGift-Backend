"""
Routes pour la gestion des associations entre participants et cadeaux.
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
    Crée des associations aléatoires entre participants et cadeaux non associés.
    
    Règles:
    - Seuls les participants et cadeaux non associés sont utilisés
    - Chaque cadeau disponible est associé à un participant aléatoire
    - Si il y a plus de participants que de cadeaux, seuls certains participants seront associés
    - Les associations existantes ne sont jamais modifiées
    
    Returns:
        JSON: Nouvelles associations créées et total des associations
    """
    # Créer les associations via le service
    result = association_service.create_random_associations()
    
    # Déterminer le code de statut HTTP
    status_code = 200 if result['success'] else 400
    
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
