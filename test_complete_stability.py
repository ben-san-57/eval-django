#!/usr/bin/env python3
"""
Test final pour valider l'intégration complète de Stability AI
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')
sys.path.append('.')

django.setup()

from cocktails.services.ollama_service import UnifiedCocktailService

def test_complete_integration():
    print("🧪 Test complet de l'intégration Stability AI")
    print("=" * 60)
    
    # 1. Test d'initialisation
    print("\n1️⃣ Test d'initialisation du service...")
    service = UnifiedCocktailService()
    print("✅ Service initialisé avec succès")
    
    # 2. Test du statut détaillé
    print("\n2️⃣ Statut détaillé du service d'images...")
    status = service.get_image_service_status()
    
    for key, value in status.items():
        print(f"   • {key}: {value}")
    
    # 3. Test d'activation/désactivation
    print("\n3️⃣ Test d'activation/désactivation...")
    
    print("   Désactivation...")
    service.disable_image_generation()
    print(f"   → Statut: {service.is_image_generation_enabled()}")
    
    print("   Activation...")
    service.enable_image_generation()
    print(f"   → Statut: {service.is_image_generation_enabled()}")
    
    # 4. Test de génération avec les deux services
    print("\n4️⃣ Test de génération complète...")
    
    test_cases = [
        ("Ollama", "ollama"),
        ("Mistral", "mistral")
    ]
    
    for service_name, service_type in test_cases:
        print(f"\n   🔄 Test avec {service_name}...")
        
        try:
            test_service = UnifiedCocktailService(service_type)
            
            user_prompt = f"Un cocktail festif coloré pour une soirée d'été (test {service_name})"
            cocktail = test_service.generate_cocktail(user_prompt)
            
            print(f"   ✅ Cocktail: {cocktail['name']}")
            print(f"   🎨 Image prompt: {cocktail.get('image_prompt', 'Non généré')[:60]}...")
            print(f"   🖼️ Image: {cocktail.get('image_url', 'Aucune')}")
            print(f"   🍷 Alcool: {cocktail.get('alcohol_content', 'Non défini')}")
            
        except Exception as e:
            print(f"   ❌ Erreur avec {service_name}: {e}")
    
    # 5. Test de configuration
    print(f"\n5️⃣ Instructions de configuration...")
    print(f"   Pour activer Stability AI :")
    print(f"   1. Créer un compte sur https://platform.stability.ai/")
    print(f"   2. Obtenir une clé API (25 crédits gratuits)")
    print(f"   3. Modifier .env : STABILITY_AI_API_KEY=votre_cle")
    print(f"   4. Modifier .env : STABILITY_AI_ENABLED=True")
    print(f"   5. Redémarrer l'application")
    
    print(f"\n🏁 Test complet terminé !")
    print(f"=" * 60)

if __name__ == "__main__":
    test_complete_integration()
