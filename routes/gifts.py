"""
Routes pour la gestion des femmes (via /gifts pour compatibilité).
"""
import pandas as pd
import io
from flask import Blueprint, request, jsonify
from storage.memory_store import store
from utils.auth import token_required

# Créer le Blueprint pour les routes des femmes (gifts)
gifts_bp = Blueprint('gifts', __name__)


@gifts_bp.route('/gifts', methods=['POST'])
@token_required
def add_gift():
    """
    Ajoute une femme (identifiant).
    
    Body JSON attendu:
        {
            "numero": "F1"
        }
    
    Returns:
        JSON: Confirmation de l'ajout ou erreur
    """
    data = request.get_json()
    
    # Validation des données - accepter 'numero' ou 'gift' pour compatibilité
    numero = data.get('numero') if data else None
    if numero is None:
        numero = data.get('gift') if data else None
    
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
    
    # Ajouter la femme
    if store.add_femme(numero):
        return jsonify({
            "success": True,
            "message": f"Femme {numero} ajoutée avec succès",
            "numero": numero
        }), 201
    else:
        return jsonify({
            "success": False,
            "error": f"La femme {numero} existe déjà"
        }), 400


@gifts_bp.route('/gifts/bulk', methods=['POST'])
@token_required
def add_gifts_bulk():
    """
    Ajoute plusieurs femmes (identifiants) en une seule opération.
    
    Deux modes d'envoi possibles:
    
    1. Via fichier CSV/Excel (form-data):
        - Le fichier doit contenir une colonne nommée 'numero' ou 'femme'
        - Formats acceptés: .csv, .xlsx, .xls
        - Form-data: file: fichier CSV ou Excel
    
    2. Via liste JSON (application/json):
        - Body JSON attendu:
            {
                "numeros": ["F1", "F2", "F3"]
            }
    
    Returns:
        JSON: Liste des femmes ajoutées et ignorées
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
        for key in ['numeros', 'numero', 'femmes', 'femme', 'gifts']:
            if key in data and isinstance(data[key], list):
                numeros_list = data[key]
                break
        
        if numeros_list is None:
            return jsonify({
                "success": False,
                "error": "Le champ 'numeros' doit être une liste. Ex: {\"numeros\": [\"F1\", \"F2\", \"F3\"]}"
            }), 400
        
        # Convertir et valider les numéros en strings
        converted_numeros = []
        for value in numeros_list:
            if value is not None:
                str_value = str(value).strip()
                if str_value:
                    converted_numeros.append(str_value)
        
        if not converted_numeros:
            return jsonify({
                "success": False,
                "error": "Aucun numéro valide dans la liste"
            }), 400
        
        # Ajouter les femmes
        result = store.add_femmes_bulk(converted_numeros)
        
        return jsonify({
            "success": True,
            "message": f"{len(result['added'])} femme(s) ajoutée(s), {len(result['ignored'])} ignorée(s)",
            "added": result['added'],
            "ignored": result['ignored'],
            "total_processed": len(converted_numeros)
        }), 201
    
    # Mode 2: Via fichier CSV/Excel
    if 'file' not in request.files:
        return jsonify({
            "success": False,
            "error": "Aucun fichier fourni. Utilisez le champ 'file' en form-data ou envoyez un JSON avec 'gifts': [...]"
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
            if col_lower in ['numero', 'numeros', 'femme', 'femmes', 'gift', 'gifts']:
                numero_col = col
                break
        
        if numero_col is None:
            return jsonify({
                "success": False,
                "error": "Aucune colonne 'numero' ou 'femme' trouvée dans le fichier",
                "columns_found": list(df.columns)
            }), 400
        
        # Extraire et convertir les numéros en strings
        converted_numeros = []
        for value in df[numero_col]:
            if pd.notna(value):
                str_value = str(value).strip()
                if str_value:
                    converted_numeros.append(str_value)
        
        if not converted_numeros:
            return jsonify({
                "success": False,
                "error": "Aucun numéro valide trouvé dans le fichier"
            }), 400
        
        # Ajouter les femmes
        result = store.add_femmes_bulk(converted_numeros)
        
        return jsonify({
            "success": True,
            "message": f"{len(result['added'])} femme(s) ajoutée(s), {len(result['ignored'])} ignorée(s)",
            "added": result['added'],
            "ignored": result['ignored'],
            "total_processed": len(converted_numeros)
        }), 201
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erreur lors de la lecture du fichier",
            "details": str(e)
        }), 400


@gifts_bp.route('/gifts', methods=['GET'])
def get_gifts():
    """
    Récupère toutes les femmes (numéros).
    
    Returns:
        JSON: Liste des numéros de femmes et le total
    """
    femmes_data = store.get_femmes()
    # Extraire juste les numéros
    femmes_list = [f['numero'] for f in femmes_data]
    
    return jsonify({
        "success": True,
        "total": len(femmes_list),
        "femmes": femmes_list
    }), 200


@gifts_bp.route('/gifts/<numero>', methods=['DELETE'])
@token_required
def delete_gift(numero):
    """
    Supprime une femme (identifiant).
    
    Args:
        numero (str): L'identifiant de la femme à supprimer (ex: F1)
    
    Returns:
        JSON: Confirmation de la suppression ou erreur
    """
    # Supprimer la femme
    if store.remove_femme(numero):
        return jsonify({
            "success": True,
            "message": f"Femme {numero} supprimée avec succès"
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": f"La femme {numero} n'existe pas"
        }), 404
