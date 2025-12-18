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
def add_participant():
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
def add_participants_bulk():
    """
    Ajoute plusieurs participants en une seule opération.
    
    Deux modes d'envoi possibles:
    
    1. Via fichier CSV/Excel (form-data):
        - Le fichier doit contenir une colonne nommée 'participant' ou 'name'
        - Formats acceptés: .csv, .xlsx, .xls
        - Form-data: file: fichier CSV ou Excel
    
    2. Via liste JSON (application/json):
        - Body JSON attendu:
            {
                "participants": ["Alice", "Bob", "Charlie"]
            }
    
    Returns:
        JSON: Liste des participants ajoutés et ignorés
    """
    # Mode 1: Vérifier si c'est une requête JSON avec une liste
    if request.is_json:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Données JSON invalides"
            }), 400
        
        # Chercher la liste de participants
        participants_list = None
        for key in ['participants', 'participant', 'names', 'name', 'noms', 'nom']:
            if key in data and isinstance(data[key], list):
                participants_list = data[key]
                break
        
        if participants_list is None:
            return jsonify({
                "success": False,
                "error": "Le champ 'participants' doit être une liste. Ex: {\"participants\": [\"Alice\", \"Bob\"]}"
            }), 400
        
        # Nettoyer et valider les participants
        cleaned_participants = []
        for value in participants_list:
            if value is not None:
                participant = str(value).strip()
                if participant:
                    cleaned_participants.append(participant)
        
        if not cleaned_participants:
            return jsonify({
                "success": False,
                "error": "Aucun participant valide dans la liste"
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
    
    # Mode 2: Via fichier CSV/Excel
    if 'file' not in request.files:
        return jsonify({
            "success": False,
            "error": "Aucun fichier fourni. Utilisez le champ 'file' en form-data ou envoyez un JSON avec 'participants': [...]"
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
    Récupère tous les participants.
    
    Returns:
        JSON: Liste des noms de participants et le total
    """
    participants_data = store.get_participants()
    # Extraire juste les noms des participants
    participants_list = [p['participant'] for p in participants_data]
    
    return jsonify({
        "success": True,
        "total": len(participants_list),
        "participants": participants_list
    }), 200


@participants_bp.route('/participants/<string:participant>', methods=['DELETE'])
@token_required
def delete_participant(participant):
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
