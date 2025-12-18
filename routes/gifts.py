"""
Routes pour la gestion des cadeaux.
"""
from flask import Blueprint, request, jsonify
from storage.memory_store import store
from utils.auth import token_required

# Créer le Blueprint pour les routes des cadeaux
gifts_bp = Blueprint('gifts', __name__)


@gifts_bp.route('/gifts', methods=['POST'])
@token_required
def add_gift(current_user):
    """
    Ajoute un cadeau unique.
    
    Body JSON attendu:
        {
            "gift": 10
        }
    
    Returns:
        JSON: Confirmation de l'ajout ou erreur
    """
    data = request.get_json()
    
    # Validation des données
    if not data or 'gift' not in data:
        return jsonify({
            "success": False,
            "error": "Le champ 'gift' est requis"
        }), 400
    
    gift = data['gift']
    
    # Validation du type (int ou float converti en int)
    if not isinstance(gift, (int, float)):
        return jsonify({
            "success": False,
            "error": "Le cadeau doit être un nombre"
        }), 400
    
    gift = int(gift)
    
    # Ajouter le cadeau
    if store.add_gift(gift):
        return jsonify({
            "success": True,
            "message": f"Cadeau {gift} ajouté avec succès",
            "gift": gift
        }), 201
    else:
        return jsonify({
            "success": False,
            "error": f"Le cadeau {gift} existe déjà"
        }), 400


@gifts_bp.route('/gifts/bulk', methods=['POST'])
@token_required
def add_gifts_bulk(current_user):
    """
    Ajoute plusieurs cadeaux en une seule opération.
    
    Body JSON attendu:
        {
            "gifts": [10, 20, 30]
        }
    
    Returns:
        JSON: Liste des cadeaux ajoutés et ignorés
    """
    data = request.get_json()
    
    # Validation des données
    if not data or 'gifts' not in data:
        return jsonify({
            "success": False,
            "error": "Le champ 'gifts' est requis"
        }), 400
    
    gifts = data['gifts']
    
    # Validation du type
    if not isinstance(gifts, list):
        return jsonify({
            "success": False,
            "error": "'gifts' doit être une liste"
        }), 400
    
    if not gifts:
        return jsonify({
            "success": False,
            "error": "La liste de cadeaux ne peut pas être vide"
        }), 400
    
    # Valider et convertir chaque cadeau
    converted_gifts = []
    for gift in gifts:
        if not isinstance(gift, (int, float)):
            return jsonify({
                "success": False,
                "error": f"Tous les cadeaux doivent être des nombres. Trouvé: {type(gift).__name__}"
            }), 400
        
        converted_gifts.append(int(gift))
    
    # Ajouter les cadeaux
    result = store.add_gifts_bulk(converted_gifts)
    
    return jsonify({
        "success": True,
        "message": f"{len(result['added'])} cadeau(x) ajouté(s), {len(result['ignored'])} ignoré(s)",
        "added": result['added'],
        "ignored": result['ignored']
    }), 201


@gifts_bp.route('/gifts', methods=['GET'])
def get_gifts():
    """
    Récupère tous les cadeaux avec leur statut d'association.
    
    Returns:
        JSON: Liste des cadeaux avec indication d'association
    """
    gifts = store.get_gifts()
    
    return jsonify({
        "success": True,
        "total": len(gifts),
        "gifts": gifts
    }), 200


@gifts_bp.route('/gifts/<int:gift>', methods=['DELETE'])
@token_required
def delete_gift(current_user, gift):
    """
    Supprime un cadeau et son association éventuelle.
    
    Args:
        gift (int): Le cadeau à supprimer
    
    Returns:
        JSON: Confirmation de la suppression ou erreur
    """
    # Supprimer le cadeau
    if store.remove_gift(gift):
        return jsonify({
            "success": True,
            "message": f"Cadeau {gift} supprimé avec succès (ainsi que son association éventuelle)"
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": f"Le cadeau {gift} n'existe pas"
        }), 404
