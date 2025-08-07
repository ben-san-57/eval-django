#!/usr/bin/env python3
"""
Test pour vérifier la correction de détection des cocktails sans alcool
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')
sys.path.append('.')

django.setup()

from cocktails.services.ollama_service import UnifiedCocktailService
import json

def test_non_alcoholic_cocktail():
    print("🧪 Test de génération de cocktail sans alcool")
    
    service = UnifiedCocktailService()
    
    # Test de génération d'un cocktail sans alcool avec Mistral
    user_prompt = "Un cocktail rafraîchissant sans alcool avec des agrumes et de la menthe"
    print(f"📝 Prompt: {user_prompt}")
    
    try:
        # Test avec Mistral
        print("\n🌟 Test avec Mistral...")
        result_mistral = service._generate_cocktail_direct_mistral(user_prompt)
        
        print(f"✅ Cocktail généré: {result_mistral['name']}")
        print(f"📋 Description: {result_mistral['description'][:100]}...")
        print(f"🍸 Ingrédients:")
        for ing in result_mistral['ingredients'][:3]:
            ing_name = ing.get('nom', ing.get('name', 'Ingrédient'))
            ing_qty = ing.get('quantite', ing.get('quantity', 'Quantité'))
            print(f"   • {ing_name}: {ing_qty}")
        
        print(f"🍷 Catégorie d'alcool: '{result_mistral['alcohol_content']}'")
        
        if result_mistral['alcohol_content'] == 'none':
            print("✅ SUCCÈS: Le cocktail est correctement classé comme 'Sans alcool'")
        else:
            print(f"❌ ERREUR: Le cocktail est classé comme '{result_mistral['alcohol_content']}' au lieu de 'none'")
            
    except Exception as e:
        print(f"❌ Erreur lors du test Mistral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_non_alcoholic_cocktail()
