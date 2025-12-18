# 🔐 Système d'authentification JWT

## Vue d'ensemble

Le système d'authentification utilise JWT (JSON Web Tokens) avec :
- **Access tokens** : courte durée (1 heure par défaut), pour l'accès aux ressources protégées
- **Refresh tokens** : longue durée (7 jours par défaut), pour renouveler les access tokens
- **Token blocklist** : révocation des tokens (logout)

## Endpoints disponibles

### 1. Login - `/auth/login` [POST]

Authentifie un administrateur et retourne les tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Connexion réussie",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "admin": {
    "id": 1,
    "username": "admin",
    "created_at": "2025-12-18T10:30:00"
  }
}
```

### 2. Logout - `/auth/logout` [POST]

Révoque un token (ajout à la blocklist).

**Request (Header):**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

Ou **Request (Body):**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Token révoqué avec succès"
}
```

### 3. Refresh - `/auth/refresh` [POST]

Échange un refresh token contre un nouveau access token.

**Request (Header):**
```
Authorization: Bearer <refresh_token>
```

Ou **Request (Body):**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 4. Me - `/auth/me` [GET]

Retourne les informations de l'administrateur authentifié.

**Request (Header):**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "admin": {
    "id": 1,
    "username": "admin",
    "created_at": "2025-12-18T10:30:00"
  }
}
```

## Utilisation du décorateur `@token_required`

Pour protéger vos routes :

```python
from flask import Blueprint, jsonify, g
from utils.auth import token_required

my_bp = Blueprint('my_routes', __name__)

@my_bp.route('/protected', methods=['GET'])
@token_required
def protected_route():
    # Accès aux infos utilisateur via g
    admin_id = g.admin_id
    username = g.admin_username
    
    return jsonify({
        "message": f"Hello {username}!",
        "admin_id": admin_id
    }), 200
```

## Configuration

Variables d'environnement dans [`.env`](.env):

```env
# Configuration JWT
JWT_ALGORITHM=HS256
JWT_EXP_DELTA_SECONDS=3600  # 1 heure
SECRET_KEY=votre-cle-secrete-super-secure
```

## Flux d'authentification recommandé

### 1. Login initial
```
Client → POST /auth/login
       → Stocke access_token et refresh_token
```

### 2. Requêtes authentifiées
```
Client → GET /protected-route
         Header: Authorization: Bearer <access_token>
```

### 3. Rafraîchissement du token
```
Quand access_token expire (401):
Client → POST /auth/refresh
         Body: { "refresh_token": "..." }
       → Stocke le nouveau access_token
       → Réessaye la requête initiale
```

### 4. Logout
```
Client → POST /auth/logout
         Header: Authorization: Bearer <access_token>
       → Supprime les tokens stockés
```

## Structure du Token JWT

### Access Token
```json
{
  "sub": "1",              // ID de l'admin
  "username": "admin",     // Nom d'utilisateur
  "type": "access",        // Type de token
  "jti": "uuid-v4",        // JWT ID unique
  "iat": 1234567890,       // Issued at
  "exp": 1234571490        // Expiration (iat + 3600s)
}
```

### Refresh Token
```json
{
  "sub": "1",              // ID de l'admin
  "type": "refresh",       // Type de token
  "jti": "uuid-v4",        // JWT ID unique
  "iat": 1234567890,       // Issued at
  "exp": 1235172690        // Expiration (iat + 7 jours)
}
```

## Base de données

### Table `token_blocklist`
```sql
CREATE TABLE token_blocklist (
    id INTEGER PRIMARY KEY,
    jti VARCHAR(36) UNIQUE NOT NULL,    -- JWT ID
    token_type VARCHAR(10) NOT NULL,    -- 'access' ou 'refresh'
    admin_id INTEGER,                   -- ID de l'admin
    created_at DATETIME NOT NULL        -- Date de révocation
);
```

## Tests avec curl

### Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"SecurePassword123!"}'
```

### Accès à une route protégée
```bash
curl -X GET http://localhost:5000/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### Refresh
```bash
curl -X POST http://localhost:5000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```

### Logout
```bash
curl -X POST http://localhost:5000/auth/logout \
  -H "Authorization: Bearer <access_token>"
```

## Gestion des administrateurs

Utilisez le script [`admin.py`](admin.py) pour gérer les administrateurs :

```bash
# Créer un admin (utilise les identifiants du .env)
python admin.py create

# Lister les admins
python admin.py list

# Supprimer un admin
python admin.py delete
```

## Sécurité

✅ **Bonnes pratiques implémentées :**
- Tokens signés avec HMAC-SHA256
- Expiration des tokens
- Révocation des tokens via blocklist
- Validation stricte du format Authorization header
- Séparation access/refresh tokens

⚠️ **À faire en production :**
- Changer `SECRET_KEY` (minimum 32 caractères aléatoires)
- Utiliser HTTPS uniquement
- Stocker les tokens de manière sécurisée côté client (httpOnly cookies ou storage sécurisé)
- Nettoyer périodiquement la blocklist des tokens expirés
- Limiter les tentatives de login (rate limiting)

## Erreurs courantes

| Code | Message | Cause |
|------|---------|-------|
| 401 | Missing Authorization Header | Header Authorization absent |
| 401 | Token has expired | Token expiré |
| 401 | Token has been revoked | Token dans la blocklist |
| 401 | A valid access token is required | Refresh token utilisé sur route protégée |
| 400 | Token is not a refresh token | Access token utilisé pour refresh |
