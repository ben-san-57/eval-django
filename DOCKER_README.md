# ==============================================================================
# README - Déploiement Docker Le Mixologue Augmenté 
# Guide complet pour la containerisation et le déploiement
# ==============================================================================

# 🍸 Le Mixologue Augmenté - Déploiement Docker

Application Django d'IA pour recommandations de cocktails avec déploiement Docker complet.

## 📋 Prérequis

### Logiciels requis
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- 4GB RAM minimum (8GB recommandé avec Ollama)
- 20GB espace disque libre

### Vérification de l'installation
```bash
docker --version
docker-compose --version
```

## 🚀 Déploiement Rapide

### 1. Développement Local
```bash
# Clonage du repository
git clone <votre-repo>
cd eval-django

# Configuration environnement
cp .env.example .env

# Déploiement développement
chmod +x docker/scripts/manage-docker.sh
./docker/scripts/manage-docker.sh deploy-dev
```

**Services disponibles :**
- Application : http://localhost:8000
- Base de données admin : http://localhost:8080 (Adminer)
- Test emails : http://localhost:8025 (MailHog)

### 2. Production
```bash
# Configuration production
cp .env.example .env.production
# ⚠️ MODIFIER .env.production avec vos valeurs !

# Déploiement production
./docker/scripts/manage-docker.sh deploy-prod
```

## 📁 Structure Docker

```
docker/
├── nginx/
│   ├── nginx.prod.conf     # Configuration Nginx principale
│   └── prod.conf          # Configuration serveur production
├── postgres/
│   ├── postgresql.conf     # Optimisations PostgreSQL
│   └── init-db.sh         # Script initialisation DB
├── redis/
│   └── redis.conf         # Configuration Redis sécurisée
└── scripts/
    └── manage-docker.sh   # Script de gestion Docker
```

## 🔧 Configuration Environnement

### Fichiers d'environnement

#### .env.production (OBLIGATOIRE pour production)
```env
# Django
DEBUG=False
SECRET_KEY=votre-cle-secrete-super-longue-et-complexe
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# Base de données
DATABASE_URL=postgresql://user:password@postgres:5432/cocktailaiser_prod
DATABASE_PASSWORD=mot-de-passe-super-securise

# Redis
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=mot-de-passe-redis-securise

# IA Services
HUGGINGFACE_API_TOKEN=votre-token-huggingface
MISTRAL_API_KEY=votre-cle-mistral
STABILITY_API_KEY=votre-cle-stability-ai

# JWT & Sessions
JWT_SECRET_KEY=votre-cle-jwt-unique
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email (optionnel)
EMAIL_HOST=smtp.votre-provider.com
EMAIL_HOST_USER=votre-email@domaine.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe

# Monitoring (optionnel)
GRAFANA_PASSWORD=password-grafana-admin
```

### Services configurés

#### Production (`docker-compose.prod.yml`)
- **Web** : Django + Gunicorn (2 replicas)
- **Database** : PostgreSQL 15 optimisé
- **Cache** : Redis avec persistence
- **Proxy** : Nginx avec SSL/TLS
- **AI** : Ollama (optionnel, via profile)
- **Monitoring** : Prometheus + Grafana (optionnel)

#### Développement (`docker-compose.dev.yml`)
- **Web** : Django runserver + hot reload
- **Database** : PostgreSQL 15
- **Cache** : Redis simple
- **Tools** : Adminer, MailHog
- **AI** : Ollama (optionnel)

## 🛠️ Commandes Utiles

### Gestion des services
```bash
# État des services
./docker/scripts/manage-docker.sh status production
./docker/scripts/manage-docker.sh status development

# Logs des services
./docker/scripts/manage-docker.sh logs production
./docker/scripts/manage-docker.sh logs development web-dev

# Redémarrage d'un service
docker-compose -f docker-compose.prod.yml restart web
```

### Gestion base de données
```bash
# Sauvegarde
./docker/scripts/manage-docker.sh backup production

# Restauration
./docker/scripts/manage-docker.sh restore backup_prod_20240101.sql production

# Migrations Django
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### Maintenance
```bash
# Nettoyage complet
./docker/scripts/manage-docker.sh cleanup all

