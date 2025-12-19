"""
Routes pour les informations système et utilitaires.
"""
import json
import os
from flask import Blueprint, jsonify
from storage.memory_store import store
from datetime import datetime

# Fichier pour l'historique des resets
RESET_ASSOCIATION_HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reset_association_history.json')
RESET_TOTAL_HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reset_total_history.json')

# Créer le Blueprint pour les routes de statut
status_bp = Blueprint('status', __name__)


@status_bp.route('/status', methods=['GET'])
def get_status():
    """
    Retourne l'état complet du système.
    
    Inclut:
    - Statistiques sur les noms (total, associés, non associés)
    - Statistiques sur les numéros (total, associés, non associés)
    - Détails des associations
    
    Returns:
        JSON: État complet du système
    """
    status = store.get_status()
    
    return jsonify({
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "status": status
    }), 200


@status_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de vérification de santé de l'API.
    
    Returns:
        JSON: Statut de santé de l'application
    """
    return jsonify({
        "status": "healthy",
        "service": "Association API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200


@status_bp.route('/reset', methods=['DELETE'])
def reset_data():
    """
    Réinitialise toutes les données du système.
    
    Supprime:
    - Tous les participants
    - Tous les gifts
    - Toutes les associations
    
    Returns:
        JSON: Confirmation de la réinitialisation
    """
    # Sauvegarder les statistiques avant réinitialisation
    old_stats = {
        "participants": len(store.participants),
        "gift": len(store.gifts),
        "associations": len(store.get_couples())
    }
    
    # Préparer les données du reset total
    reset_data = {
        "reset_at": datetime.now().isoformat(),
        "previous_data": old_stats
    }
    
    # Charger l'historique existant ou créer un nouveau
    history = []
    if os.path.exists(RESET_TOTAL_HISTORY_FILE):
        try:
            with open(RESET_TOTAL_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []
    
    # Ajouter le nouveau reset à l'historique
    history.append(reset_data)
    
    # Sauvegarder l'historique
    with open(RESET_TOTAL_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    # Réinitialiser le store
    store.reset()
    
    return jsonify({
        "success": True,
        "message": "Toutes les données ont été réinitialisées",
        "previous_data": old_stats,
        "timestamp": datetime.now().isoformat()
    }), 200


@status_bp.route('/reset/associations', methods=['DELETE'])
def reset_associations():
    """
    Réinitialise uniquement les associations.
    
    Les participants et cadeaux sont conservés mais redeviennent non associés.
    Sauvegarde l'historique des couples dans un fichier JSON.
    
    Returns:
        JSON: Confirmation de la réinitialisation des associations
    """
    # Récupérer les couples avant suppression
    couples_before_reset = store.get_couples()
    associations_count = len(couples_before_reset)
    
    # Préparer les données du reset
    reset_data = {
        "reset_at": datetime.now().isoformat(),
        "couples_count": associations_count,
        "couples": couples_before_reset
    }
    
    # Charger l'historique existant ou créer un nouveau
    history = []
    if os.path.exists(RESET_ASSOCIATION_HISTORY_FILE):
        try:
            with open(RESET_ASSOCIATION_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []
    
    # Ajouter le nouveau reset à l'historique
    history.append(reset_data)
    
    # Sauvegarder l'historique
    with open(RESET_ASSOCIATION_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    # Effectuer le reset
    store.reset_couples()
    
    return jsonify({
        "success": True,
        "message": "Toutes les associations ont été réinitialisées",
        "associations_deleted": associations_count,
        "timestamp": datetime.now().isoformat()
    }), 200

