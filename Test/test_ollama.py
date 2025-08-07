"""
Test du service Ollama avec Llama 3.1
"""
import os
import django
import sys

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')
django.setup()

from cocktails.services.ai_factory import AIServiceFactory

def test_ollama():
    print("🦙 Test du service Ollama avec Llama 3.1")
    print("=" * 50)
    
    try:
        # Initialiser le service
        print("🔄 Initialisation du service IA...")
        ai_service = AIServiceFactory.get_service()
        print(f"✅ Service initialisé: {ai_service.__class__.__name__}")
        
        # Tests de génération de cocktails
        test_prompts = [
            "cocktail fruité pour l'été",
            "boisson sans alcool rafraîchissante", 
            "cocktail élégant pour une soirée"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n🧪 Test {i}: '{prompt}'")
            try:
                cocktail = ai_service.generate_cocktail(prompt)
                print(f"   ✅ Cocktail généré: {cocktail['name']}")
                print(f"   📝 Description: {cocktail['description'][:100]}...")
                print(f"   🍹 Ingrédients: {len(cocktail['ingredients'])} items")
                print(f"   🥃 Verre: {cocktail.get('glass_type', 'N/A')}")
                print(f"   ⏱️ Temps: {cocktail.get('preparation_time', 'N/A')} min")
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        print(f"\n🎉 Tests terminés !")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        print("\n💡 Solutions possibles:")
        print("1. Vérifiez qu'Ollama est démarré: ollama serve")
        print("2. Vérifiez que Llama 3.1 est installé: ollama pull llama3.1")
        print("3. Testez Ollama manuellement: ollama run llama3.1")

if __name__ == "__main__":
    test_ollama()
