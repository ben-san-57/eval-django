# 🚀 A LIRE AVANT DE COMMENCER - Le Mixologue Augmenté

## 📋 Vue d'ensemble du projet

**Le Mixologue Augmenté** est une application Django avancée qui utilise l'intelligence artificielle pour créer des recettes de cocktails personnalisées. L'application combine Django REST Framework, PostgreSQL, Redis, et des services d'IA (Ollama/Mistral) dans un environnement Docker.

## 🛠️ Prérequis techniques

### Logiciels nécessaires
- **Docker Desktop** (version 20.10+)
- **Git** (version 2.30+)
- **VS Code** avec les extensions :
  - Python
  - Docker
  - Django (optionnel mais recommandé)

### Compétences recommandées
- Django (niveau intermédiaire)
- Docker et Docker Compose
- Python 3.11+
- PostgreSQL
- API REST

## 📁 Structure du projet

```
eval-django/
├── cocktailaiser/          # Configuration Django principale
├── cocktails/              # Application Django principale
│   ├── services/           # Services IA (Ollama, Mistral)
│   ├── management/         # Commandes Django personnalisées
│   └── migrations/         # Migrations de base de données
├── docker/                 # Configuration Docker
├── Instruction/            # Documentation technique
├── static/                 # Fichiers statiques (CSS, JS)
├── templates/              # Templates HTML
├── media/                  # Médias uploadés
└── docker-compose.yml      # Configuration des conteneurs
```

## 🚀 Installation rapide (5 minutes)

### Étape 1 : Cloner le projet
```bash
git clone https://github.com/ben-san-57/eval-django.git
cd eval-django/eval-django
```

### Étape 2 : Vérifier la configuration Docker
```bash
# Vérifier que Docker fonctionne
docker --version
docker-compose --version
```

### Étape 3 : Démarrer l'environnement de développement
```bash
# Construire et démarrer tous les services
docker-compose up --build

# En arrière-plan (optionnel)
docker-compose up --build -d
```

### Étape 4 : Accéder à l'application
- **Application principale** : http://localhost:8000
- **Admin Django** : http://localhost:8000/admin
  - Utilisateur : `admin`
  - Mot de passe : `admin123`
- **Base de données** : localhost:5432
- **Redis** : localhost:6379
- **Ollama** : http://localhost:11434

## 🔧 Configuration de développement

### Variables d'environnement importantes

Le projet utilise plusieurs configurations via `docker-compose.yml` :

```yaml
# IA Services - Actuellement désactivé pour le développement
AI_SERVICE_TYPE=disabled        # Peut être: disabled, ollama, mistral

# Base de données
DATABASE_HOST=postgres
DATABASE_NAME=cocktailaiser_dev
DATABASE_USER=cocktailaiser_user

# Sécurité
DEBUG=True                      # ⚠️ JAMAIS en production
SECRET_KEY=docker-dev-secret-key-change-in-production
```

### Configuration Python/Django

L'environnement Python est configuré automatiquement dans le conteneur Docker. Si vous souhaitez développer localement :

```bash
# Créer un environnement virtuel local (optionnel)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt
```

## 📊 Services et leurs rôles

| Service | Port | Description | Status par défaut |
|---------|------|-------------|-------------------|
| `web` | 8000 | Application Django principale | ✅ Activé |
| `postgres` | 5432 | Base de données PostgreSQL | ✅ Activé |
| `redis` | 6379 | Cache et sessions | ✅ Activé |
| `ollama` | 11434 | IA locale (LLaMA) | ⚠️ Disponible mais IA désactivée |
| `nginx` | 80/443 | Proxy inverse | ❌ Production uniquement |

## 🔍 Commandes utiles

### Docker Compose
```bash
# Démarrer tous les services
docker-compose up

# Démarrer en arrière-plan
docker-compose up -d

# Voir les logs
docker-compose logs -f web

# Redémarrer un service spécifique
docker-compose restart web

# Arrêter tous les services
docker-compose down

# Nettoyer complètement (⚠️ supprime les données)
docker-compose down -v --rmi all
```

