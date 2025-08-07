"""Test simple Mistral"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')

import django
django.setup()

try:
    from cocktails.services.ai_factory import AIServiceFactory
    print("✅ Import Factory OK")
    
    service = AIServiceFactory.get_service('mistral')
    print("✅ Service Mistral créé")
    
    result = service.generate_cocktail("Un cocktail gin fruité pour une soirée d'été", "Apéritif en terrasse")
    print(f"✅ Cocktail: {result['name']}")
    print(f"📋 Description: {result['description']}")
    print(f"🍸 Ingrédients ({len(result['ingredients'])}):")
    
    for ing in result['ingredients']:
        nom = ing.get('nom', 'Inconnu')
        quantite = ing.get('quantite', 'À doser')
        print(f"  • {nom}: {quantite}")
    
    print(f"\n📖 Instructions: {result.get('instructions', 'N/A')}")
    print(f"🎵 Ambiance: {result.get('music_ambiance', 'N/A')}")
    print(f"⚡ Service: {result.get('ai_service')} ({result.get('ai_model_used')})")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
