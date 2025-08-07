"""
Script de test spécifique pour le service Mistral unifié
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')
django.setup()

from cocktails.services.ai_factory import AIServiceFactory

def test_mistral_generation():
    """Test de génération de cocktail avec Mistral utilisant le workflow avancé"""
    print("🌟 Test de génération Mistral avec workflow LangGraph\n")
    
    try:
        # Créer le service Mistral unifié
        mistral_service = AIServiceFactory.get_service('mistral')
        print("✅ Service Mistral unifié créé")
        
        # Tester la connexion
        if mistral_service.test_connection():
            print("✅ Connexion Mistral OK")
        else:
            print("❌ Connexion Mistral échoue")
            return
        
        # Test de génération avec le workflow complet
        print("\n🍹 Génération d'un cocktail de test avec workflow...")
        result = mistral_service.generate_cocktail_recipe(
            "Un cocktail fruité à base de gin pour une soirée d'été", 
            "Apéritif en terrasse"
        )
        
        print("✅ Cocktail généré avec succès!")
        print(f"Nom: {result.get('name')}")
        print(f"Service: {result.get('ai_service')}")
        print(f"Modèle: {result.get('ai_model_used')}")
        print(f"Ingrédients: {len(result.get('ingredients', []))} ingrédients")
        
        # Afficher les ingrédients avec unités
        print("\n📋 Ingrédients détaillés:")
        for ing in result.get('ingredients', []):
            if isinstance(ing, dict):
                nom = ing.get('nom', 'Inconnu')
                quantite = ing.get('quantite', 'À doser')
                print(f"  • {nom}: {quantite}")
            else:
                print(f"  • {ing}")
        
        print(f"\n📖 Description: {result.get('description', 'N/A')}")
        print(f"🎵 Ambiance: {result.get('music_ambiance', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        print("Traceback complet:")
        traceback.print_exc()

if __name__ == "__main__":
    test_mistral_generation()