### Django dans le conteneur
```bash
# Exécuter des commandes Django
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Shell Django
docker-compose exec web python manage.py shell

# Shell bash dans le conteneur
docker-compose exec web bash
```

## 🐛 Résolution des problèmes courants

### Problème 1 : "no configuration file provided: not found"
**Solution** : Vous n'êtes pas dans le bon répertoire
```bash
cd c:\Git\eval-django\eval-django
ls  # Vérifiez que docker-compose.yml est présent
```

### Problème 2 : Erreur de build Python/requirements.txt
**Solution** : Problème de versions de paquets
```bash
docker-compose down
docker-compose build --no-cache web
docker-compose up
```

### Problème 3 : Base de données non accessible
**Solution** : Attendre que PostgreSQL soit prêt
```bash
# Vérifier le status
docker-compose ps
# Les services doivent être "Up" et "healthy"
```

### Problème 4 : Port 8000 déjà utilisé
**Solution** : Modifier le port dans docker-compose.yml
```yaml
ports:
  - "8001:8000"  # Utiliser le port 8001 à la place
```

## 🎯 Développement avec l'IA

### État actuel
- L'IA est **désactivée** par défaut (`AI_SERVICE_TYPE=disabled`)
- L'application fonctionne normalement sans IA
- Les fonctionnalités IA retournent des messages d'erreur appropriés

### Activation de l'IA (optionnel)
1. Modifier `docker-compose.yml` :
   ```yaml
   - AI_SERVICE_TYPE=ollama  # ou mistral
   ```

2. Redémarrer :
   ```bash
   docker-compose restart web
   ```

3. Attendre le téléchargement du modèle (première fois uniquement)

## 📚 Documentation technique

- `DOCKER_README.md` - Configuration Docker avancée
- `SECURITE.md` - Bonnes pratiques de sécurité
- `MISTRAL_SETUP.md` - Configuration Mistral AI

## 🔄 Workflow de développement recommandé

1. **Démarrer l'environnement** :
   ```bash
   docker-compose up -d
   ```

2. **Faire des modifications** dans le code

3. **Tester les changements** :
   - Django redémarre automatiquement
   - Accéder à http://localhost:8000

4. **Voir les logs** :
   ```bash
   docker-compose logs -f web
   ```

5. **Faire les migrations** si nécessaire :
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

## 🚨 Points d'attention importants

### Sécurité
- ⚠️ **JAMAIS** commiter de vraies clés API
- ⚠️ Changer `SECRET_KEY` en production
- ⚠️ Désactiver `DEBUG` en production

### Performance
- Redis est configuré pour les sessions
- PostgreSQL utilise des volumes persistants
- Les fichiers statiques sont servis par whitenoise

### Base de données
- Les données sont persistantes via Docker volumes
- Superutilisateur créé automatiquement : `admin/admin123`
- Backups automatiques non configurés (à implémenter)

## 🆘 Aide et support

### En cas de blocage :
1. Vérifier les logs : `docker-compose logs -f`
2. Redémarrer les services : `docker-compose restart`
3. Nettoyer et reconstruire : `docker-compose down && docker-compose up --build`

### Ressources utiles :
- Documentation Django : https://docs.djangoproject.com/
- Documentation Docker Compose : https://docs.docker.com/compose/
- Issues GitHub : [Lien vers le repo]

---

## ✅ Checklist de démarrage

- [ ] Docker Desktop installé et démarré
- [ ] Projet cloné dans `c:\Git\eval-django\eval-django`
- [ ] `docker-compose up --build` exécuté avec succès
- [ ] Application accessible sur http://localhost:8000
- [ ] Admin accessible avec admin/admin123
- [ ] Logs consultés : `docker-compose logs -f web`

**🎉 Félicitations ! Vous êtes prêt à développer sur Le Mixologue Augmenté !**

---

*Dernière mise à jour : 7 août 2025*
*Version du guide : 1.0*
