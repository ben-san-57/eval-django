"""
Script de test simple pour le nouveau service IA
"""
import sys
import os
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')

try:
    django.setup()
    
    from cocktails.services.ai_factory import AIServiceFactory
    
    print("🤖 Test du nouveau service IA Hugging Face...")
    print("=" * 50)
    
    # Obtenir le service IA
    ai_service = AIServiceFactory.get_service()
    print(f"✅ Service IA initialisé: {ai_service.__class__.__name__}")
    
    # Test de génération de cocktail
    test_prompts = [
        "cocktail fruité pour l'été",
        "boisson sans alcool rafraîchissante",
        "cocktail élégant pour une soirée"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🧪 Test {i}: '{prompt}'")
        try:
            cocktail = ai_service.generate_cocktail(prompt, "Test automatique")
            print(f"   ✅ Nom: {cocktail.get('name', 'N/A')}")
            print(f"   ✅ Ingrédients: {len(cocktail.get('ingredients', []))} items")
            print(f"   ✅ Description: {cocktail.get('description', 'N/A')[:50]}...")
            print(f"   ✅ Image: {'Oui' if cocktail.get('image_url') else 'Non'}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    print("\n🎉 Tests terminés !")
    
except Exception as e:
    print(f"❌ Erreur configuration: {e}")
    print("Assurez-vous que Django est correctement configuré.")
