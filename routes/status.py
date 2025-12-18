"""
Routes pour les informations système et utilitaires.
"""
from flask import Blueprint, jsonify
from storage.memory_store import store
from datetime import datetime

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
    - Tous les noms
    - Tous les numéros
    - Toutes les associations
    
    Returns:
        JSON: Confirmation de la réinitialisation
    """
    # Sauvegarder les statistiques avant réinitialisation
    old_stats = {
        "names": len(store.names),
        "numbers": len(store.numbers),
        "associations": len(store.associations)
    }
    
    # Réinitialiser le store
    store.reset()
    
    return jsonify({
        "success": True,
        "message": "Toutes les données ont été réinitialisées",
        "previous_data": old_stats,
        "timestamp": datetime.now().isoformat()
    }), 200
