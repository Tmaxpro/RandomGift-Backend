# 🎯 API d'Association de Participants et Cadeaux

Backend Flask complet pour gérer des participants, des cadeaux et leur association aléatoire progressive avec **persistance en base de données SQLite**.

## 📋 Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Lancement](#lancement)
- [Endpoints API](#endpoints-api)
- [Exemples d'utilisation](#exemples-dutilisation)

## ✨ Fonctionnalités

- ✅ Ajouter des participants (individuellement ou en masse)
- ✅ Ajouter des cadeaux (individuellement ou en masse)
- ✅ Associer aléatoirement les éléments non encore associés
- ✅ Supprimer des participants, cadeaux et associations (soft delete avec archivage)
- ✅ Consulter l'état complet des données
- ✅ **Authentification JWT avec gestion des administrateurs**
- ✅ **Horodatage de toutes les actions (created_at, updated_at)**
- ✅ **Export des associations en CSV et PDF**
- ✅ **Soft delete avec is_archived pour garder l'historique**
- ✅ **Stockage persistant en base de données SQLite**
- ✅ CORS activé
- ✅ Gestion d'erreurs complète
- ✅ API REST avec réponses JSON

## 🏗️ Architecture

```
project/
├── app.py                          # Application Flask principale
├── associations.db                 # Base de données SQLite (créée automatiquement)
├── routes/
│   ├── participants.py             # Routes pour les participants
│   ├── gifts.py                    # Routes pour les cadeaux
│   ├── associations.py             # Routes pour les associations
│   ├── auth.py                     # Routes d'authentification (register, login)
│   ├── export.py                   # Routes d'export (CSV, PDF)
│   └── status.py                   # Routes système (status, health, reset)
├── services/
│   └── association_service.py      # Logique d'association aléatoire
├── storage/
│   ├── database.py                 # Modèles SQLAlchemy (Admin, Participant, Gift, Association)
│   └── memory_store.py             # Couche d'abstraction pour la base de données
├── utils/
│   └── auth.py                     # Utilitaires JWT (generate_token, decode_token, token_required)
├── requirements.txt                # Dépendances Python
└── README.md                       # Documentation
```

## 📦 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de packages Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**

```bash
cd Project_association
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

Au premier lancement, la base de données SQLite `associations.db` sera créée automatiquement.

Vous verrez un message de confirmation :

```
============================================================
🚀 Démarrage de l'API d'association
============================================================
📍 URL: http://localhost:5000
📖 Documentation: http://localhost:5000
💚 Health check: http://localhost:5000/health
💾 Base de données: SQLite (associations.db)
============================================================
```

## 💾 Base de données

L'application utilise **SQLite** pour stocker les données de manière persistante :

- **Fichier** : `associations.db` (créé automatiquement dans le dossier du projet)
- **Tables** :
  - `admins` : Stocke les administrateurs avec mot de passe hashé
  - `participants` : Stocke tous les participants avec is_archived, created_at, updated_at
  - `gifts` : Stocke tous les cadeaux avec is_archived, created_at, updated_at
  - `associations` : Stocke les associations avec is_archived, created_at, updated_at
- **Avantages** :
  - Les données persistent entre les redémarrages
  - Pas de serveur de base de données externe requis
  - Fichier unique facile à sauvegarder/restaurer
  - Soft delete avec is_archived pour garder l'historique
  - Horodatage automatique de toutes les actions

## 🔐 Authentification JWT

L'API utilise des tokens JWT (JSON Web Token) pour sécuriser les endpoints sensibles.

### Workflow d'authentification

1. **Enregistrer un administrateur** : `POST /auth/register`
2. **Se connecter** : `POST /auth/login` → Retourne un token JWT
3. **Utiliser le token** : Ajouter `Authorization: Bearer <token>` dans les headers

### Endpoints protégés

Les endpoints suivants nécessitent un token JWT valide :
- POST /participants (ajouter un participant)
- POST /participants/bulk (ajouter plusieurs participants)
- DELETE /participants/<participant> (archiver un participant)
- POST /gifts (ajouter un cadeau)
- POST /gifts/bulk (ajouter plusieurs cadeaux)
- DELETE /gifts/<gift> (archiver un cadeau)
- POST /associate (créer des associations)
- DELETE /associations/<participant> (archiver une association)
- GET /export/csv (exporter en CSV)
- GET /export/pdf (exporter en PDF)

### Endpoints publics

Ces endpoints ne nécessitent pas d'authentification :
- GET / (page d'accueil)
- GET /health (santé de l'application)
- GET /status (état complet du système)
- GET /participants (lister les participants)
- GET /gifts (lister les cadeaux)
- GET /associations (lister les associations)
- POST /auth/register (créer un compte admin)
- POST /auth/login (se connecter)

## 📚 Endpoints API

### 🔐 Authentification

#### `POST /auth/register`
Enregistrer un nouvel administrateur

**Body :**
```json
{
  "username": "admin",
  "password": "securepassword"
}
```

**Réponse (201 Created) :**
```json
{
  "success": true,
  "message": "Administrateur 'admin' créé avec succès",
  "admin": {
    "id": 1,
    "username": "admin",
    "created_at": "2024-01-15 10:30:00"
  }
}
```

**Erreurs :**
- 400 Bad Request : Champs manquants, username trop court (<3 caractères), password trop court (<6 caractères), ou username déjà existant

---

#### `POST /auth/login`
Se connecter et obtenir un token JWT

**Body :**
```json
{
  "username": "admin",
  "password": "securepassword"
}
```

**Réponse (200 OK) :**
```json
{
  "success": true,
  "message": "Connexion réussie",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "admin": {
    "id": 1,
    "username": "admin",
    "created_at": "2024-01-15 10:30:00"
  }
}
```

**Erreurs :**
- 400 Bad Request : Champs manquants
- 401 Unauthorized : Identifiants incorrects

**Note :** Le token JWT est valide pendant 24 heures. Utilisez-le dans le header `Authorization: Bearer <token>` pour les requêtes protégées.

---

### 🏠 Racine

#### `GET /`
Liste tous les endpoints disponibles

**Réponse :**
```json
{
  "message": "API d'association de participants et cadeaux",
  "version": "1.0.0",
  "endpoints": {...}
}
```

---

### 👤 Gestion des Participants

#### `POST /participants`
Ajouter un participant unique

**🔒 Nécessite authentification JWT**

**Headers :**
```
Authorization: Bearer <votre_token_jwt>
```

**Body :**
```json
{
  "participant": "Alice"
}
```

**Réponse (201) :**
```json
{
  "success": true,
  "message": "Participant 'Alice' ajouté avec succès",
  "participant": "Alice"
}
```

#### `POST /participants/bulk`
Ajouter plusieurs participants

**🔒 Nécessite authentification JWT**

**Deux modes d'envoi possibles :**

**Mode 1 - Liste JSON :**
```json
{
  "participants": ["Alice", "Bob", "Charlie"]
}
```

**Clés acceptées :** `participants`, `participant`, `names`, `name`, `noms`, `nom`

**Mode 2 - Fichier CSV/Excel (form-data) :**
- Champ : `file`
- Formats : `.csv`, `.xlsx`, `.xls`
- Le fichier doit contenir une colonne nommée `participant`, `name` ou `nom`

**Exemple de fichier CSV :**
```csv
participant
Alice
Bob
Charlie
```

**Réponse (201) :**
```json
{
  "success": true,
  "message": "3 participant(s) ajouté(s), 0 ignoré(s)",
  "added": ["Alice", "Bob", "Charlie"],
  "ignored": [],
  "total_processed": 3
}
```

#### `GET /participants`
Lister tous les participants

**Réponse (200) :**
```json
{
  "success": true,
  "total": 3,
  "participants": ["Alice", "Bob", "Charlie"]
}
```

#### `DELETE /participants/<participant>`
Supprimer un participant et son association

**Exemple :** `DELETE /participants/Alice`

**Réponse (200) :**
```json
{
  "success": true,
  "message": "Participant 'Alice' supprimé avec succès (ainsi que son association éventuelle)"
}
```

---

### 🎁 Gestion des Cadeaux

#### `POST /gifts`
Ajouter un cadeau unique

**Body :**
```json
{
  "gift": 10
}
```

**Réponse (201) :**
```json
{
  "success": true,
  "message": "Cadeau 10 ajouté avec succès",
  "gift": 10
}
```

#### `POST /gifts/bulk`
Ajouter plusieurs cadeaux

**🔒 Nécessite authentification JWT**

**Deux modes d'envoi possibles :**

**Mode 1 - Liste JSON :**
```json
{
  "gifts": [10, 20, 30]
}
```

**Clés acceptées :** `gifts`, `gift`, `cadeaux`, `cadeau`, `numbers`, `number`, `numéros`

**Mode 2 - Fichier CSV/Excel (form-data) :**
- Champ : `file`
- Formats : `.csv`, `.xlsx`, `.xls`
- Le fichier doit contenir une colonne nommée `gift`, `cadeau` ou `number`

**Exemple de fichier CSV :**
```csv
gift
10
20
30
```

**Réponse (201) :**
```json
{
  "success": true,
  "message": "3 cadeau(x) ajouté(s), 0 ignoré(s)",
  "added": [10, 20, 30],
  "ignored": [],
  "total_processed": 3
}
```

#### `GET /gifts`
Lister tous les cadeaux

**Réponse (200) :**
```json
{
  "success": true,
  "total": 3,
  "gifts": [10, 20, 30]
}
```

#### `DELETE /gifts/<gift>`
Supprimer un cadeau et son association

**Exemple :** `DELETE /gifts/10`

**Réponse (200) :**
```json
{
  "success": true,
  "message": "Cadeau 10 supprimé avec succès (ainsi que son association éventuelle)"
}
```

---

### 🔗 Gestion des Associations

#### `POST /associate`
Créer des associations aléatoires entre participants et cadeaux non associés

**Règles :**
- Seuls les éléments non associés sont utilisés
- Nombre de participants non associés ≤ nombre de cadeaux non associés
- Les associations existantes ne sont jamais modifiées

**Réponse (200) :**
```json
{
  "success": true,
  "message": "2 nouvelle(s) association(s) créée(s)",
  "new_associations": [
    {
      "participant": "Alice",
      "gift": 20
    },
    {
      "participant": "Bob",
      "gift": 10
    }
  ],
  "total_associations": {
    "Alice": 20,
    "Bob": 10
  }
}
```

#### `GET /associations`
Récupérer toutes les associations

**Réponse (200) :**
```json
{
  "success": true,
  "total": 2,
  "associations": {
    "Alice": 20,
    "Bob": 10
  },
  "associations_list": [
    {"participant": "Alice", "gift": 20},
    {"participant": "Bob", "gift": 10}
  ]
}
```

#### `DELETE /associations/<participant>`
Supprimer l'association d'un participant (le cadeau redevient disponible)

**Exemple :** `DELETE /associations/Alice`

**Réponse (200) :**
```json
{
  "success": true,
  "message": "Association du participant 'Alice' supprimée avec succès. Le cadeau est maintenant disponible."
}
```

---

### 📊 Système

#### `GET /status`
État complet du système

**Réponse (200) :**
```json
{
  "success": true,
  "timestamp": "2025-12-18T10:30:00.123456",
  "status": {
    "participants": {
      "total": 5,
      "associated": 3,
      "unassociated": 2,
      "list_associated": ["Alice", "Bob", "Charlie"],
      "list_unassociated": ["David", "Eve"]
    },
    "gifts": {
      "total": 6,
      "associated": 3,
      "unassociated": 3,
      "list_associated": [10, 20, 30],
      "list_unassociated": [40, 50, 60]
    },
    "associations": {
      "total": 3,
      "details": {
        "Alice": 10,
        "Bob": 20,
        "Charlie": 30
      }
    }
  }
}
```

#### `GET /health`
Vérification de santé de l'API

**Réponse (200) :**
```json
{
  "status": "healthy",
  "service": "Association API",
  "version": "1.0.0",
  "timestamp": "2025-12-18T10:30:00.123456"
}
```

#### `DELETE /reset`
Réinitialiser toutes les données

**Réponse (200) :**
```json
{
  "success": true,
  "message": "Toutes les données ont été réinitialisées",
  "previous_data": {
    "names": 5,
    "numbers": 6,
    "associations": 3
  },
  "timestamp": "2025-12-18T10:30:00.123456"
}
```

---

### 📦 Export des données

#### `GET /export/csv`
Exporter toutes les associations non archivées en format CSV

**🔒 Nécessite authentification JWT**

**Headers :**
```
Authorization: Bearer <votre_token_jwt>
```

**Réponse :**
Fichier CSV téléchargeable avec les colonnes :
- Participant
- Gift
- Created At

**Exemple de contenu CSV :**
```csv
Participant,Gift,Created At
Alice,10,2024-01-15 10:30:00
Bob,20,2024-01-15 10:31:00
Charlie,30,2024-01-15 10:32:00
```

**Nom du fichier :** `associations_YYYYMMDD_HHMMSS.csv`

---

#### `GET /export/pdf`
Exporter toutes les associations non archivées en format PDF

**🔒 Nécessite authentification JWT**

**Headers :**
```
Authorization: Bearer <votre_token_jwt>
```

**Réponse :**
Fichier PDF téléchargeable avec :
- Titre : "Rapport des Associations"
- Date de génération
- Total des associations
- Tableau formaté avec : Participant | Cadeau | Date de création
- Design professionnel avec en-tête coloré et alternance de couleurs

**Nom du fichier :** `associations_YYYYMMDD_HHMMSS.pdf`

---

## 🧪 Exemples d'utilisation

### Avec cURL

```bash
# 1. Créer un compte administrateur
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "securepassword"}'

# 2. Se connecter et obtenir un token JWT
TOKEN=$(curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "securepassword"}' \
  | jq -r '.token')

# 3. Ajouter des participants (avec authentification)
curl -X POST http://localhost:5000/participants/bulk \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"participants": ["Alice", "Bob", "Charlie"]}'

# 4. Ajouter des cadeaux (avec authentification)
curl -X POST http://localhost:5000/gifts/bulk \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"gifts": [10, 20, 30, 40]}'

# 5. Créer des associations (avec authentification)
curl -X POST http://localhost:5000/associate \
  -H "Authorization: Bearer $TOKEN"

# 6. Consulter les associations (public)
curl http://localhost:5000/associations

# 7. Consulter le statut (public)
curl http://localhost:5000/status

# 8. Exporter en CSV (avec authentification)
curl http://localhost:5000/export/csv \
  -H "Authorization: Bearer $TOKEN" \
  -o associations.csv

# 9. Exporter en PDF (avec authentification)
curl http://localhost:5000/export/pdf \
  -H "Authorization: Bearer $TOKEN" \
  -o associations.pdf

# 10. Archiver une association (avec authentification)
curl -X DELETE http://localhost:5000/associations/Alice \
  -H "Authorization: Bearer $TOKEN"
```

### Avec Python (requests)

```python
import requests

BASE_URL = "http://localhost:5000"

# 1. Créer un compte administrateur
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={"username": "admin", "password": "securepassword"}
)
print(response.json())

