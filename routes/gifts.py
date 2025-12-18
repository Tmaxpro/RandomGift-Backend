"""
Routes pour la gestion des cadeaux.
"""
import pandas as pd
import io
from flask import Blueprint, request, jsonify
from storage.memory_store import store
from utils.auth import token_required

# Créer le Blueprint pour les routes des cadeaux
gifts_bp = Blueprint('gifts', __name__)


@gifts_bp.route('/gifts', methods=['POST'])
@token_required
def add_gift():
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
def add_gifts_bulk():
    """
    Ajoute plusieurs cadeaux en une seule opération.
    
    Deux modes d'envoi possibles:
    
    1. Via fichier CSV/Excel (form-data):
        - Le fichier doit contenir une colonne nommée 'gift', 'cadeau' ou 'number'
        - Formats acceptés: .csv, .xlsx, .xls
        - Form-data: file: fichier CSV ou Excel
    
    2. Via liste JSON (application/json):
        - Body JSON attendu:
            {
                "gifts": [10, 20, 30, 40, 50]
            }
    
    Returns:
        JSON: Liste des cadeaux ajoutés et ignorés
    """
    # Mode 1: Vérifier si c'est une requête JSON avec une liste
    if request.is_json:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Données JSON invalides"
            }), 400
        
        # Chercher la liste de cadeaux
        gifts_list = None
        for key in ['gifts', 'gift', 'cadeaux', 'cadeau', 'numbers', 'number', 'numeros', 'numéros']:
            if key in data and isinstance(data[key], list):
                gifts_list = data[key]
                break
        
        if gifts_list is None:
            return jsonify({
                "success": False,
                "error": "Le champ 'gifts' doit être une liste. Ex: {\"gifts\": [10, 20, 30]}"
            }), 400
        
        # Convertir et valider les cadeaux
        converted_gifts = []
        for value in gifts_list:
            if value is not None:
                try:
                    gift = int(float(value))  # Convertir en float puis int pour gérer les décimaux
                    converted_gifts.append(gift)
                except (ValueError, TypeError):
                    # Ignorer les valeurs non numériques
                    pass
        
        if not converted_gifts:
            return jsonify({
                "success": False,
                "error": "Aucun cadeau valide (nombre) dans la liste"
            }), 400
        
        # Ajouter les cadeaux
        result = store.add_gifts_bulk(converted_gifts)
        
        return jsonify({
            "success": True,
            "message": f"{len(result['added'])} cadeau(x) ajouté(s), {len(result['ignored'])} ignoré(s)",
            "added": result['added'],
            "ignored": result['ignored'],
            "total_processed": len(converted_gifts)
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
        
        # Chercher la colonne des cadeaux
        gift_col = None
        for col in df.columns:
            col_lower = col.lower().strip()
            if col_lower in ['gift', 'gifts', 'cadeau', 'cadeaux', 'number', 'numero', 'numéro']:
                gift_col = col
                break
        
        if gift_col is None:
            return jsonify({
                "success": False,
                "error": "Aucune colonne 'gift' ou 'cadeau' trouvée dans le fichier",
                "columns_found": list(df.columns)
            }), 400
        
        # Extraire et convertir les cadeaux
        converted_gifts = []
        for value in df[gift_col]:
            if pd.notna(value):  # Ignorer les valeurs NaN
                try:
                    gift = int(float(value))  # Convertir en float puis int pour gérer les décimaux
                    converted_gifts.append(gift)
                except (ValueError, TypeError):
                    # Ignorer les valeurs non numériques
                    pass
        
        if not converted_gifts:
            return jsonify({
                "success": False,
                "error": "Aucun cadeau valide (nombre) trouvé dans le fichier"
            }), 400
        
        # Ajouter les cadeaux
        result = store.add_gifts_bulk(converted_gifts)
        
        return jsonify({
            "success": True,
            "message": f"{len(result['added'])} cadeau(x) ajouté(s), {len(result['ignored'])} ignoré(s)",
            "added": result['added'],
            "ignored": result['ignored'],
            "total_processed": len(converted_gifts)
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
    Récupère tous les cadeaux.
    
    Returns:
        JSON: Liste des cadeaux et le total
    """
    gifts_data = store.get_gifts()
    # Extraire juste les valeurs des cadeaux
    gifts_list = [g['gift'] for g in gifts_data]
    
    return jsonify({
        "success": True,
        "total": len(gifts_list),
        "gifts": gifts_list
    }), 200


@gifts_bp.route('/gifts/<int:gift>', methods=['DELETE'])
@token_required
def delete_gift(gift):
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
