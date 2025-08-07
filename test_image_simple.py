#!/usr/bin/env python3
"""
Test simple de génération d'image
"""

import os
import sys

# Setup Django AVANT d'importer quoi que ce soit de Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')

import django
django.setup()

from cocktails.services.ollama_service import OllamaService

def test_image_generation():
    """Test simple de génération d'image"""
    
    print("🎨 Test Génération d'Image Stability AI")
    print("=" * 50)
    
    # Créer le service
    service = OllamaService()
    
    # Vérifier le statut du service d'image
    image_status = service.get_image_service_status()
    print(f"📊 Statut service image:")
    print(f"   - Activé: {image_status['enabled']}")
    print(f"   - Modèle: {image_status['model']}")
    print(f"   - Mode coût: {image_status['cost_mode']}")
    print(f"   - Coût par image: {image_status['cost_per_image']}")
    print(f"   - Images possibles: {image_status.get('with_25_free_credits', 'N/A')}")
    print(f"   - Prêt: {image_status['ready']}")
    print(f"   - API configurée: {image_status['api_key_configured']}")
    
    if not image_status['enabled']:
        print("❌ Service image désactivé")
        return
    
    # Test de génération d'image
    print(f"\n🖼️ Test génération d'image...")
    
    try:
        image_url = service.generate_cocktail_image("Un mojito tropical avec des fruits frais")
        
        print(f"✅ Génération réussie!")
        print(f"   URL: {image_url}")
        
        if image_url.startswith('https://'):
            print("✅ Image réelle générée par Stability AI")
        else:
            print("🔧 Image placeholder utilisée (normal en mode test)")
            
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_generation()
