# Exemple : si vous vouliez ajouter OpenAI GPT
from cocktails.services.base_ai_service import BaseAIService

class OpenAIService(BaseAIService):
    def generate_cocktail(self, user_prompt: str, context: str = "", generate_image: bool = True):
        # Implémentation avec OpenAI GPT
        pass
        
    def generate_image_prompt(self, cocktail_name: str, cocktail_description: str):
        # Implémentation pour OpenAI
        pass
        
    def generate_image(self, image_prompt: str):
        # Utiliser DALL-E par exemple
        pass

# Usage identique dans views.py !
ai_service = AIServiceFactory.get_service('openai')  # Nouveau service
cocktail = ai_service.generate_cocktail_recipe(prompt)  # Même interface
