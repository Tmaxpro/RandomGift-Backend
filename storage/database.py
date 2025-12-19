"""
Configuration de la base de données et modèles SQLAlchemy.
Terminologie: Homme (anciennement participant) et Femme (anciennement gift)
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Instance de SQLAlchemy
db = SQLAlchemy()


class Admin(db.Model):
    """
    Modèle pour stocker les administrateurs.
    """
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def set_password(self, password):
        """Hash et stocke le mot de passe."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie le mot de passe."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<Admin {self.username}>"
    
    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class TokenBlocklist(db.Model):
    """
    Modèle pour stocker les tokens JWT révoqués.
    """
    __tablename__ = 'token_blocklist'
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False, index=True)  # JWT ID
    token_type = db.Column(db.String(10), nullable=False)  # 'access' ou 'refresh'
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id', ondelete='CASCADE'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    @staticmethod
    def is_blocked(jti):
        """Vérifie si un token est révoqué."""
        return TokenBlocklist.query.filter_by(jti=jti).first() is not None
    
    def __repr__(self):
        return f"<TokenBlocklist {self.jti}>"


class Homme(db.Model):
    """
    Modèle pour stocker les hommes (numéros).
    """
    __tablename__ = 'hommes'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False, index=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Homme {self.numero}>"
    
    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            "numero": self.numero,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Femme(db.Model):
    """
    Modèle pour stocker les femmes (numéros).
    """
    __tablename__ = 'femmes'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False, index=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Femme {self.numero}>"
    
    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            "numero": self.numero,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Couple(db.Model):
    """
    Modèle pour stocker les associations/couples.
    Types: H-F (homme-femme), H-H (homme-homme), F-F (femme-femme)
    """
    __tablename__ = 'couples'
    
    id = db.Column(db.Integer, primary_key=True)
    type_couple = db.Column(db.String(5), nullable=False, index=True)  # 'H-F', 'H-H', 'F-F'
    personne1 = db.Column(db.Integer, nullable=False)
    personne2 = db.Column(db.Integer, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Couple {self.type_couple}: {self.personne1} - {self.personne2}>"
    
    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            "type": self.type_couple,
            "personne1": self.personne1,
            "personne2": self.personne2,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# Aliases pour compatibilité avec les anciennes routes
Participant = Homme  # Pour /participants
Gift = Femme  # Pour /gifts
Association = Couple  # Pour les exports et autres