# Reconstruction images
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Sécurité Production

### SSL/TLS
1. Placez vos certificats dans `docker/ssl/`
2. Modifiez `docker/nginx/prod.conf` avec votre domaine
3. Redémarrez Nginx : `docker-compose -f docker-compose.prod.yml restart nginx`

### Firewall recommandé
```bash
# Autoriser seulement HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 8000/tcp  # Bloquer accès direct Django
ufw deny 5432/tcp  # Bloquer accès direct PostgreSQL
```

### Variables sensibles
- Générez des clés sécurisées : `python generate_secret_key.py`
- Utilisez des mots de passe forts (32+ caractères)
- Activez l'authentification Redis
- Configurez les CORS appropriés

## 📊 Monitoring

### Avec Prometheus + Grafana
```bash
# Activation du monitoring
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# Accès
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin / password depuis .env.production)
```

### Health checks
```bash
# Vérification santé services
curl http://localhost/nginx-health
curl http://localhost:8000/  # Via load balancer
```

## 🐛 Dépannage

### Problèmes courants

#### Service web ne démarre pas
```bash
# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs web

# Vérifier la configuration
docker-compose -f docker-compose.prod.yml config

# Reconstruire l'image
docker-compose -f docker-compose.prod.yml build web --no-cache
```

#### Base de données inaccessible
```bash
# Vérifier PostgreSQL
docker-compose -f docker-compose.prod.yml logs postgres
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Connexion manuelle
docker-compose -f docker-compose.prod.yml exec postgres psql -U cocktailaiser_prod_user -d cocktailaiser_prod
```

#### Problèmes de mémoire
```bash
# Monitoring ressources
docker stats

# Augmenter les limites dans docker-compose.prod.yml
# Ou désactiver Ollama si non nécessaire
docker-compose -f docker-compose.prod.yml stop ollama
```

### Logs détaillés
```bash
# Tous les services
docker-compose -f docker-compose.prod.yml logs -f

# Service specific
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f postgres
docker-compose -f docker-compose.prod.yml logs -f nginx
```

## 🔄 Mise à jour

### Déploiement nouvelle version
```bash
# Pull du code
git pull origin main

# Sauvegarde
./docker/scripts/manage-docker.sh backup production

# Mise à jour
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### Rollback
```bash
# Restaurer version précédente
git checkout previous-working-commit
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Ou restaurer BDD
./docker/scripts/manage-docker.sh restore backup_prod_YYYYMMDD.sql
```

## 📈 Performance

### Optimisations recommandées
- **CPU** : 2-4 cores minimum
- **RAM** : 4GB sans Ollama, 8GB+ avec Ollama
- **Storage** : SSD recommandé
- **Network** : 1Gbps recommandé

### Scaling horizontal
```yaml
# Dans docker-compose.prod.yml
services:
  web:
    deploy:
      replicas: 3  # Augmenter selon besoins
```

### Monitoring performances
```bash
# Métriques en temps réel
docker stats --no-stream
htop
iotop
```

## 📞 Support

### Logs d'audit
- Application : `/app/logs/` dans le conteneur web
- Nginx : `/var/log/nginx/` dans le conteneur nginx
- PostgreSQL : logs via `docker-compose logs postgres`

### Commandes debug
```bash
# Shell dans le conteneur
docker-compose -f docker-compose.prod.yml exec web bash

# Django shell
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Tests
docker-compose -f docker-compose.prod.yml exec web python manage.py test
```

---

## 🏆 Checklist Déploiement Production

- [ ] Fichier `.env.production` configuré
- [ ] Certificats SSL en place
- [ ] Domaine configuré dans Nginx
- [ ] Firewall configuré
- [ ] Sauvegarde automatique configurée
- [ ] Monitoring activé
- [ ] Tests fonctionnels OK
- [ ] Performance validée

**🍸 Votre Mixologue Augmenté est prêt à servir !**
