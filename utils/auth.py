"""
Utilitaires pour l'authentification JWT.
"""
import jwt
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app, g


def create_access_token(identity, additional_claims=None, expires_delta=None):
    """
    Crée un token JWT d'accès.
    
    Args:
        identity: ID de l'utilisateur
        additional_claims (dict): Claims additionnels (ex: username)
        expires_delta (timedelta): Durée de validité personnalisée
        
    Returns:
        str: Token JWT d'accès
    """
    algo = current_app.config.get('JWT_ALGORITHM', 'HS256')
    now = datetime.utcnow()
    
    if expires_delta:
        exp = now + expires_delta
    else:
        exp_seconds = int(current_app.config.get('JWT_EXP_DELTA_SECONDS', 3600))
        exp = now + timedelta(seconds=exp_seconds)
    
    jti = str(uuid.uuid4())
    
    payload = {
        'sub': str(identity),
        'iat': now,
        'exp': exp,
        'jti': jti,
        'type': 'access'
    }
    
    if additional_claims:
        payload.update(additional_claims)
    
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm=algo)
    
    # PyJWT >= 2.0 retourne une string
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return token


def create_refresh_token(identity, expires_delta=None):
    """
    Crée un token JWT de rafraîchissement.
    
    Args:
        identity: ID de l'utilisateur
        expires_delta (timedelta): Durée de validité personnalisée (défaut: 7 jours)
        
    Returns:
        str: Token JWT de rafraîchissement
    """
    algo = current_app.config.get('JWT_ALGORITHM', 'HS256')
    now = datetime.utcnow()
    
    if expires_delta:
        exp = now + expires_delta
    else:
        exp = now + timedelta(days=7)
    
    jti = str(uuid.uuid4())
    
    payload = {
        'sub': str(identity),
        'iat': now,
        'exp': exp,
        'jti': jti,
        'type': 'refresh'
    }
    
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm=algo)
    
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return token


def decode_token(token):
    """
    Décode et valide un token JWT.
    
    Args:
        token (str): Token JWT
        
    Returns:
        dict: Payload du token
        
    Raises:
        jwt.InvalidTokenError: Si le token est invalide ou révoqué
    """
    from storage.database import TokenBlocklist
    
    algo = current_app.config.get('JWT_ALGORITHM', 'HS256')
    payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=[algo])
    
    # Vérifier si le token est révoqué
    jti = payload.get('jti')
    if jti and TokenBlocklist.is_blocked(jti):
        raise jwt.InvalidTokenError('Token has been revoked')
    
    return payload


def verify_jwt_in_request():
    """
    Vérifie le JWT dans le header Authorization de la requête.
    
    Returns:
        dict: Payload du token
        
    Raises:
        Exception: Si le token est manquant ou invalide
    """
    auth_header = request.headers.get('Authorization', None)
    
    if not auth_header:
        raise Exception('Missing Authorization Header')
    
    parts = auth_header.split()
    
    if parts[0].lower() != 'bearer':
        raise Exception('Invalid Authorization Header: must start with Bearer')
    elif len(parts) == 1:
        raise Exception('Invalid Authorization Header: token not found')
    elif len(parts) > 2:
        raise Exception('Invalid Authorization Header: contains extra content')
    
    token = parts[1]
    
    try:
        payload = decode_token(token)
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception('Token has expired')
    except jwt.InvalidTokenError as e:
        raise Exception(f'Invalid token: {str(e)}')


def get_jwt_identity():
    """
    Récupère l'identité (sub) du JWT vérifié dans la requête.
    
    Returns:
        int/str: ID de l'utilisateur
    """
    payload = verify_jwt_in_request()
    sub = payload.get('sub')
    
    # Essayer de retourner un entier si possible
    if isinstance(sub, str):
        try:
            return int(sub)
        except ValueError:
            return sub
    
    return sub


def get_jwt():
    """
    Récupère le payload complet du JWT vérifié dans la requête.
    
    Returns:
        dict: Payload du token
    """
    return verify_jwt_in_request()


def token_required(f):
    """
    Décorateur pour protéger les routes avec authentification JWT.
    
    Usage: Ajouter le header "Authorization: Bearer <access_token>"
    où access_token est obtenu via POST /auth/login
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            payload = verify_jwt_in_request()
            
            # Vérifier que c'est un access token
            if payload.get('type') != 'access':
                return jsonify({
                    'success': False,
                    'error': 'Un access token valide est requis',
                    'hint': 'Utilisez le token retourné par POST /auth/login'
                }), 401
            
            # Ajouter les infos utilisateur à g
            try:
                g.admin_id = int(payload.get('sub'))
            except Exception:
                g.admin_id = payload.get('sub')
            
            g.admin_username = payload.get('username')
            g.jwt_payload = payload
            
            return f(*args, **kwargs)
        
        except Exception as exc:
            error_message = str(exc)
            current_app.logger.debug('JWT verification failed: %s', exc)
            
            # Messages d'erreur plus clairs
            if 'Missing Authorization Header' in error_message:
                return jsonify({
                    'success': False,
                    'error': 'Header Authorization manquant',
                    'hint': 'Ajoutez le header: Authorization: Bearer <access_token>'
                }), 401
            elif 'expired' in error_message.lower():
                return jsonify({
                    'success': False,
                    'error': 'Token expiré',
                    'hint': 'Reconnectez-vous via POST /auth/login ou utilisez POST /auth/refresh'
                }), 401
            else:
                return jsonify({
                    'success': False,
                    'error': 'Authentification requise',
                    'reason': error_message
                }), 401
    
    return decorated
