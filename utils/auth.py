"""
Utilitaires pour l'authentification JWT.
"""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app


def generate_token(user_id, username):
    """
    Génère un token JWT pour un utilisateur.
    
    Args:
        user_id (int): ID de l'utilisateur
        username (str): Nom d'utilisateur
        
    Returns:
        str: Token JWT
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=1),  # Token valide 24h
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def decode_token(token):
    """
    Décode un token JWT.
    
    Args:
        token (str): Token JWT
        
    Returns:
        dict: Payload du token ou None si invalide
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """
    Décorateur pour protéger les routes avec authentification JWT.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Récupérer le token du header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Format: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'error': 'Format du token invalide. Utilisez: Bearer <token>'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token manquant. Authentification requise.'
            }), 401
        
        # Décoder et valider le token
        payload = decode_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Token invalide ou expiré'
            }), 401
        
        # Ajouter les infos utilisateur à la requête
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated
