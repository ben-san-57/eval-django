#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')
django.setup()

from cocktails.models import CocktailRecipe

cocktail = CocktailRecipe.objects.last()
if cocktail:
    print(f'Nom: {cocktail.name}')
    print(f'Ingrédients:')
    for i, ing in enumerate(cocktail.ingredients, 1):
        nom = ing.get('nom', 'N/A')
        quantite = ing.get('quantite', ing.get('quantité', 'N/A'))
        type_ing = ing.get('type', 'N/A')
        print(f'  {i}. {nom}: {quantite} ({type_ing})')
else:
    print('Aucun cocktail trouvé')
