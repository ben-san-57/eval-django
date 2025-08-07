#!/bin/bash
# ==============================================================================
# Scripts de déploiement et gestion Docker pour Le Mixologue Augmenté
# ==============================================================================

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="cocktailaiser"
COMPOSE_PROD_FILE="docker-compose.prod.yml"
COMPOSE_DEV_FILE="docker-compose.dev.yml"

# Fonctions utilitaires
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérification des prérequis
check_requirements() {
    log_info "Vérification des prérequis..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    log_success "Prérequis OK"
}

# Déploiement en production
deploy_production() {
    log_info "🚀 Déploiement en production..."
    
    # Vérification du fichier d'environnement
    if [ ! -f ".env.production" ]; then
        log_error "Fichier .env.production manquant"
        exit 1
    fi
    
    # Build des images
    log_info "Construction des images Docker..."
    docker-compose -f $COMPOSE_PROD_FILE build --no-cache
    
    # Démarrage des services
    log_info "Démarrage des services..."
    docker-compose -f $COMPOSE_PROD_FILE up -d
    
    # Attente que les services soient prêts
    log_info "Attente que les services soient prêts..."
    sleep 30
    
    # Vérification de l'état des services
    if docker-compose -f $COMPOSE_PROD_FILE ps | grep -q "Up"; then
        log_success "Déploiement réussi!"
        show_status "production"
    else
        log_error "Échec du déploiement"
        docker-compose -f $COMPOSE_PROD_FILE logs
        exit 1
    fi
}

# Déploiement en développement
deploy_development() {
    log_info "🛠️ Déploiement en développement..."
    
    # Build des images
    log_info "Construction des images Docker..."
    docker-compose -f $COMPOSE_DEV_FILE build
    
    # Démarrage des services
    log_info "Démarrage des services..."
    docker-compose -f $COMPOSE_DEV_FILE up -d
    
    log_success "Environnement de développement démarré!"
    log_info "Application disponible sur: http://localhost:8000"
    log_info "Adminer disponible sur: http://localhost:8080"
    log_info "MailHog disponible sur: http://localhost:8025"
}

# Affichage du statut
show_status() {
    local env=${1:-"production"}
    local compose_file=""
    
    if [ "$env" = "development" ]; then
        compose_file=$COMPOSE_DEV_FILE
    else
        compose_file=$COMPOSE_PROD_FILE
    fi
    
    log_info "État des services ($env):"
    docker-compose -f $compose_file ps
    
    log_info "Utilisation des ressources:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

# Sauvegarde de la base de données
backup_database() {
    local env=${1:-"production"}
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="backup_${env}_${timestamp}.sql"
    
    log_info "💾 Sauvegarde de la base de données..."
    
    if [ "$env" = "production" ]; then
        docker-compose -f $COMPOSE_PROD_FILE exec postgres pg_dump -U cocktailaiser_prod_user cocktailaiser_prod > $backup_file
    else
        docker-compose -f $COMPOSE_DEV_FILE exec postgres-dev pg_dump -U cocktailaiser_dev_user cocktailaiser_dev > $backup_file
    fi
    
    log_success "Sauvegarde créée: $backup_file"
}

# Restauration de la base de données
restore_database() {
    local backup_file=$1
    local env=${2:-"production"}
    
    if [ -z "$backup_file" ]; then
        log_error "Fichier de sauvegarde requis"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Fichier de sauvegarde introuvable: $backup_file"
        exit 1
    fi
    
    log_warning "⚠️  Restauration de la base de données - ATTENTION: toutes les données actuelles seront perdues!"
    read -p "Continuer? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Restauration annulée"
        exit 0
    fi
    
    log_info "🔄 Restauration de la base de données..."
    
    if [ "$env" = "production" ]; then
        docker-compose -f $COMPOSE_PROD_FILE exec -T postgres psql -U cocktailaiser_prod_user -d cocktailaiser_prod < $backup_file
    else
        docker-compose -f $COMPOSE_DEV_FILE exec -T postgres-dev psql -U cocktailaiser_dev_user -d cocktailaiser_dev < $backup_file
    fi
    
    log_success "Base de données restaurée"
}

# Nettoyage
cleanup() {
    local env=${1:-"all"}
    
    log_warning "🧹 Nettoyage Docker..."
    
    if [ "$env" = "all" ] || [ "$env" = "production" ]; then
        docker-compose -f $COMPOSE_PROD_FILE down -v --remove-orphans
    fi
    
    if [ "$env" = "all" ] || [ "$env" = "development" ]; then
        docker-compose -f $COMPOSE_DEV_FILE down -v --remove-orphans
    fi
    
    # Nettoyage des images inutilisées
    docker image prune -f
    docker volume prune -f
    
    log_success "Nettoyage terminé"
}

# Affichage des logs
show_logs() {
    local env=${1:-"production"}
    local service=$2
    local compose_file=""
    
    if [ "$env" = "development" ]; then
        compose_file=$COMPOSE_DEV_FILE
    else
        compose_file=$COMPOSE_PROD_FILE
    fi
    
    if [ -n "$service" ]; then
        docker-compose -f $compose_file logs -f $service
    else
        docker-compose -f $compose_file logs -f
    fi
}

# Menu d'aide
show_help() {
    echo "🍸 Gestion Docker - Le Mixologue Augmenté"
    echo ""
    echo "Usage: $0 [COMMANDE] [OPTIONS]"
    echo ""
    echo "Commandes disponibles:"
    echo "  deploy-prod              Déployer en production"
    echo "  deploy-dev               Déployer en développement"
    echo "  status [env]             Afficher l'état des services"
    echo "  backup [env]             Sauvegarder la base de données"
    echo "  restore <file> [env]     Restaurer la base de données"
    echo "  logs [env] [service]     Afficher les logs"
    echo "  cleanup [env]            Nettoyer les conteneurs et volumes"
    echo "  help                     Afficher cette aide"
    echo ""
    echo "Environnements: production, development"
    echo ""
    echo "Exemples:"
    echo "  $0 deploy-prod"
    echo "  $0 status development"
    echo "  $0 backup production"
    echo "  $0 restore backup_prod_20240101_120000.sql"
    echo "  $0 logs development web-dev"
}

# Main
main() {
    check_requirements
    
    case "${1:-help}" in
        "deploy-prod")
            deploy_production
            ;;
        "deploy-dev")
            deploy_development
            ;;
        "status")
            show_status "${2:-production}"
            ;;
        "backup")
            backup_database "${2:-production}"
            ;;
        "restore")
            restore_database "$2" "${3:-production}"
            ;;
        "logs")
            show_logs "${2:-production}" "$3"
            ;;
        "cleanup")
            cleanup "${2:-all}"
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Exécution
main "$@"
