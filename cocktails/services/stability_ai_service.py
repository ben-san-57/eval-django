#!/usr/bin/env python3
"""
Service de génération d'images avec Stability AI
"""

import requests
import logging
import os
import base64
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

class StabilityAIService:
    """Service pour générer des images de cocktails avec Stability AI"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'STABILITY_AI_API_KEY', '')
        self.base_url = getattr(settings, 'STABILITY_AI_BASE_URL', 'https://api.stability.ai')
        self.model = getattr(settings, 'STABILITY_AI_MODEL', 'stable-diffusion-v1-6')
        self.enabled = getattr(settings, 'ENABLE_IMAGE_GENERATION', False)
        
        if not self.api_key and self.enabled:
            logger.warning("⚠️ Stability AI API key non configurée, génération d'images désactivée")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Vérifie si la génération d'images est activée"""
        return self.enabled and bool(self.api_key)
    
    def test_connection(self) -> bool:
        """Test de connexion à l'API Stability AI"""
        if not self.is_enabled():
            return False
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Accept': 'application/json',
            }
            
            # Test avec l'endpoint des modèles disponibles
            response = requests.get(
                f'{self.base_url}/v1/engines/list',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Connexion Stability AI OK")
                return True
            else:
                logger.error(f"❌ Erreur connexion Stability AI: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur test connexion Stability AI: {e}")
            return False
    
    def generate_cocktail_image(self, cocktail_data: Dict[str, Any]) -> Optional[str]:
        """
        Génère une image de cocktail basée sur les données du cocktail
        
        Args:
            cocktail_data: Données du cocktail (nom, description, ingrédients, etc.)
            
        Returns:
            str: Chemin vers l'image générée ou None si erreur
        """
        if not self.is_enabled():
            logger.info("🚫 Génération d'images désactivée")
            return None
        
        try:
            # Créer le prompt d'image basé sur les données du cocktail
            image_prompt = self._create_image_prompt(cocktail_data)
            logger.info(f"🎨 Génération image: {image_prompt[:100]}...")
            
            # Appel à l'API Stability AI
            image_data = self._call_stability_api(image_prompt)
            
            if image_data:
                # Sauvegarder l'image
                image_path = self._save_image(image_data, cocktail_data['name'])
                logger.info(f"✅ Image générée: {image_path}")
                return image_path
            else:
                logger.error("❌ Échec génération image")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur génération image: {e}")
            return None
    
    def _create_image_prompt(self, cocktail_data: Dict[str, Any]) -> str:
        """Crée un prompt optimisé pour la génération d'image de cocktail"""
        
        name = cocktail_data.get('name', 'Cocktail')
        description = cocktail_data.get('description', '')
        ingredients = cocktail_data.get('ingredients', [])
        theme = cocktail_data.get('theme', 'moderne')
        
        # Extraire les couleurs principales des ingrédients
        colors = []
        for ing in ingredients[:3]:  # Prendre les 3 premiers ingrédients
            ing_name = ing.get('nom', ing.get('name', '')).lower()
            if 'orange' in ing_name or 'agrume' in ing_name:
                colors.append('orange')
            elif 'citron' in ing_name or 'lime' in ing_name:
                colors.append('jaune citron')
            elif 'menthe' in ing_name:
                colors.append('vert menthe')
            elif 'fraise' in ing_name or 'grenadine' in ing_name:
                colors.append('rouge')
            elif 'gin' in ing_name or 'vodka' in ing_name:
                colors.append('cristallin')
        
        color_desc = ', '.join(colors[:2]) if colors else 'coloré'
        
        # Prompt optimisé pour Stability AI
        prompt = f"""
Professional cocktail photography of "{name}", elegant {theme} style cocktail.
Beautiful {color_desc} drink in appropriate glassware, garnished beautifully.
Studio lighting, clean background, high-end bar setting.
Photorealistic, 4K quality, commercial photography style.
Condensation on glass, perfect lighting, artistic presentation.
""".strip().replace('\n', ' ')
        
        return prompt
    
    def _call_stability_api(self, prompt: str) -> Optional[bytes]:
        """Appelle l'API Stability AI pour générer l'image"""
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        # Utiliser SDXL pour un bon rapport qualité/prix (0.9 crédit)
        data = {
            'text_prompts': [
                {
                    'text': prompt,
                    'weight': 1
                }
            ],
            'cfg_scale': 7,
            'height': 1024,
            'width': 1024,
            'samples': 1,
            'steps': 30,
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'artifacts' in result and result['artifacts']:
                    # Décoder l'image base64
                    image_base64 = result['artifacts'][0]['base64']
                    image_data = base64.b64decode(image_base64)
                    return image_data
                else:
                    logger.error("❌ Aucune image dans la réponse")
                    return None
            else:
                logger.error(f"❌ Erreur API Stability: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur appel API: {e}")
            return None
    
    def _save_image(self, image_data: bytes, cocktail_name: str) -> str:
        """Sauvegarde l'image générée"""
        
        # Nettoyer le nom du cocktail pour le nom de fichier
        clean_name = "".join(c for c in cocktail_name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_name = clean_name.replace(' ', '_').lower()
        
        # Créer un nom de fichier unique
        import uuid
        filename = f"cocktail_{clean_name}_{uuid.uuid4().hex[:8]}.png"
        
        # Sauvegarder dans le dossier media/cocktail_images/
        file_path = f"cocktail_images/{filename}"
        
        # Utiliser Django pour sauvegarder
        saved_path = default_storage.save(file_path, ContentFile(image_data))
        
        return saved_path
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du service"""
        return {
            'enabled': self.is_enabled(),
            'api_key_configured': bool(self.api_key),
            'model': self.model,
            'connection_ok': self.test_connection() if self.is_enabled() else False
        }
