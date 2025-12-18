"""
Configuration de la base de données et modèles SQLAlchemy.
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


class Participant(db.Model):
    """
    Modèle pour stocker les participants.
    """
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    participant = db.Column(db.String(255), unique=True, nullable=False, index=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relation avec Association
    association = db.relationship('Association', backref='participant_obj', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Participant {self.participant}>"
    
    def to_dict(self):
        """Convertir en dictionnaire."""
        associated_gift = None
        if self.association and not self.association.is_archived:
            associated_gift = self.association.gift
        
        return {
            "participant": self.participant,
            "associated": self.association is not None and not self.association.is_archived,
            "gift": associated_gift,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Gift(db.Model):
    """
    Modèle pour stocker les cadeaux.
    """
    __tablename__ = 'gifts'
    
    id = db.Column(db.Integer, primary_key=True)
    gift = db.Column(db.Integer, unique=True, nullable=False, index=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relation avec Association
    association = db.relationship('Association', backref='gift_obj', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Gift {self.gift}>"
    
    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            "gift": self.gift,
            "associated": self.association is not None and not self.association.is_archived,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Association(db.Model):
    """
    Modèle pour stocker les associations entre participants et cadeaux.
    """
    __tablename__ = 'associations'
    
    id = db.Column(db.Integer, primary_key=True)
    participant = db.Column(db.String(255), db.ForeignKey('participants.participant', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    gift = db.Column(db.Integer, db.ForeignKey('gifts.gift', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Association {self.participant} -> {self.gift}>"
    
    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            "participant": self.participant,
            "gift": self.gift,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
