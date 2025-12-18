#!/usr/bin/env python3
"""
Script CLI pour gérer les administrateurs.
Usage:
    python admin.py create  - Crée l'administrateur depuis les variables .env
    python admin.py delete  - Supprime l'administrateur
"""
import sys
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

from app import create_app
from storage.database import db, Admin


def create_admin():
    """Crée un administrateur avec les identifiants du .env"""
    app = create_app()
    
    with app.app_context():
        username = os.getenv('ADMIN_USERNAME')
        password = os.getenv('ADMIN_PASSWORD')
        
        if not username or not password:
            print("❌ Erreur: ADMIN_USERNAME et ADMIN_PASSWORD doivent être définis dans le fichier .env")
            return False
        
        # Vérifier si l'admin existe déjà
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            print(f"⚠️  L'administrateur '{username}' existe déjà.")
            response = input("Voulez-vous mettre à jour le mot de passe ? (o/n): ")
            if response.lower() == 'o':
                existing_admin.set_password(password)
                db.session.commit()
                print(f"✅ Mot de passe de l'administrateur '{username}' mis à jour avec succès!")
                return True
            else:
                print("Opération annulée.")
                return False
        
        # Créer le nouvel admin
        new_admin = Admin(username=username)
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        db.session.commit()
        
        print(f"✅ Administrateur '{username}' créé avec succès!")
        print(f"   ID: {new_admin.id}")
        print(f"   Créé le: {new_admin.created_at}")
        return True


def delete_admin():
    """Supprime l'administrateur défini dans le .env"""
    app = create_app()
    
    with app.app_context():
        username = os.getenv('ADMIN_USERNAME')
        
        if not username:
            print("❌ Erreur: ADMIN_USERNAME doit être défini dans le fichier .env")
            return False
        
        # Rechercher l'admin
        admin = Admin.query.filter_by(username=username).first()
        
        if not admin:
            print(f"❌ L'administrateur '{username}' n'existe pas.")
            return False
        
        # Confirmation
        print(f"⚠️  Vous êtes sur le point de supprimer l'administrateur '{username}'")
        response = input("Êtes-vous sûr ? (o/n): ")
        
        if response.lower() != 'o':
            print("Opération annulée.")
            return False
        
        db.session.delete(admin)
        db.session.commit()
        
        print(f"✅ Administrateur '{username}' supprimé avec succès!")
        return True


def list_admins():
    """Liste tous les administrateurs"""
    app = create_app()
    
    with app.app_context():
        admins = Admin.query.all()
        
        if not admins:
            print("Aucun administrateur trouvé.")
            return
        
        print(f"\n📋 Liste des administrateurs ({len(admins)}):")
        print("-" * 60)
        for admin in admins:
            print(f"  ID: {admin.id}")
            print(f"  Username: {admin.username}")
            print(f"  Créé le: {admin.created_at}")
            print("-" * 60)


def show_usage():
    """Affiche l'aide d'utilisation"""
    print("""
Usage: python admin.py [command]

Commandes disponibles:
  create    Crée un administrateur avec les identifiants du .env
  delete    Supprime l'administrateur spécifié dans le .env
  list      Liste tous les administrateurs existants
  help      Affiche cette aide

Exemples:
  python admin.py create
  python admin.py delete
  python admin.py list
    """)


def main():
    """Point d'entrée principal"""
    if len(sys.argv) < 2:
        print("❌ Erreur: Aucune commande spécifiée.")
        show_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        success = create_admin()
        sys.exit(0 if success else 1)
    elif command == 'delete':
        success = delete_admin()
        sys.exit(0 if success else 1)
    elif command == 'list':
        list_admins()
        sys.exit(0)
    elif command in ['help', '--help', '-h']:
        show_usage()
        sys.exit(0)
    else:
        print(f"❌ Commande inconnue: {command}")
        show_usage()
        sys.exit(1)


if __name__ == '__main__':
    main()
