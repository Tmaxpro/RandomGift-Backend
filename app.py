"""
Application Flask principale pour la gestion d'associations entre participants et cadeaux.
Utilise SQLite pour la persistance des données.
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Importer la base de données
from storage.database import db

# Importer les blueprints
from routes.participants import participants_bp
from routes.gifts import gifts_bp
from routes.associations import associations_bp
from routes.status import status_bp
from routes.auth import auth_bp
from routes.export import export_bp


def create_app():
    """
    Factory pattern pour créer et configurer l'application Flask.
    
    Returns:
        Flask: Instance de l'application configurée
    """
    # Créer l'application Flask
    app = Flask(__name__)
    
    # Configuration
    app.config['JSON_AS_ASCII'] = False  # Support des caractères UTF-8
    app.config['JSON_SORT_KEYS'] = False  # Préserver l'ordre des clés JSON
    
    # Configuration de la clé secrète pour JWT
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuration JWT
    app.config['JWT_ALGORITHM'] = os.environ.get('JWT_ALGORITHM', 'HS256')
    app.config['JWT_EXP_DELTA_SECONDS'] = int(os.environ.get('JWT_EXP_DELTA_SECONDS', 3600))  # 1 heure par défaut
    
    # Configuration de la base de données SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "associations.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Désactiver les signaux de modification
    
    # Initialiser la base de données
    db.init_app(app)
    
    # Créer les tables si elles n'existent pas
    with app.app_context():
        db.create_all()
    
    # Activer CORS pour toutes les routes
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Enregistrer les blueprints
    app.register_blueprint(participants_bp)
    app.register_blueprint(gifts_bp)
    app.register_blueprint(associations_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(export_bp)
    
    # Route racine
    @app.route('/', methods=['GET'])
    def home():
        """
        Page d'accueil de l'API avec liste des endpoints disponibles.
        """
        return jsonify({
            "message": "API d'association de participants et cadeaux",
            "version": "1.0.0",
            "storage": "SQLite Database",
            "endpoints": {
                "auth": {
                    "POST /auth/login": "Authentification (retourne access_token et refresh_token)",
                    "POST /auth/logout": "Déconnexion (révoque le token) (requiert authentification)",
                    "POST /auth/refresh": "Rafraîchir l'access token avec un refresh token",
                    "GET /auth/me": "Obtenir les informations de l'utilisateur connecté (requiert authentification)"
                },
                "participants": {
                    "POST /participants": "Ajouter un participant (requiert authentification)",
                    "POST /participants/bulk": "Ajouter plusieurs participants via fichier CSV ou Excel (colonne: participant/name) (requiert authentification)",
                    "GET /participants": "Lister tous les participants (requiert authentification)",
                    "DELETE /participants/<participant>": "Supprimer un participant (requiert authentification)"
                },
                "gifts": {
                    "POST /gifts": "Ajouter un cadeau (requiert authentification)",
                    "POST /gifts/bulk": "Ajouter plusieurs cadeaux via fichier CSV ou Excel (colonne: gift/cadeau) (requiert authentification)",
                    "GET /gifts": "Lister tous les cadeaux (requiert authentification)",
                    "DELETE /gifts/<gift>": "Supprimer un cadeau (requiert authentification)"
                },
                "associations": {
                    "POST /associate": "Créer des associations aléatoires (associe tous les cadeaux disponibles à des participants aléatoires) (requiert authentification)",
                    "GET /associations": "Lister toutes les associations (requiert authentification)",
                    "DELETE /associations/<participant>": "Supprimer une association (requiert authentification)"
                },
                "export": {
                    "GET /export/csv": "Exporter les associations en CSV (requiert authentification)",
                    "GET /export/pdf": "Exporter les associations en PDF (requiert authentification)"
                },
                "system": {
                    "GET /status": "État complet du système",
                    "GET /health": "Vérification de santé",
                    "DELETE /reset": "Réinitialiser toutes les données",
                    "DELETE /reset/associations": "Réinitialiser uniquement les associations"
                }
            }
        }), 200
    
    # Gestionnaire d'erreurs 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": "Endpoint non trouvé",
            "message": "Consultez GET / pour la liste des endpoints disponibles"
        }), 404
    
    # Gestionnaire d'erreurs 500
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur",
            "message": str(error)
        }), 500
    
    return app


# Créer l'instance de l'application
app = create_app()


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Démarrage de l'API d'association")
    print("=" * 60)
    print("📍 URL: http://localhost:5000")
    print("📖 Documentation: http://localhost:5000")
    print("💚 Health check: http://localhost:5000/health")
    print("💾 Base de données: SQLite (associations.db)")
    print("=" * 60)
    
    # Lancer le serveur en mode développement
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
