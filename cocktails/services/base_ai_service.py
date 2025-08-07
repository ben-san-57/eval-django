from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class AIServiceException(Exception):
    """Exception personnalisée pour les erreurs des services IA"""
    pass

class BaseAIService(ABC):
    """Service de base abstrait pour l'intelligence artificielle"""
    
    def __init__(self):
        self.service_name = self.__class__.__name__
    
    @abstractmethod
    def generate_cocktail(self, user_prompt: str, context: str = "", generate_image: bool = True) -> Dict[str, Any]:
        """
        « Propose-moi une fiche cocktail créative basé sur le prompt utilisateur. 
        Le nom du cocktail doit obligatoirement être festif, 
        original, inspirer la fête ou la célébration.
        
        Args:
            user_prompt: La demande de l'utilisateur
            context: Contexte optionnel (occasion, ambiance, cocktail signature pour un enterrement de vie de garçon,
             soirée entre filles, etc.)
            
        Returns:
            Dict contenant:
            - name: Nom du cocktail
            - description: Description/histoire
            - ingredients: Liste des ingrédients
            - music_ambiance: Ambiance musicale
            - image_prompt: Prompt pour génération d'image
            - difficulty_level: Niveau de difficulté
            - alcohol_content: Teneur en alcool
            - preparation_time: Temps de préparation
        """
        pass
    
    @abstractmethod
    def generate_image_prompt(self, cocktail_name: str, cocktail_description: str) -> str:
        """
        Génère un prompt optimisé pour la génération d'image
        
        Args:
            cocktail_name: Nom du cocktail
            cocktail_description: Description du cocktail
            
        Returns:
            Prompt optimisé pour la génération d'image
        """
        pass
    
    @abstractmethod
    def generate_image(self, image_prompt: str) -> Optional[str]:
        """
        Génère une image du cocktail
        
        Args:
            image_prompt: Prompt pour la génération d'image
            
        Returns:
            URL de l'image générée ou None si échec
        """
        pass
    
    def _clean_json_response(self, response_text: str) -> str:
        """Nettoie la réponse pour extraire le JSON valide"""
        try:
            # Chercher le JSON dans la réponse
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                # Valider que c'est du JSON valide
                json.loads(json_str)
                return json_str
            else:
                raise ValueError("Aucun JSON trouvé dans la réponse")
                
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Erreur lors du nettoyage JSON: {e}")
            raise AIServiceException(f"Impossible de parser la réponse JSON: {e}")
    
    def _build_cocktail_prompt(self, user_prompt: str, context: str = "") -> str:
        """Construit le prompt complet pour la génération de cocktail"""
        base_prompt = """Tu es un mixologue expert et créatif. Crée un cocktail original basé sur la demande suivante.

DEMANDE UTILISATEUR: {user_prompt}
CONTEXTE: {context}

Réponds UNIQUEMENT avec un objet JSON valide contenant exactement ces champs:
{{
    "name": "Nom créatif du cocktail",
    "description": "Une histoire courte et engageante du cocktail (2-3 phrases)",
    "ingredients": [
        {{"nom": "Nom de l'ingrédient", "quantité": "Quantité précise"}},
        {{"nom": "Autre ingrédient", "quantité": "Quantité"}}
    ],
    "music_ambiance": "Style musical et artistes recommandés pour accompagner ce cocktail",
    "difficulty_level": "easy|medium|hard",
    "alcohol_content": "none|low|medium|high",
    "preparation_time": 5
}}

Sois créatif avec le nom et l'histoire. Les ingrédients doivent être réalistes et disponibles dans un bar."""
        
        return base_prompt.format(
            user_prompt=user_prompt,
            context=context if context else "Aucun contexte spécifique"
        )
    
    def parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse la réponse JSON de l'IA et la convertit au format attendu"""
        try:
            # Nettoyer et parser le JSON
            clean_json = self._clean_json_response(ai_response)
            data = json.loads(clean_json)
            
            # Convertir au format attendu par l'application
            return {
                'name': data.get('name', 'Cocktail Mystère'),
                'description': data.get('description', 'Un cocktail créé spécialement pour vous'),
                'ingredients': self._format_ingredients(data.get('ingredients', [])),
                'music_ambiance': data.get('music_ambiance', 'Ambiance lounge décontractée'),
                'difficulty_level': data.get('difficulty', 'medium').lower(),
                'alcohol_content': data.get('strength', 'medium').lower(),
                'preparation_time': data.get('preparation_time', '5 minutes'),
                'instructions': data.get('instructions', []),
                'glassware': data.get('glassware', 'Verre à cocktail'),
                'garnish': data.get('garnish', 'Garniture au choix'),
                'flavor_profile': data.get('flavor_profile', []),
                'occasion': data.get('occasion', 'Toute occasion')
            }
        except Exception as e:
            logger.error(f"Erreur parsing réponse IA: {e}")
            raise AIServiceException(f"Erreur lors de l'analyse de la réponse: {e}")
    
    def _format_ingredients(self, ingredients) -> list:
        """Formate la liste des ingrédients au format attendu"""
        formatted = []
        for ingredient in ingredients:
            if isinstance(ingredient, dict):
                # Format nouveau (avec quantity et unit séparés)
                name = ingredient.get('name', ingredient.get('nom', 'Ingrédient inconnu'))
                quantity = ingredient.get('quantity', ingredient.get('quantité', ''))
                unit = ingredient.get('unit', '')
                
                # Si on a quantity et unit, les combiner
                if quantity and unit:
                    full_quantity = f"{quantity} {unit}".strip()
                elif quantity:  # Seulement quantity
                    full_quantity = str(quantity).strip()
                elif unit:  # Seulement unit (rare)
                    full_quantity = unit.strip()
                else:  # Ni quantity ni unit
                    full_quantity = 'À doser'
                
                formatted.append({
                    'nom': name,
                    'quantité': full_quantity
                })
            else:
                # Format ancien (string simple)
                formatted.append({'nom': str(ingredient), 'quantité': 'À doser'})
        return formatted
