"""
Routes pour l'authentification des administrateurs.
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import timedelta
from storage.database import db, Admin, TokenBlocklist
from utils.auth import create_access_token, create_refresh_token, decode_token, verify_jwt_in_request, get_jwt_identity, get_jwt

# Créer le Blueprint pour les routes d'authentification
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Authentifie un administrateur et retourne des tokens JWT (access + refresh).
    
    Body JSON attendu:
        {
            "username": "admin",
            "password": "securepassword"
        }
    
    Returns:
        JSON: Access token, refresh token et informations utilisateur
    """
    data = request.get_json(silent=True) or {}
    
    username = data.get('username')
    password = data.get('password')
    
    # Validation des données
    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Les champs 'username' et 'password' sont requis"
        }), 400
    
    # Rechercher l'admin
    admin = Admin.query.filter_by(username=username).first()
    
    if not admin or not admin.check_password(password):
        return jsonify({
            "success": False,
            "error": "Nom d'utilisateur ou mot de passe incorrect"
        }), 401
    
    # Créer les tokens JWT
    access_expires = timedelta(seconds=int(current_app.config.get('JWT_EXP_DELTA_SECONDS', 3600)))
    access_token = create_access_token(
        identity=admin.id,
        additional_claims={'username': admin.username},
        expires_delta=access_expires
    )
    refresh_token = create_refresh_token(identity=admin.id)
    
    return jsonify({
        "success": True,
        "message": "Connexion réussie",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "admin": admin.to_dict()
    }), 200


@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    """
    Révoque un token JWT (ajout à la blocklist).
    
    Le token peut être fourni dans le header Authorization ou dans le body JSON.
    
    Body JSON optionnel:
        {
            "token": "eyJ0eXAi..."
        }
    
    Returns:
        JSON: Confirmation de la révocation
    """
    # Récupérer le token du header ou du body
    token = None
    auth_header = request.headers.get('Authorization', None)
    
    if auth_header and auth_header.split()[0].lower() == 'bearer':
        token = auth_header.split()[1]
    else:
        data = request.get_json(silent=True) or {}
        token = data.get('token')
    
    if not token:
        return jsonify({
            "success": True,
            "message": "Aucun token fourni, supprimez les tokens localement"
        }), 200
    
    try:
        payload = decode_token(token)
        jti = payload.get('jti')
        token_type = payload.get('type', 'access')
        
        # Récupérer l'admin_id
        admin_id = None
        try:
            admin_id = int(payload.get('sub'))
        except Exception:
            admin_id = payload.get('sub')
        
        # Ajouter le token à la blocklist
        if jti:
            blocked_token = TokenBlocklist(
                jti=jti,
                token_type=token_type,
                admin_id=admin_id
            )
            db.session.add(blocked_token)
            db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Token révoqué avec succès"
        }), 200
    
    except Exception as exc:
        current_app.logger.debug('Logout token revoke failed: %s', exc)
        return jsonify({
            "success": False,
            "error": "Token invalide",
            "reason": str(exc)
        }), 400


@auth_bp.route('/auth/refresh', methods=['POST'])
def refresh():
    """
    Échange un refresh token contre un nouveau access token.
    
    Le refresh token peut être fourni dans le header Authorization ou dans le body JSON.
    
    Body JSON optionnel:
        {
            "refresh_token": "eyJ0eXAi..."
        }
    
    Returns:
        JSON: Nouveau access token
    """
    # Récupérer le token du header ou du body
    token = None
    auth_header = request.headers.get('Authorization', None)
    
    if auth_header and auth_header.split()[0].lower() == 'bearer':
        token = auth_header.split()[1]
    else:
        data = request.get_json(silent=True) or {}
        token = data.get('refresh_token')
    
    if not token:
        return jsonify({
            "success": False,
            "error": "Refresh token requis"
        }), 400
    
    try:
        payload = decode_token(token)
        
        # Vérifier que c'est bien un refresh token
        if payload.get('type') != 'refresh':
            return jsonify({
                "success": False,
                "error": "Le token fourni n'est pas un refresh token"
            }), 400
        
        # Récupérer l'admin
        admin_id = payload.get('sub')
        try:
            admin_key = int(admin_id)
        except Exception:
            admin_key = admin_id
        
        admin = Admin.query.get(admin_key)
        
        if not admin:
            return jsonify({
                "success": False,
                "error": "Administrateur non trouvé"
            }), 404
        
        # Créer un nouveau access token
        access_expires = timedelta(seconds=int(current_app.config.get('JWT_EXP_DELTA_SECONDS', 3600)))
        access_token = create_access_token(
            identity=admin.id,
            additional_claims={'username': admin.username},
            expires_delta=access_expires
        )
        
        return jsonify({
            "success": True,
            "access_token": access_token
        }), 200
    
    except Exception as exc:
        current_app.logger.debug('Refresh failed: %s', exc)
        return jsonify({
            "success": False,
            "error": "Refresh token invalide",
            "reason": str(exc)
        }), 401


@auth_bp.route('/auth/me', methods=['GET'])
def me():
    """
    Retourne les informations de l'administrateur actuellement authentifié.
    
    Requiert un access token valide dans le header Authorization.
    
    Returns:
        JSON: Informations de l'administrateur
    """
    try:
        payload = verify_jwt_in_request()
        
        # Vérifier que c'est un access token
        if payload.get('type') != 'access':
            return jsonify({
                "success": False,
                "error": "Un access token valide est requis"
            }), 401
        
        admin_id = get_jwt_identity()
        admin = Admin.query.get(admin_id)
        
        if not admin:
            return jsonify({
                "success": False,
                "error": "Administrateur non trouvé"
            }), 404
        
        return jsonify({
            "success": True,
            "admin": admin.to_dict()
        }), 200
    
    except Exception as exc:
        current_app.logger.debug('JWT verification failed in /me: %s', exc)
        return jsonify({
            "success": False,
            "error": "Authentification requise",
            "reason": str(exc)
        }), 401
