#!/usr/bin/env python3
"""
Test pour vérifier l'intégration de Stability AI dans ollama_service.py
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')
sys.path.append('.')

django.setup()

from cocktails.services.ollama_service import UnifiedCocktailService

def test_stability_integration():
    print("🧪 Test de l'intégration Stability AI")
    
    # Créer le service unifié
    service = UnifiedCocktailService()
    
    # Vérifier le statut du service Stability AI
    stability_status = service.stability_service.get_status()
    
    print(f"\n📊 Statut Stability AI :")
    print(f"   • Activé: {stability_status['enabled']}")
    print(f"   • Clé API configurée: {stability_status['api_key_configured']}")
    print(f"   • Modèle: {stability_status['model']}")
    print(f"   • Prêt: {stability_status['ready']}")
    
    if stability_status['ready']:
        print(f"✅ Stability AI prêt - Génération d'images activée")
    else:
        print(f"⚠️ Stability AI non configuré - Images placeholder utilisées")
    
    # Test de génération de cocktail avec image
    print(f"\n🍹 Test de génération de cocktail avec image...")
    user_prompt = "Un cocktail coloré tropical avec ananas et rhum"
    
    try:
        cocktail = service.generate_cocktail(user_prompt)
        
        print(f"✅ Cocktail généré: {cocktail['name']}")
        print(f"🎨 Prompt d'image: {cocktail.get('image_prompt', 'Non généré')}")
        print(f"🖼️ Chemin image: {cocktail.get('image_url', 'Aucune')}")
        
        # Vérifier si c'est une vraie image ou placeholder
        if 'placeholder_' in cocktail.get('image_url', ''):
            print("📋 Image placeholder utilisée (normal si Stability AI désactivé)")
        else:
            print("🎨 Image générée par Stability AI !")
            
    except Exception as e:
        print(f"❌ Erreur génération cocktail: {e}")
        import traceback
        traceback.print_exc()

def test_image_generation_only():
    print(f"\n🎨 Test direct de génération d'images...")
    
    service = UnifiedCocktailService()
    
    # Test direct du service Stability
    image_prompt = "Beautiful tropical cocktail with pineapple and rum, colorful, professional photography"
    cocktail_name = "Tropical Paradise"
    
    image_url = service.stability_service.generate_image(image_prompt, cocktail_name)
    
    print(f"📸 Prompt: {image_prompt}")
    print(f"🖼️ Image générée: {image_url}")
    
    if 'placeholder_' in image_url:
        print("📋 Image placeholder (Stability AI désactivé ou erreur)")
    else:
        print("✅ Image Stability AI générée avec succès !")

if __name__ == "__main__":
    test_stability_integration()
    test_image_generation_only()
    print(f"\n🏁 Tests terminés !")
