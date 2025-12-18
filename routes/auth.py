"""
Routes pour l'authentification des administrateurs.
"""
from flask import Blueprint, request, jsonify
from storage.database import db, Admin
from utils.auth import generate_token

# Créer le Blueprint pour les routes d'authentification
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """
    Enregistre un nouvel administrateur.
    
    Body JSON attendu:
        {
            "username": "admin",
            "password": "securepassword"
        }
    
    Returns:
        JSON: Confirmation de l'enregistrement
    """
    data = request.get_json()
    
    # Validation des données
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            "success": False,
            "error": "Les champs 'username' et 'password' sont requis"
        }), 400
    
    username = data['username'].strip()
    password = data['password']
    
    # Validation
    if not username or len(username) < 3:
        return jsonify({
            "success": False,
            "error": "Le nom d'utilisateur doit contenir au moins 3 caractères"
        }), 400
    
    if not password or len(password) < 6:
        return jsonify({
            "success": False,
            "error": "Le mot de passe doit contenir au moins 6 caractères"
        }), 400
    
    # Vérifier si l'utilisateur existe déjà
    existing_admin = Admin.query.filter_by(username=username).first()
    if existing_admin:
        return jsonify({
            "success": False,
            "error": f"L'utilisateur '{username}' existe déjà"
        }), 400
    
    # Créer le nouvel admin
    new_admin = Admin(username=username)
    new_admin.set_password(password)
    
    db.session.add(new_admin)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": f"Administrateur '{username}' créé avec succès",
        "admin": new_admin.to_dict()
    }), 201


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Authentifie un administrateur et retourne un token JWT.
    
    Body JSON attendu:
        {
            "username": "admin",
            "password": "securepassword"
        }
    
    Returns:
        JSON: Token JWT et informations utilisateur
    """
    data = request.get_json()
    
    # Validation des données
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            "success": False,
            "error": "Les champs 'username' et 'password' sont requis"
        }), 400
    
    username = data['username'].strip()
    password = data['password']
    
    # Rechercher l'admin
    admin = Admin.query.filter_by(username=username).first()
    
    if not admin or not admin.check_password(password):
        return jsonify({
            "success": False,
            "error": "Nom d'utilisateur ou mot de passe incorrect"
        }), 401
    
    # Générer le token JWT
    token = generate_token(admin.id, admin.username)
    
    return jsonify({
        "success": True,
        "message": "Connexion réussie",
        "token": token,
        "admin": admin.to_dict()
    }), 200
