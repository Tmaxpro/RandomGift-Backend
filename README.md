# 🎯 API d'Association Hommes/Femmes

Backend Flask pour gérer l'association aléatoire de personnes (hommes et femmes représentés par des numéros) avec **persistance en base de données SQLite**.

## 📋 Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Algorithme d'association](#algorithme-dassociation)
- [Architecture](#architecture)
- [Installation](#installation)
- [Lancement](#lancement)
- [Endpoints API](#endpoints-api)
- [Exemples d'utilisation](#exemples-dutilisation)

## ✨ Fonctionnalités

- ✅ Ajouter des hommes (numéros, individuellement ou en masse)
- ✅ Ajouter des femmes (numéros, individuellement ou en masse)
- ✅ Associer aléatoirement selon l'algorithme H-F prioritaire
- ✅ Gérer les listes déséquilibrées (associations même genre)
- ✅ **Authentification JWT avec gestion des administrateurs**
- ✅ **Stockage persistant en base de données SQLite**
- ✅ CORS activé
- ✅ Gestion d'erreurs complète
- ✅ API REST avec réponses JSON

## 🧩 Algorithme d'association

L'algorithme respecte les règles suivantes :

1. **Mélange aléatoire** des deux listes (hommes et femmes)
2. **Priorité H-F** : Associer 1 homme + 1 femme tant que les deux listes contiennent des éléments
3. **Même genre** : Quand une liste est vide, associer les personnes restantes du même genre :
   - Femmes restantes → Couples F-F
   - Hommes restants → Couples H-H
4. **Unicité** : Aucun numéro ne peut apparaître dans plus d'un couple

### Exemple

**Entrée :**
- Hommes : `[10, 11]`
- Femmes : `[1, 2, 3, 4]`

**Sortie :**
```json
{
  "couples": [
    {"type": "H-F", "personne1": 10, "personne2": 3},
    {"type": "H-F", "personne1": 11, "personne2": 1},
    {"type": "F-F", "personne1": 4, "personne2": 2}
  ]
}
```

## 🏗️ Architecture

```
project/
├── app.py                          # Application Flask principale
├── associations.db                 # Base de données SQLite (créée automatiquement)
├── routes/
│   ├── participants.py             # Routes pour les hommes (/participants)
│   ├── gifts.py                    # Routes pour les femmes (/gifts)
│   ├── associations.py             # Routes pour les couples (/associate)
│   ├── auth.py                     # Routes d'authentification
│   ├── export.py                   # Routes d'export (CSV, PDF)
│   └── status.py                   # Routes système (status, health, reset)
├── services/
│   └── association_service.py      # Logique d'association H-F
├── storage/
│   ├── database.py                 # Modèles SQLAlchemy (Homme, Femme, Couple)
│   └── memory_store.py             # Couche d'abstraction pour la base de données
├── utils/
│   └── auth.py                     # Utilitaires JWT
├── requirements.txt                # Dépendances Python
└── README.md                       # Documentation
```

## 📦 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de packages Python)

### Étapes d'installation

1. **Cloner le projet**

```bash
git clone <repository_url>
cd RandomGift-Backend
```

2. **Créer un environnement virtuel (recommandé)**

```bash
python3 -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# ou
venv\Scripts\activate  # Sur Windows
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

## 🚀 Lancement

```bash
python app.py
```

L'API sera accessible sur : **http://localhost:5000**

## 💾 Base de données

L'application utilise **SQLite** pour stocker les données :

- **Fichier** : `associations.db` (créé automatiquement)
- **Tables** :
  - `admins` : Administrateurs avec mot de passe hashé
  - `hommes` : Numéros des hommes
  - `femmes` : Numéros des femmes
  - `couples` : Associations créées (type, personne1, personne2)

## 🔐 Authentification JWT

### Workflow

1. **Se connecter** : `POST /auth/login` → Retourne un token JWT
2. **Utiliser le token** : `Authorization: Bearer <token>` dans les headers

### Endpoints protégés (nécessitent JWT)

- `POST /participants` - Ajouter un homme
- `POST /participants/bulk` - Ajouter plusieurs hommes
- `DELETE /participants/<numero>` - Supprimer un homme
- `POST /gifts` - Ajouter une femme
- `POST /gifts/bulk` - Ajouter plusieurs femmes
- `DELETE /gifts/<numero>` - Supprimer une femme
- `POST /associate` - Créer les couples
- `DELETE /associations/reset` - Réinitialiser les couples

### Endpoints publics

- `GET /` - Documentation API
- `GET /health` - Santé de l'application
- `GET /status` - État complet du système
- `GET /participants` - Lister les hommes
- `GET /gifts` - Lister les femmes
- `GET /associations` - Lister les couples

---

## 📚 Endpoints API

### 🔐 Authentification

#### `POST /auth/login`
Se connecter et obtenir un token JWT

**Body :**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Réponse (200) :**
```json
{
  "success": true,
  "message": "Connexion réussie",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "..."
}
```

---

### 👨 Gestion des Hommes

#### `POST /participants`
Ajouter un homme (numéro)

**🔒 Nécessite authentification JWT**

**Body :**
```json
{
  "numero": 10
}
```

**Réponse (201) :**
```json
{
  "success": true,
  "message": "Homme 10 ajouté avec succès",
  "numero": 10
}
```

---

#### `POST /participants/bulk`
Ajouter plusieurs hommes

**🔒 Nécessite authentification JWT**

**Body JSON :**
```json
{
  "numeros": [10, 11, 12, 13]
}
```

**Ou via fichier CSV/Excel** avec une colonne `numero` ou `homme`

**Réponse (201) :**
```json
{
  "success": true,
  "message": "4 homme(s) ajouté(s), 0 ignoré(s)",
  "added": [10, 11, 12, 13],
  "ignored": []
}
```

---

#### `GET /participants`
Lister tous les hommes

**Réponse (200) :**
```json
{
  "success": true,
  "total": 4,
  "hommes": [10, 11, 12, 13]
}
```

---

#### `DELETE /participants/<numero>`
Supprimer un homme

**🔒 Nécessite authentification JWT**

**Exemple :** `DELETE /participants/10`

---

### 👩 Gestion des Femmes

#### `POST /gifts`
Ajouter une femme (numéro)

**🔒 Nécessite authentification JWT**

**Body :**
```json
{
  "numero": 1
}
```

**Réponse (201) :**
```json
{
  "success": true,
  "message": "Femme 1 ajoutée avec succès",
  "numero": 1
}
```

---

#### `POST /gifts/bulk`
Ajouter plusieurs femmes

**🔒 Nécessite authentification JWT**

**Body JSON :**
```json
{
  "numeros": [1, 2, 3, 4]
}
```

**Réponse (201) :**
```json
{
  "success": true,
  "message": "4 femme(s) ajoutée(s), 0 ignorée(s)",
  "added": [1, 2, 3, 4],
  "ignored": []
}
```

---

#### `GET /gifts`
Lister toutes les femmes

**Réponse (200) :**
```json
{
  "success": true,
  "total": 4,
  "femmes": [1, 2, 3, 4]
}
```

---

#### `DELETE /gifts/<numero>`
Supprimer une femme

**🔒 Nécessite authentification JWT**

**Exemple :** `DELETE /gifts/1`

---

### 💑 Associations / Couples

#### `POST /associate`
Créer les couples à partir des hommes et femmes en base

**🔒 Nécessite authentification JWT**

**Aucun body requis** - L'API récupère automatiquement les hommes et femmes de la base de données.

**Réponse (200) :**
```json
{
  "success": true,
  "message": "3 couple(s) créé(s)",
  "timestamp": "2025-12-19T12:00:00",
  "couples": [
    {"type": "H-F", "personne1": 10, "personne2": 3},
    {"type": "H-F", "personne1": 11, "personne2": 1},
    {"type": "F-F", "personne1": 4, "personne2": 2}
  ],
  "statistiques": {
    "total_personnes": 6,
    "total_couples": 3,
    "couples_H-F": 2,
    "couples_F-F": 1,
    "couples_H-H": 0,
    "personnes_non_associees": 0
  }
}
```

---

#### `GET /associations`
Lister tous les couples créés

**Réponse (200) :**
```json
{
  "success": true,
  "total": 3,
  "couples": [
    {"type": "H-F", "personne1": 10, "personne2": 3},
    {"type": "H-F", "personne1": 11, "personne2": 1},
    {"type": "F-F", "personne1": 4, "personne2": 2}
  ]
}
```

---

#### `DELETE /associations/reset`
Réinitialiser tous les couples (les hommes et femmes restent)

**🔒 Nécessite authentification JWT**

**Réponse (200) :**
```json
{
  "success": true,
  "message": "3 couple(s) supprimé(s)"
}
```

---

### 📊 Système

#### `GET /status`
État complet du système

**Réponse (200) :**
```json
{
  "hommes": {
    "total": 4,
    "list": [10, 11, 12, 13]
  },
  "femmes": {
    "total": 4,
    "list": [1, 2, 3, 4]
  },
  "couples": {
    "total": 3,
    "H-F": 2,
    "F-F": 1,
    "H-H": 0,
    "details": [...]
  }
}
```

#### `GET /health`
Vérification de santé

**Réponse (200) :**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## 🧪 Exemple complet avec cURL

```bash
# 1. Se connecter
TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}' | jq -r '.access_token')

# 2. Ajouter des hommes
curl -X POST http://localhost:5000/participants/bulk \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"numeros": [10, 11]}'

# 3. Ajouter des femmes
curl -X POST http://localhost:5000/gifts/bulk \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"numeros": [1, 2, 3, 4]}'

# 4. Créer les couples
curl -X POST http://localhost:5000/associate \
  -H "Authorization: Bearer $TOKEN"

# 5. Voir les résultats
curl http://localhost:5000/associations
```

---

## 📝 Types de couples

| Type | Description |
|------|-------------|
| `H-F` | Homme + Femme (prioritaire) |
| `F-F` | Femme + Femme (quand plus d'hommes disponibles) |
| `H-H` | Homme + Homme (quand plus de femmes disponibles) |

---

## 🛠️ Technologies utilisées

- **Flask** - Framework web Python
- **SQLAlchemy** - ORM pour SQLite
- **JWT** - Authentification par tokens
- **Flask-CORS** - Gestion des requêtes cross-origin

---

## 📄 Licence

MIT License
