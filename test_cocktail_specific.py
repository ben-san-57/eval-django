#!/usr/bin/env python3
"""
Test de détection d'alcool pour un cocktail spécifique
"""

import os
import sys

# Setup Django AVANT d'importer quoi que ce soit de Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')

import django
django.setup()

from cocktails.services.ollama_service import OllamaService
from cocktails.models import CocktailRecipe

def test_specific_cocktail():
    """Test la détection d'alcool pour des cocktails spécifiques"""
    
    print("🧪 Test Détection d'Alcool - Cocktails Spécifiques")
    print("=" * 60)
    
    service = OllamaService()
    
    # Test 1: Rechercher un cocktail avec "rhum" dans le nom
    cocktails_rhum = CocktailRecipe.objects.filter(name__icontains="rhum").order_by('-created_at')[:3]
    cocktails_banane = CocktailRecipe.objects.filter(name__icontains="banane").order_by('-created_at')[:3]
    cocktails_enflam = CocktailRecipe.objects.filter(name__icontains="enflamm").order_by('-created_at')[:3]
    
    all_cocktails = list(cocktails_rhum) + list(cocktails_banane) + list(cocktails_enflam)
    
    if not all_cocktails:
        print("Aucun cocktail trouvé, testons tous les cocktails récents...")
        all_cocktails = CocktailRecipe.objects.all().order_by('-created_at')[:10]
    
    for cocktail in all_cocktails:
        print(f"\n🍹 {cocktail.name}")
        print(f"   Catégorie stockée: {cocktail.alcohol_content}")
        print(f"   Description: {cocktail.description[:100]}...")
        
        # Afficher les ingrédients bruts
        print(f"   Ingrédients bruts: {cocktail.ingredients}")
        print(f"   Type ingrédients: {type(cocktail.ingredients)}")
        
        # Tester la détection
        if cocktail.ingredients:
            try:
                alcohol_degree = service._estimate_alcohol_content(cocktail.ingredients)
                category = service._convert_alcohol_degree_to_category(alcohol_degree)
                
                print(f"   Degré calculé: {alcohol_degree:.1f}°")
                print(f"   Catégorie calculée: {category}")
                
                # Vérifier les mots-clés d'alcool
                alcohol_keywords = ['vodka', 'gin', 'rhum', 'rum', 'whisky', 'whiskey', 'tequila', 'cognac', 'liqueur', 'vin', 'champagne', 'alcool', 'brandy', 'ambré', 'ambre']
                
                ingredients_text = str(cocktail.ingredients).lower()
                found_keywords = [kw for kw in alcohol_keywords if kw in ingredients_text]
                
                print(f"   Mots-clés trouvés: {found_keywords}")
                
                if found_keywords and category == 'none':
                    print(f"   ❌ PROBLÈME: Alcool détecté mais catégorie 'none'!")
                elif not found_keywords and category != 'none':
                    print(f"   ❌ PROBLÈME: Pas d'alcool détecté mais catégorie '{category}'!")
                else:
                    print(f"   ✅ Cohérent")
                    
            except Exception as e:
                print(f"   ❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    test_specific_cocktail()
