#!/usr/bin/env python3
print("🧪 Test de détection d'alcool")
print("Test simple...")

# Test de base pour voir si le script fonctionne
ingredients_sans_alcool = [
    {'name': 'Jus d\'orange', 'quantity': '200ml'},
    {'name': 'Eau gazeuse', 'quantity': '50ml'}
]

alcohol_keywords = ['vodka', 'gin', 'rhum', 'whisky', 'tequila', 'cognac', 'liqueur', 'vin', 'champagne']

alcohol_count = 0
for ing in ingredients_sans_alcool:
    ing_name = ing.get('name', '') if isinstance(ing, dict) else str(ing)
    if any(keyword in ing_name.lower() for keyword in alcohol_keywords):
        alcohol_count += 1

print(f"Nombre d'alcools détectés: {alcohol_count}")

if alcohol_count == 0:
    alcohol_degree = 0.0
    category = 'none'
else:
    alcohol_degree = 15.0
    category = 'medium'

print(f"Degré d'alcool estimé: {alcohol_degree}%")
print(f"Catégorie: {category}")

print("✅ Test terminé")
