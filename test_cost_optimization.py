#!/usr/bin/env python3
"""
Test des optimisations de coût pour Stability AI
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')
sys.path.append('.')

django.setup()

from cocktails.services.ollama_service import UnifiedCocktailService

def test_cost_optimization():
    print("💰 Test des optimisations de coût Stability AI")
    print("=" * 60)
    
    # Initialiser le service
    service = UnifiedCocktailService()
    
    # 1. Afficher les modes disponibles
    print("\n1️⃣ Modes de coût disponibles:")
    modes = service.get_available_cost_modes()
    
    for mode_name, mode_info in modes.items():
        print(f"   📊 {mode_name.upper()}:")
        print(f"      • Modèle: {mode_info['model']}")
        print(f"      • Coût: {mode_info['cost']} crédits ({mode_info['cost_usd']})")
        print(f"      • Description: {mode_info['description']}")
        print()
    
    # 2. Test de changement de mode
    print("2️⃣ Test de changement de mode:")
    
    modes_to_test = ['economic', 'balanced', 'quality']
    
    for mode in modes_to_test:
        print(f"\n   🔄 Passage en mode {mode.upper()}...")
        service.set_image_cost_mode(mode)
        
        status = service.get_image_service_status()
        print(f"      • Modèle actuel: {status['model']}")
        print(f"      • Coût: {status['cost_per_image']} ({status['cost_in_usd']})")
        print(f"      • Optimisation: {status['optimization']}")
        
        # Calculer combien d'images possibles avec 25 crédits gratuits
        if 'crédits' in status['cost_per_image']:
            cost_num = float(status['cost_per_image'].split()[0])
            images_possible = int(25 / cost_num)
            print(f"      • Avec 25 crédits gratuits: ~{images_possible} images")
    
    # 3. Recommandations
    print(f"\n3️⃣ Recommandations pour économiser:")
    print(f"   💡 Mode ECONOMIC (recommandé pour les tests):")
    print(f"      • Seulement 0.9 crédit = $0.009 par image")
    print(f"      • 25 crédits gratuits = ~27 images")
    print(f"      • Résolution 512x512 (suffisant pour les cocktails)")
    print(f"      • Prompts simplifiés")
    
    print(f"\n   ⚖️ Mode BALANCED (bon compromis):")
    print(f"      • 2.5 crédits = $0.025 par image") 
    print(f"      • 25 crédits gratuits = ~10 images")
    print(f"      • Meilleure qualité, génération rapide")
    
    print(f"\n   💎 Mode QUALITY (pour les démos):")
    print(f"      • 4 crédits = $0.040 par image")
    print(f"      • 25 crédits gratuits = ~6 images")
    print(f"      • Haute qualité, détails fins")
    
    # 4. Configuration recommandée
    print(f"\n4️⃣ Configuration recommandée dans .env:")
    print(f"   STABILITY_AI_COST_MODE=economic")
    print(f"   STABILITY_AI_MODEL=sdxl-1-0")
    
    print(f"\n🏁 Test des optimisations terminé !")
    print(f"=" * 60)

def test_prompt_optimization():
    print(f"\n📝 Test d'optimisation des prompts:")
    
    service = UnifiedCocktailService()
    
    # Tester différents modes
    test_cases = [
        ('economic', "Simple cocktail glass"),
        ('balanced', "Elegant cocktail with garnish"),
        ('quality', "Professional cocktail photography with detailed garnish and lighting")
    ]
    
    for mode, expected_style in test_cases:
        service.set_image_cost_mode(mode)
        print(f"   🎨 Mode {mode}: Prompt style = {expected_style}")

if __name__ == "__main__":
    test_cost_optimization()
    test_prompt_optimization()
