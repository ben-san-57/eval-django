import json
import logging
from typing import Dict, Any, Optional
import requests
from django.conf import settings
from .base_ai_service import BaseAIService

logger = logging.getLogger(__name__)

class MistralService(BaseAIService):
    """Service pour l'intégration avec l'API Mistral AI"""
    
    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        self.model = settings.MISTRAL_MODEL
        self.base_url = settings.MISTRAL_BASE_URL
        
        # Ne pas lever d'erreur immédiatement, mais logger
        if not self.api_key or self.api_key == 'your_mistral_api_key_here':
            logger.warning("⚠️ MISTRAL_API_KEY n'est pas configurée ou utilise la valeur par défaut")
            self.api_key = None
    
    def test_connection(self) -> bool:
        """Teste la connexion à l'API Mistral"""
        if not self.api_key:
            logger.error("❌ Clé API Mistral manquante")
            return False
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Test simple avec un prompt minimal
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "Test"}],
                    "max_tokens": 5
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Connexion Mistral AI OK")
                return True
            elif response.status_code == 401:
                logger.error("❌ Clé API Mistral invalide (401 Unauthorized)")
                return False
            elif response.status_code == 429:
                logger.error("❌ Limite de taux dépassée ou crédit épuisé (429)")
                return False
            else:
                logger.error(f"❌ Erreur connexion Mistral: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur connexion Mistral: {e}")
            return False
    
    def generate_cocktail_recipe(self, user_prompt: str, context: str = "") -> Dict[str, Any]:
        """Génère une recette de cocktail via l'API Mistral"""
        if not self.api_key:
            raise Exception("Clé API Mistral non configurée. Veuillez configurer MISTRAL_API_KEY dans .env")
            
        try:
            # Construction du prompt système
            system_prompt = self._build_system_prompt()
            
            # Construction du prompt utilisateur
            full_user_prompt = f"""
            Demande: {user_prompt}
            {f"Contexte: {context}" if context else ""}
            
            Génère une recette de cocktail créative et détaillée qui répond parfaitement à cette demande.
            """
            
            # Appel à l'API Mistral
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_user_prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 2000
            }
            
            logger.debug(f"🌟 Envoi requête à Mistral avec le modèle {self.model}")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 401:
                raise Exception("Clé API Mistral invalide. Vérifiez votre MISTRAL_API_KEY dans .env")
            elif response.status_code == 429:
                raise Exception("Limite de taux dépassée ou crédit Mistral épuisé. Vérifiez votre compte Mistral.")
            elif response.status_code != 200:
                logger.error(f"❌ Erreur API Mistral: {response.status_code} - {response.text}")
                raise Exception(f"Erreur API Mistral: {response.status_code} - {response.text}")
            
            response_data = response.json()
            ai_response = response_data['choices'][0]['message']['content']
            
            logger.debug(f"✅ Réponse Mistral reçue: {len(ai_response)} caractères")
            
            # Parser la réponse JSON
            cocktail_data = self.parse_ai_response(ai_response)
            
            # Ajouter les métadonnées du modèle
            cocktail_data['ai_model_used'] = f"mistral-{self.model}"
            cocktail_data['ai_service'] = "mistral"
            
            return cocktail_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur parsing JSON Mistral: {e}")
            raise Exception("La réponse de Mistral n'est pas au format JSON attendu")
        except requests.RequestException as e:
            logger.error(f"❌ Erreur réseau Mistral: {e}")
            raise Exception(f"Erreur de connexion à Mistral: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Erreur génération Mistral: {e}")
            raise Exception(f"Erreur lors de la génération avec Mistral: {str(e)}")
    
    def _build_system_prompt(self) -> str:
        """Construit le prompt système pour Mistral"""
        return """Tu es un expert mixologue créatif et innovant. Ta mission est de créer des recettes de cocktails uniques et délicieuses.

IMPORTANT: Tu dois IMPÉRATIVEMENT répondre uniquement avec un JSON valide, sans texte supplémentaire.

Le JSON doit avoir exactement cette structure:
{
  "name": "Nom créatif du cocktail",
  "description": "Description courte et alléchante (50-80 mots)",
  "ingredients": [
    {
      "name": "Nom de l'ingrédient",
      "quantity": "Quantité",
      "unit": "ml/cl/cuillère/trait/etc",
      "type": "spirit/liqueur/mixer/garnish/other"
    }
  ],
  "instructions": [
    "Étape 1 détaillée",
    "Étape 2 détaillée",
    "Étape 3 détaillée"
  ],
  "glassware": "Type de verre recommandé",
  "garnish": "Garniture et décoration",
  "difficulty": "Facile/Moyen/Difficile",
  "preparation_time": "Temps en minutes",
  "serving_size": 1,
  "flavor_profile": ["saveur1", "saveur2", "saveur3"],
  "occasion": "Type d'occasion approprié",
  "strength": "Faible/Modéré/Fort"
}

Règles:
- Utilise des ingrédients réalistes et disponibles
- Assure-toi que les proportions sont équilibrées
- Sois créatif mais réaliste
- Les quantités doivent être précises
- Adapte-toi au contexte et à l'occasion mentionnés
"""
    
    def generate_cocktail(self, user_prompt: str, context: str = "") -> Dict[str, Any]:
        """Génère un cocktail complet via Mistral (méthode pour compatibilité)"""
        return self.generate_cocktail_recipe(user_prompt, context)
    
    def generate_image_prompt(self, cocktail_name: str, cocktail_description: str) -> str:
        """Génère un prompt pour l'image du cocktail"""
        return f"Professional cocktail photography of '{cocktail_name}', {cocktail_description}, elegant glassware, perfect lighting, restaurant quality, 4K resolution"
    
    def generate_image(self, image_prompt: str) -> Optional[str]:
        """Mistral ne génère pas d'images, retourne None"""
        logger.info("Mistral AI ne supporte pas la génération d'images")
        return None
