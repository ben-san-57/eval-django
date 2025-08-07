from django.conf import settings
from .ollama_service import OllamaService
from .base_ai_service import BaseAIService
import logging

logger = logging.getLogger(__name__)

class AIServiceFactory:
    """Factory pour créer des instances de services IA"""
    
    @staticmethod
    def get_service() -> BaseAIService:
        """Retourne une instance du service IA configuré"""
        service_type = getattr(settings, 'AI_SERVICE_TYPE', 'ollama')
        
        if service_type == 'ollama':
            return OllamaService()
        else:
            logger.warning(f"Service IA non reconnu: {service_type}, utilisation d'Ollama par défaut")
            return OllamaService()

# Instance globale pour faciliter l'utilisation
ai_service = AIServiceFactory.get_service()
