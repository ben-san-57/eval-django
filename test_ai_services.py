"""
Script de test pour les services IA - Ollama et Mistral
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')
django.setup()

from cocktails.services.ai_factory import AIServiceFactory

def test_ai_services():
    """Test des services IA disponibles"""
    print("🧪 Test des services IA disponibles\n")
    
    # Test des modèles disponibles
    available_models = AIServiceFactory.get_available_models()
    print("📋 Modèles configurés:")
    for model_key, model_info in available_models.items():
        status = "✅ Activé" if model_info.get('enabled') else "❌ Désactivé"
        print(f"  {model_info['icon']} {model_info['name']}: {status}")
        print(f"     {model_info['description']}")
    
    print("\n" + "="*50)
    
    # Test Ollama
    print("\n🦙 Test du service Ollama:")
    try:
        ollama_service = AIServiceFactory.get_service('ollama')
        print("✅ Ollama: Service créé avec succès")
    except Exception as e:
        print(f"❌ Ollama: Erreur - {e}")
    
    # Test Mistral (si configuré)
    print("\n🌟 Test du service Mistral:")
    try:
        if settings.MISTRAL_API_KEY:
            mistral_service = AIServiceFactory.get_service('mistral')
            if mistral_service.test_connection():
                print("✅ Mistral: Connexion réussie")
            else:
                print("❌ Mistral: Échec de connexion")
        else:
            print("⚠️ Mistral: API Key non configurée (dans .env)")
    except Exception as e:
        print(f"❌ Mistral: Erreur - {e}")
    
    print("\n" + "="*50)
    print("✅ Tests terminés!")

if __name__ == "__main__":
    test_ai_services()
