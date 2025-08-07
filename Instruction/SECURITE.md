# 🔒 SÉCURITÉ - Variables d'environnement configurées

## ✅ Variables sécurisées avec .env

### 🎯 Variables CRITIQUES protégées :
- `SECRET_KEY` - Clé secrète Django 
- `DEBUG` - Mode debug (False en production)
- `ALLOWED_HOSTS` - Domaines autorisés
- `CORS_ALLOWED_ORIGINS` - Origines CORS autorisées  
- `CSRF_TRUSTED_ORIGINS` - Origines CSRF de confiance

### 🕒 JWT Configuration (tokens courts pour sécurité) :
- `JWT_ACCESS_TOKEN_MINUTES=15` - Token d'accès : 15 min
- `JWT_REFRESH_TOKEN_HOURS=2` - Token de rafraîchissement : 2h
- `JWT_ROTATE_REFRESH_TOKENS=True` - Rotation automatique
- `JWT_BLACKLIST_AFTER_ROTATION=True` - Blacklist ancien token

### 🍪 Session Configuration (sessions courtes) :
- `SESSION_COOKIE_AGE=1800` - Durée session : 30 min  
- `SESSION_EXPIRE_AT_BROWSER_CLOSE=True` - Expire à fermeture
- `SESSION_SAVE_EVERY_REQUEST=True` - Renouvellement automatique
- `SESSION_COOKIE_HTTPONLY=True` - Protection XSS

### 🤖 IA Configuration :
- `AI_SERVICE_TYPE=ollama`
- `OLLAMA_MODEL=llama3.1`  
- `OLLAMA_BASE_URL=http://127.0.0.1:11434`

### 📊 Logging :
- `LOG_LEVEL=INFO`
- `COCKTAILS_LOG_LEVEL=DEBUG`

## 🚀 Fichiers créés :

1. **`.env`** - Développement (avec tes vraies valeurs)
2. **`.env.production`** - Production (template à remplir)
3. **`generate_secret_key.py`** - Générateur de clés sécurisées

## ⚠️ SÉCURITÉ - Points importants :

### ✅ Maintenant sécurisé :
- Tokens JWT très courts (15min/2h au lieu de 1h/7j)
- Sessions courtes (30min au lieu de 24h)  
- Variables sensibles dans .env
- Pas de valeurs hardcodées dans le code
- Rotation automatique des tokens
- Expiration à la fermeture du navigateur

### 🔐 Pour la production :
1. Génère une nouvelle `SECRET_KEY` : `python generate_secret_key.py`
2. Configure `.env.production` avec tes vraies valeurs
3. Change `DEBUG=False`
4. Configure ton domaine dans `ALLOWED_HOSTS`
5. Utilise HTTPS pour tous les cookies sécurisés

## 📈 Résultat :
**Tu ne resteras plus connecté longtemps !** 
- Token expire en 15min d'inactivité
- Session expire en 30min ou à la fermeture du navigateur
- Refresh token expire en 2h maximum
- Aucune persistance entre redémarrages de serveur

## 🎯 Prochaines étapes optionnelles :
- [ ] Configurer PostgreSQL pour production
- [ ] Configurer Redis pour sessions
- [ ] Ajouter monitoring avec Sentry  
- [ ] Configurer nginx avec SSL/HTTPS
- [ ] Mettre en place backup automatique
