#!/bin/bash
# ==============================================================================
# Script d'initialisation de la base de données PostgreSQL
# Crée la base de données et l'utilisateur pour Le Mixologue Augmenté
# ==============================================================================

set -e

# Configuration
DB_NAME="cocktailaiser_prod"
DB_USER="cocktailaiser_prod_user"
DB_PASSWORD="${DATABASE_PASSWORD:-changeme_in_production}"

echo "🍸 Initialisation de la base de données PostgreSQL pour Le Mixologue Augmenté..."

# Création de l'utilisateur s'il n'existe pas
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE USER $DB_USER WITH PASSWORD '"'"'$DB_PASSWORD'"'"''
    WHERE NOT EXISTS (
        SELECT FROM pg_catalog.pg_roles
        WHERE rolname = '$DB_USER'
    )\\gexec
EOSQL

# Création de la base de données s'elle n'existe pas
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER ENCODING '"'"'UTF8'"'"''
    WHERE NOT EXISTS (
        SELECT FROM pg_database
        WHERE datname = '$DB_NAME'
    )\\gexec
EOSQL

# Attribution des permissions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
    ALTER USER $DB_USER CREATEDB;
EOSQL

# Activation des extensions utiles
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    CREATE EXTENSION IF NOT EXISTS "unaccent";
EOSQL

echo "✅ Base de données $DB_NAME initialisée avec succès!"
echo "👤 Utilisateur: $DB_USER"
echo "🔧 Extensions activées: uuid-ossp, pg_trgm, unaccent"
