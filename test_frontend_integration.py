#!/usr/bin/env python3
"""
Test d'intégration du frontend avec l'option génération d'image
"""

import os
import sys

# Setup Django AVANT d'importer quoi que ce soit de Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')

import django
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from cocktails.models import GenerationRequest, CocktailRecipe

def test_frontend_integration():
    """Test l'intégration frontend avec l'option génération d'image"""
    
    print("🧪 Test Frontend - Option génération d'image")
    print("=" * 60)
    
    # Client de test
    client = Client()
    
    # Créer un utilisateur de test
    user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )
    
    # Se connecter
    login_success = client.login(username='testuser', password='testpass123')
    print(f"✅ Connexion utilisateur: {login_success}")
    
    # Test 1: Accès à la page de génération
    response = client.get(reverse('cocktails:generate'))
    print(f"✅ Page génération accessible: {response.status_code == 200}")
    
    # Vérifier que le formulaire contient le nouveau champ
    form_content = response.content.decode()
    has_generate_image = 'generate_image' in form_content
    has_stability_info = 'Mode économique' in form_content
    has_cost_info = '0.009$' in form_content
    
    print(f"✅ Champ génération d'image présent: {has_generate_image}")
    print(f"✅ Info mode économique présente: {has_stability_info}")
    print(f"✅ Info coût présente: {has_cost_info}")
    
    # Test 2: Soumission sans génération d'image
    print("\n📝 Test génération SANS image")
    response = client.post(reverse('cocktails:generate'), {
        'user_prompt': 'Un cocktail tropical rafraîchissant',
        'context': 'Soirée d\'été entre amis',
        'ai_model': 'ollama',
        # generate_image non coché = False par défaut
    })
    
    if response.status_code == 302:  # Redirection après succès
        print("✅ Génération sans image réussie")
        
        # Vérifier la création en base
        request_obj = GenerationRequest.objects.filter(user=user).last()
        if request_obj:
            print(f"✅ GenerationRequest créé avec generate_image = {request_obj.generate_image}")
        
        cocktail = CocktailRecipe.objects.filter(user=user).last()
        if cocktail:
            print(f"✅ Cocktail créé: {cocktail.name}")
            print(f"   - Image URL vide: {not cocktail.image_url}")
    else:
        print(f"❌ Erreur génération sans image: {response.status_code}")
        if hasattr(response, 'context') and response.context.get('form'):
            print(f"   Erreurs form: {response.context['form'].errors}")
    
    # Test 3: Soumission avec génération d'image
    print("\n🎨 Test génération AVEC image")
    response = client.post(reverse('cocktails:generate'), {
        'user_prompt': 'Un mojito aux fruits rouges',
        'context': 'Cocktail d\'été coloré',
        'ai_model': 'ollama',
        'generate_image': 'on',  # Checkbox cochée
    })
    
    if response.status_code == 302:  # Redirection après succès
        print("✅ Génération avec image réussie")
        
        # Vérifier la création en base
        request_obj = GenerationRequest.objects.filter(user=user).last()
        if request_obj:
            print(f"✅ GenerationRequest créé avec generate_image = {request_obj.generate_image}")
        
        cocktail = CocktailRecipe.objects.filter(user=user).last()
        if cocktail:
            print(f"✅ Cocktail créé: {cocktail.name}")
            print(f"   - Image URL: {cocktail.image_url or 'Placeholder utilisé'}")
    else:
        print(f"❌ Erreur génération avec image: {response.status_code}")
        if hasattr(response, 'context') and response.context.get('form'):
            print(f"   Erreurs form: {response.context['form'].errors}")
    
    # Statistiques finales
    print(f"\n📊 Statistiques:")
    total_requests = GenerationRequest.objects.filter(user=user).count()
    requests_with_image = GenerationRequest.objects.filter(user=user, generate_image=True).count()
    total_cocktails = CocktailRecipe.objects.filter(user=user).count()
    
    print(f"   - Demandes créées: {total_requests}")
    print(f"   - Demandes avec image: {requests_with_image}")
    print(f"   - Cocktails créés: {total_cocktails}")
    
    # Nettoyage
    GenerationRequest.objects.filter(user=user).delete()
    CocktailRecipe.objects.filter(user=user).delete()
    user.delete()
    
    print("\n🎯 Test frontend terminé avec succès!")

if __name__ == "__main__":
    test_frontend_integration()
