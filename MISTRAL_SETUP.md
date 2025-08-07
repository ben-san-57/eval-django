# Configuration Mistral AI 

## Comment ajouter Mistral AI à votre projet

### 1. Obtenir une clé API Mistral

1. Aller sur [https://console.mistral.ai](https://console.mistral.ai)
2. Créer un compte ou se connecter
3. Aller dans la section "API Keys"
4. Créer une nouvelle clé API
5. Copier la clé (elle ressemble à : `mr-xxx...`)

### 2. Configurer les variables d'environnement

Créez un fichier `.env` dans le répertoire racine (ou modifiez l'existant) :

```bash
# Configuration Django
SECRET_KEY=your_secret_key_here
DEBUG=True

# IA Configuration - Ollama (local)
AI_SERVICE_TYPE=ollama
OLLAMA_MODEL=llama3.1
OLLAMA_BASE_URL=http://127.0.0.1:11434

# IA Configuration - Mistral AI (cloud)
MISTRAL_API_KEY=mr-your-actual-api-key-here
MISTRAL_MODEL=mistral-large-latest
MISTRAL_BASE_URL=https://api.mistral.ai/v1
```

### 3. Modèles Mistral disponibles

- `mistral-tiny` - Le plus rapide et économique
- `mistral-small` - Bon équilibre performance/prix
- `mistral-medium` - Performance élevée
- `mistral-large-latest` - Le plus performant (recommandé pour les cocktails)

### 4. Test de la configuration

Lancez le script de test :

```bash
python test_ai_services.py
```

Vous devriez voir :
```
🌟 Mistral AI: ✅ Activé
✅ Mistral: Connexion réussie
```

### 5. Utilisation

Une fois configuré, les utilisateurs verront deux options dans l'interface :

- 🦙 **Ollama (Local)** - Modèle local Llama 3.1 - Gratuit, privé
- 🌟 **Mistral AI** - Modèle cloud Mistral - Performant, payant

### 6. Coûts approximatifs Mistral

- **mistral-large-latest** : ~0,008$ pour 1000 tokens
- Une génération de cocktail ≈ 500-800 tokens ≈ 0,004-0,006$ par cocktail

### 7. Sécurité

⚠️ **Important** : 
- Ne jamais commit votre `.env` avec la vraie clé API
- Utilisez des variables d'environnement en production
- La clé API donne accès à votre compte Mistral

### 8. En cas de problème

1. Vérifiez que la clé API est correcte
2. Vérifiez votre crédit Mistral
3. Consultez les logs Django pour les erreurs détaillées
4. Testez la connexion avec `python test_ai_services.py`
