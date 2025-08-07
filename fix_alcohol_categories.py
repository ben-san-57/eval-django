#!/usr/bin/env python3
"""
Script pour corriger les catégories d'alcool dans la base de données
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

def fix_alcohol_categories():
    """Corrige les catégories d'alcool de tous les cocktails existants"""
    
    print("🔧 Correction des catégories d'alcool")
    print("=" * 50)
    
    service = OllamaService()
    cocktails = CocktailRecipe.objects.all()
    
    print(f"📊 {cocktails.count()} cocktails à analyser")
    
    corrections = 0
    
    for cocktail in cocktails:
        if cocktail.ingredients:
            try:
                # Recalculer la catégorie d'alcool
                alcohol_degree = service._estimate_alcohol_content(cocktail.ingredients)
                new_category = service._convert_alcohol_degree_to_category(alcohol_degree)
                
                # Comparer avec l'ancienne
                if new_category != cocktail.alcohol_content:
                    print(f"\n🍹 {cocktail.name}")
                    print(f"   Ancienne: {cocktail.alcohol_content} → Nouvelle: {new_category}")
                    print(f"   Degré calculé: {alcohol_degree:.1f}°")
                    
                    # Mettre à jour
                    cocktail.alcohol_content = new_category
                    cocktail.save()
                    corrections += 1
                    
            except Exception as e:
                print(f"❌ Erreur pour {cocktail.name}: {e}")
    
    print(f"\n✅ Correction terminée: {corrections} cocktails mis à jour")

if __name__ == "__main__":
    fix_alcohol_categories()
