"""
Point d'entrée WSGI pour le déploiement de l'application Flask.

Ce fichier peut être utilisé avec des serveurs WSGI comme:
- Gunicorn: gunicorn wsgi:application
- uWSGI: uwsgi --http :5000 --wsgi-file wsgi.py --callable application
- mod_wsgi (Apache)
"""
import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer l'application Flask
from app import app as application

if __name__ == "__main__":
    # Pour exécution directe (développement uniquement)
    application.run()
