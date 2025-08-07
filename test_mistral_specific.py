"""
Script de test spécifique pour Mistral
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')
django.setup()

from cocktails.services.mistral_service import MistralService

def test_mistral_generation():
    """Test de génération de cocktail avec Mistral"""
    print("🌟 Test de génération Mistral\n")
    
    try:
        # Créer le service
        mistral_service = MistralService()
        print("✅ Service Mistral créé")
        
        # Tester la connexion
        if mistral_service.test_connection():
            print("✅ Connexion Mistral OK")
        else:
            print("❌ Connexion Mistral échoue")
            return
        
        # Test de génération
        print("\n🍹 Génération d'un cocktail de test...")
        result = mistral_service.generate_cocktail_recipe(
            "Un cocktail fruité à base de gin", 
            "Apéritif d'été"
        )
        
        print("✅ Cocktail généré avec succès!")
        print(f"Nom: {result.get('name')}")
        print(f"Service: {result.get('ai_service')}")
        print(f"Modèle: {result.get('ai_model_used')}")
        print(f"Ingrédients: {len(result.get('ingredients', []))} ingrédients")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        print("Traceback complet:")
        traceback.print_exc()

if __name__ == "__main__":
    test_mistral_generation()
