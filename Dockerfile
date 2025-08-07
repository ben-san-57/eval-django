# ==============================================================================
# DOCKERFILE - Le Mixologue Augmenté
# ==============================================================================
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Créer utilisateur non-root pour sécurité
RUN useradd --create-home --shell /bin/bash app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copier les requirements et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p /app/media/cocktail_images \
    && mkdir -p /app/static \
    && mkdir -p /app/logs

# Changer les permissions pour l'utilisateur app
RUN chown -R app:app /app
USER app

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput

# Port d'écoute
EXPOSE 8000

# Commande de santé
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Commande par défaut
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "cocktailaiser.wsgi:application"]
