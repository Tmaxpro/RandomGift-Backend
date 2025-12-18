"""
Routes pour la gestion des participants.
"""
import pandas as pd
import io
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
    Ajoute plusieurs participants en une seule opération via fichier CSV/Excel.
    
    Le fichier doit contenir une colonne nommée 'participant' ou 'name'.
    Les formats acceptés: .csv, .xlsx, .xls
    
    Form-data attendu:
        file: fichier CSV ou Excel
    
    Returns:
        JSON: Liste des participants ajoutés et ignorés
    """
    # Vérifier qu'un fichier a été envoyé
    if 'file' not in request.files:
        return jsonify({
            "success": False,
            "error": "Aucun fichier fourni. Utilisez le champ 'file' en form-data"
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            "success": False,
            "error": "Nom de fichier vide"
        }), 400
    
    # Vérifier l'extension du fichier
    allowed_extensions = {'.csv', '.xlsx', '.xls'}
    file_ext = '.' + file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        return jsonify({
            "success": False,
            "error": f"Format de fichier non supporté. Utilisez: {', '.join(allowed_extensions)}"
        }), 400
    
    try:
        # Lire le fichier selon son format
        if file_ext == '.csv':
            df = pd.read_csv(io.BytesIO(file.read()))
        else:  # .xlsx ou .xls
            df = pd.read_excel(io.BytesIO(file.read()))
        
        # Chercher la colonne des participants
        participant_col = None
        for col in df.columns:
            col_lower = col.lower().strip()
            if col_lower in ['participant', 'participants', 'name', 'nom']:
                participant_col = col
                break
        
        if participant_col is None:
            return jsonify({
                "success": False,
                "error": "Aucune colonne 'participant' ou 'name' trouvée dans le fichier",
                "columns_found": list(df.columns)
            }), 400
        
        # Extraire et nettoyer les participants
        cleaned_participants = []
        for value in df[participant_col]:
            if pd.notna(value):  # Ignorer les valeurs NaN
                participant = str(value).strip()
                if participant:
                    cleaned_participants.append(participant)
        
        if not cleaned_participants:
            return jsonify({
                "success": False,
                "error": "Aucun participant valide trouvé dans le fichier"
            }), 400
        
        # Ajouter les participants
        result = store.add_participants_bulk(cleaned_participants)
        
        return jsonify({
            "success": True,
            "message": f"{len(result['added'])} participant(s) ajouté(s), {len(result['ignored'])} ignoré(s)",
            "added": result['added'],
            "ignored": result['ignored'],
            "total_processed": len(cleaned_participants)
        }), 201
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erreur lors de la lecture du fichier",
            "details": str(e)
        }), 400


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