# 2. Se connecter et obtenir un token
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "admin", "password": "securepassword"}
)
token = response.json()['token']
headers = {"Authorization": f"Bearer {token}"}

# 3. Ajouter des participants
response = requests.post(
    f"{BASE_URL}/participants/bulk",
    json={"participants": ["Alice", "Bob", "Charlie"]},
    headers=headers
)
print(response.json())

# 4. Ajouter des cadeaux
response = requests.post(
    f"{BASE_URL}/gifts/bulk",
    json={"gifts": [10, 20, 30, 40]},
    headers=headers
)
print(response.json())

# 5. Créer des associations
response = requests.post(f"{BASE_URL}/associate", headers=headers)
print(response.json())

# 6. Consulter les associations (public)
response = requests.get(f"{BASE_URL}/associations")
print(response.json())

# 7. Exporter en CSV
response = requests.get(f"{BASE_URL}/export/csv", headers=headers)
with open('associations.csv', 'wb') as f:
    f.write(response.content)

# 8. Exporter en PDF
response = requests.get(f"{BASE_URL}/export/pdf", headers=headers)
with open('associations.pdf', 'wb') as f:
    f.write(response.content)
```

### Avec Postman

1. **Import des endpoints :** Créez une nouvelle collection
2. **Configurez l'authentification :**
   - Créez un compte avec `POST /auth/register`
   - Connectez-vous avec `POST /auth/login`
   - Copiez le token JWT reçu
   - Pour les endpoints protégés, ajoutez dans l'onglet "Authorization" :
     - Type: Bearer Token
     - Token: <votre_token_jwt>
3. **Configurez la base URL :** `http://localhost:5000`
4. **Testez les endpoints** dans l'ordre suggéré

