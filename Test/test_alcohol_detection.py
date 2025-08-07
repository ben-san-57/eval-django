#!/usr/bin/env python3
"""
Test pour vérifier la détection des cocktails sans alcool
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')
sys.path.append('.')

# Initialiser Django
django.setup()

from cocktails.services.ollama_service import UnifiedCocktailService

def test_alcohol_detection():
    print("🧪 Test de détection d'alcool")
    
    # Créer le service unifié
    service = UnifiedCocktailService()
    
    # Test avec des ingrédients sans alcool
    ingredients_sans_alcool = [
        {'name': 'Jus d\'orange', 'quantity': '200ml'},
        {'name': 'Jus de pomme', 'quantity': '100ml'},
        {'name': 'Sirop de grenadine', 'quantity': '30ml'},
        {'name': 'Eau gazeuse', 'quantity': '50ml'},
        {'name': 'Menthe fraîche', 'quantity': '5 feuilles'},
    ]
    
    # Test avec des ingrédients avec alcool
    ingredients_avec_alcool = [
        {'name': 'Gin', 'quantity': '50ml'},
        {'name': 'Jus de citron', 'quantity': '30ml'},
        {'name': 'Sirop de sureau', 'quantity': '15ml'},
        {'name': 'Eau gazeuse', 'quantity': '100ml'},
    ]
    
    print("\n📊 Test sans alcool :")
    degre_sans_alcool = service._estimate_alcohol_content(ingredients_sans_alcool)
    print(f"   Degré estimé: {degre_sans_alcool}%")
    
    print("\n🍸 Test avec alcool :")
    degre_avec_alcool = service._estimate_alcohol_content(ingredients_avec_alcool)
    print(f"   Degré estimé: {degre_avec_alcool}%")
    
    # Test de la conversion en catégorie
    print("\n🔄 Test de conversion en catégories :")
    def convert_to_category(alcohol_degree):
        if alcohol_degree == 0:
            return 'none'
        elif alcohol_degree < 10:
            return 'low'
        elif alcohol_degree < 20:
            return 'medium'
        else:
            return 'high'
    
    cat_sans = convert_to_category(degre_sans_alcool)
    cat_avec = convert_to_category(degre_avec_alcool)
    
    print(f"   Sans alcool → Catégorie: '{cat_sans}'")
    print(f"   Avec alcool → Catégorie: '{cat_avec}'")

if __name__ == "__main__":
    try:
        test_alcohol_detection()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
