-- Script d'initialisation PostgreSQL pour Le Mixologue Augmenté
-- Ce script sera exécuté automatiquement au premier démarrage de PostgreSQL

-- Création des extensions utiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Message de confirmation
SELECT 'Base de données initialisée avec succès pour Le Mixologue Augmenté!' as message;
