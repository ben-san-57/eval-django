from django.conf import settings
from .ollama_service import OllamaService, MistralWorkflowService
from .base_ai_service import BaseAIService
import logging

logger = logging.getLogger(__name__)

class AIServiceFactory:
    """Factory pour créer des instances de services IA"""
    
    @staticmethod
    def get_service(service_type: str = None) -> BaseAIService:
        """Retourne une instance du service IA spécifié ou configuré par défaut"""
        if service_type is None:
            service_type = getattr(settings, 'AI_SERVICE_TYPE', 'ollama')
        
        if service_type == 'ollama':
            return OllamaService()
        elif service_type == 'mistral':
            # Utilise le même workflow sophistiqué que Ollama mais avec Mistral
            return MistralWorkflowService()
        else:
            logger.warning(f"Service IA non reconnu: {service_type}, utilisation d'Ollama par défaut")
            return OllamaService()
    
    @staticmethod
    def get_available_models():
        """Retourne la liste des modèles IA disponibles"""
        return getattr(settings, 'AVAILABLE_AI_MODELS', {})

# Instance globale pour faciliter l'utilisation (par défaut)
ai_service = AIServiceFactory.get_service()
