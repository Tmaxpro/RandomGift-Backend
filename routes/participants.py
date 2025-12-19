"""
Routes pour la gestion des hommes (via /participants pour compatibilité).
"""
import pandas as pd
import io
from flask import Blueprint, request, jsonify
from storage.memory_store import store
from utils.auth import token_required

# Créer le Blueprint pour les routes des hommes (participants)
participants_bp = Blueprint('participants', __name__)


@participants_bp.route('/participants', methods=['POST'])
@token_required
def add_participant():
    """
    Ajoute un homme (identifiant).
    
    Body JSON attendu:
        {
            "numero": "H1"
        }
    
    Returns:
        JSON: Confirmation de l'ajout ou erreur
    """
    data = request.get_json()
    
    # Validation des données - accepter 'numero' ou 'participant' pour compatibilité
    numero = data.get('numero') if data else None
    if numero is None:
        numero = data.get('participant') if data else None
    
    if numero is None:
        return jsonify({
            "success": False,
            "error": "Le champ 'numero' est requis"
        }), 400
    
    # Convertir en string
    numero = str(numero).strip()
    
    if not numero:
        return jsonify({
            "success": False,
            "error": "Le numéro ne peut pas être vide"
        }), 400
    
    # Ajouter l'homme
    if store.add_homme(numero):
        return jsonify({
            "success": True,
            "message": f"Homme {numero} ajouté avec succès",
            "numero": numero
        }), 201
    else:
        return jsonify({
            "success": False,
            "error": f"L'homme {numero} existe déjà"
        }), 400


@participants_bp.route('/participants/bulk', methods=['POST'])
@token_required
def add_participants_bulk():
    """
    Ajoute plusieurs hommes (identifiants) en une seule opération.
    
    Deux modes d'envoi possibles:
    
    1. Via fichier CSV/Excel (form-data):
        - Le fichier doit contenir une colonne nommée 'numero' ou 'homme'
        - Formats acceptés: .csv, .xlsx, .xls
        - Form-data: file: fichier CSV ou Excel
    
    2. Via liste JSON (application/json):
        - Body JSON attendu:
            {
                "numeros": ["H1", "H2", "H3"]
            }
    
    Returns:
        JSON: Liste des hommes ajoutés et ignorés
    """
    # Mode 1: Vérifier si c'est une requête JSON avec une liste
    if request.is_json:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Données JSON invalides"
            }), 400
        
        # Chercher la liste de numéros
        numeros_list = None
        for key in ['numeros', 'numero', 'hommes', 'homme', 'participants']:
            if key in data and isinstance(data[key], list):
                numeros_list = data[key]
                break
        
        if numeros_list is None:
            return jsonify({
                "success": False,
                "error": "Le champ 'numeros' doit être une liste. Ex: {\"numeros\": [\"H1\", \"H2\", \"H3\"]}"
            }), 400
        
        # Valider et convertir les numéros en strings
        cleaned_numeros = []
        for value in numeros_list:
            if value is not None:
                str_value = str(value).strip()
                if str_value:
                    cleaned_numeros.append(str_value)
        
        if not cleaned_numeros:
            return jsonify({
                "success": False,
                "error": "Aucun numéro valide dans la liste"
            }), 400
        
        # Ajouter les hommes
        result = store.add_hommes_bulk(cleaned_numeros)
        
        return jsonify({
            "success": True,
            "message": f"{len(result['added'])} homme(s) ajouté(s), {len(result['ignored'])} ignoré(s)",
            "added": result['added'],
            "ignored": result['ignored'],
            "total_processed": len(cleaned_numeros)
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
        
        # Chercher la colonne des numéros
        numero_col = None
        for col in df.columns:
            col_lower = col.lower().strip()
            if col_lower in ['numero', 'numeros', 'homme', 'hommes', 'participant', 'participants']:
                numero_col = col
                break
        
        if numero_col is None:
            return jsonify({
                "success": False,
                "error": "Aucune colonne 'numero' ou 'homme' trouvée dans le fichier",
                "columns_found": list(df.columns)
            }), 400
        
        # Extraire et valider les numéros (maintenant en strings)
        cleaned_numeros = []
        for value in df[numero_col]:
            if pd.notna(value):  # Ignorer les valeurs NaN
                str_value = str(value).strip()
                if str_value:
                    cleaned_numeros.append(str_value)
        
        if not cleaned_numeros:
            return jsonify({
                "success": False,
                "error": "Aucun numéro valide trouvé dans le fichier"
            }), 400
        
        # Ajouter les hommes
        result = store.add_hommes_bulk(cleaned_numeros)
        
        return jsonify({
            "success": True,
            "message": f"{len(result['added'])} homme(s) ajouté(s), {len(result['ignored'])} ignoré(s)",
            "added": result['added'],
            "ignored": result['ignored'],
            "total_processed": len(cleaned_numeros)
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
    Récupère tous les hommes (numéros).
    
    Returns:
        JSON: Liste des numéros d'hommes et le total
    """
    hommes_data = store.get_hommes()
    # Extraire juste les numéros
    hommes_list = [h['numero'] for h in hommes_data]
    
    return jsonify({
        "success": True,
        "total": len(hommes_list),
        "participants": hommes_list
    }), 200


@participants_bp.route('/participants/<numero>', methods=['DELETE'])
@token_required
def delete_participant(numero):
    """
    Supprime un homme (identifiant).
    
    Args:
        numero (str): L'identifiant de l'homme à supprimer (ex: H1)
    
    Returns:
        JSON: Confirmation de la suppression ou erreur
    """
    # Supprimer l'homme
    if store.remove_homme(numero):
        return jsonify({
            "success": True,
            "message": f"Homme {numero} supprimé avec succès"
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": f"L'homme {numero} n'existe pas"
        }), 404