---

## ⚠️ Gestion des erreurs

L'API retourne des codes HTTP appropriés :

- `200` : Succès
- `201` : Ressource créée
- `400` : Requête invalide
- `401` : Non authentifié (token manquant ou invalide)
- `403` : Accès refusé
- `404` : Ressource non trouvée
- `500` : Erreur serveur

Exemples d'erreurs :

**Champ manquant :**
```json
{
  "success": false,
  "error": "Le champ 'participant' est requis"
}
```

**Token JWT manquant ou invalide :**
```json
{
  "success": false,
  "error": "Token manquant",
  "message": "Le header Authorization est requis pour cet endpoint"
}
```

```json
{
  "success": false,
  "error": "Token invalide ou expiré",
  "message": "Veuillez vous reconnecter pour obtenir un nouveau token"
}
```

**Identifiants incorrects :**
```json
{
  "success": false,
  "error": "Nom d'utilisateur ou mot de passe incorrect"
}
```

---

## 📝 Notes importantes

- **Stockage en base de données SQLite** : Les données persistent entre les redémarrages
- **Fichier de base de données** : `associations.db` dans le dossier du projet
- **Unicité** : Les participants et cadeaux doivent être uniques
- **Associations uniques** : Un participant ou un cadeau ne peut être associé qu'une seule fois
- **Suppression en cascade** : Supprimer un participant/cadeau supprime aussi son association

## 🔄 Gestion de la base de données

### Sauvegarder les données

```bash
# Copier le fichier de base de données
cp associations.db associations_backup.db
```

### Restaurer les données

```bash
# Remplacer le fichier actuel par la sauvegarde
cp associations_backup.db associations.db
```

### Supprimer toutes les données

- Via l'API : `DELETE /reset`
- Manuellement : Supprimer le fichier `associations.db`

---

## 🔧 Développement

### Mode debug

Le serveur est lancé en mode debug par défaut, permettant le rechargement automatique lors de modifications du code.

### Désactiver le mode debug

Dans [app.py](app.py), modifiez :
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

---

## 📄 Licence

Projet développé à des fins éducatives et de démonstration.

---

## 👨‍💻 Auteur

Développé avec ❤️ en utilisant Flask et Python
