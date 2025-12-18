"""
Routes pour la gestion des participants.
"""
from flask import Blueprint, request, jsonify
from storage.memory_store import store
from utils.auth import token_required

# Créer le Blueprint pour les routes des participants
participants_bp = Blueprint('participants', __name__)


@participants_bp.route('/participants', methods=['POST'])
@token_required
def add_participant(current_user):
    """
    Ajoute un participant unique.
    
    Body JSON attendu:
        {
            "participant": "Alice"
        }
    
    Returns:
        JSON: Confirmation de l'ajout ou erreur
    """
    data = request.get_json()
    
    # Validation des données
    if not data or 'participant' not in data:
        return jsonify({
            "success": False,
            "error": "Le champ 'participant' est requis"
        }), 400
    
    participant = data['participant']
    
    # Validation du type
    if not isinstance(participant, str) or not participant.strip():
        return jsonify({
            "success": False,
            "error": "Le participant doit être une chaîne non vide"
        }), 400
    
    participant = participant.strip()
    
    # Ajouter le participant
    if store.add_participant(participant):
        return jsonify({
            "success": True,
            "message": f"Participant '{participant}' ajouté avec succès",
            "participant": participant
        }), 201
    else:
        return jsonify({
            "success": False,
            "error": f"Le participant '{participant}' existe déjà"
        }), 400


@participants_bp.route('/participants/bulk', methods=['POST'])
@token_required
def add_participants_bulk(current_user):
    """
    Ajoute plusieurs participants en une seule opération.
    
    Body JSON attendu:
        {
            "participants": ["Alice", "Bob", "Charlie"]
        }
    
    Returns:
        JSON: Liste des participants ajoutés et ignorés
    """
    data = request.get_json()
    
    # Validation des données
    if not data or 'participants' not in data:
        return jsonify({
            "success": False,
            "error": "Le champ 'participants' est requis"
        }), 400
    
    participants = data['participants']
    
    # Validation du type
    if not isinstance(participants, list):
        return jsonify({
            "success": False,
            "error": "'participants' doit être une liste"
        }), 400
    
    if not participants:
        return jsonify({
            "success": False,
            "error": "La liste de participants ne peut pas être vide"
        }), 400
    
    # Nettoyer et valider chaque participant
    cleaned_participants = []
    for participant in participants:
        if not isinstance(participant, str):
            return jsonify({
                "success": False,
                "error": f"Tous les participants doivent être des chaînes. Trouvé: {type(participant).__name__}"
            }), 400
        
        cleaned_participant = participant.strip()
        if cleaned_participant:
            cleaned_participants.append(cleaned_participant)
    
    # Ajouter les participants
    result = store.add_participants_bulk(cleaned_participants)
    
    return jsonify({
        "success": True,
        "message": f"{len(result['added'])} participant(s) ajouté(s), {len(result['ignored'])} ignoré(s)",
        "added": result['added'],
        "ignored": result['ignored']
    }), 201


@participants_bp.route('/participants', methods=['GET'])
def get_participants():
    """
    Récupère tous les participants avec leur statut d'association.
    
    Returns:
        JSON: Liste des participants avec indication d'association
    """
    participants = store.get_participants()
    
    return jsonify({
        "success": True,
        "total": len(participants),
        "participants": participants
    }), 200


@participants_bp.route('/participants/<string:participant>', methods=['DELETE'])
@token_required
def delete_participant(current_user, participant):
    """
    Supprime un participant et son association éventuelle.
    
    Args:
        participant (str): Le participant à supprimer
    
    Returns:
        JSON: Confirmation de la suppression ou erreur
    """
    # Supprimer le participant
    if store.remove_participant(participant):
        return jsonify({
            "success": True,
            "message": f"Participant '{participant}' supprimé avec succès (ainsi que son association éventuelle)"
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": f"Le participant '{participant}' n'existe pas"
        }), 404
