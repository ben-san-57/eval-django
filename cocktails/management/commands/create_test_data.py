from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cocktails.models import CocktailTag, GenerationRequest, CocktailRecipe
import json

class Command(BaseCommand):
    help = 'Crée des données de test pour les cocktails'

    def handle(self, *args, **options):
        # Créer des tags
        tags_data = [
            {'name': 'Fruité', 'color': '#F59E0B'},
            {'name': 'Tropical', 'color': '#10B981'},
            {'name': 'Classique', 'color': '#8B5CF6'},
            {'name': 'Sans alcool', 'color': '#6B7280'},
            {'name': 'Épicé', 'color': '#EF4444'},
            {'name': 'Rafraîchissant', 'color': '#06B6D4'},
        ]
        
        for tag_data in tags_data:
            tag, created = CocktailTag.objects.get_or_create(
                name=tag_data['name'],
                defaults={'color': tag_data['color']}
            )
            if created:
                self.stdout.write(f"Tag créé: {tag.name}")
        
        # Créer un utilisateur de test si il n'existe pas
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@test.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write("Utilisateur de test créé: testuser / testpass123")
        
        # Créer des cocktails de test
        cocktails_data = [
            {
                'name': 'Sunset Paradise',
                'description': 'Un cocktail tropical qui évoque les couchers de soleil sur une plage paradisiaque. Mélange parfait de fruits exotiques et de rhum.',
                'ingredients': [
                    {'nom': 'Rhum blanc', 'quantité': '5 cl'},
                    {'nom': 'Jus de mangue', 'quantité': '8 cl'},
                    {'nom': 'Jus de passion', 'quantité': '3 cl'},
                    {'nom': 'Sirop de coco', 'quantité': '2 cl'},
                    {'nom': 'Glace pilée', 'quantité': 'À volonté'}
                ],
                'music_ambiance': 'Musique lounge tropical, artistes comme Thievery Corporation ou Boozoo Bajou',
                'difficulty_level': 'easy',
                'alcohol_content': 'medium',
                'preparation_time': 5,
                'user_prompt': 'Je veux quelque chose de tropical et fruité pour une soirée d\'été'
            },
            {
                'name': 'Mystic Garden',
                'description': 'Un cocktail sans alcool aux saveurs herbacées et rafraîchissantes, parfait pour une pause détente en terrasse.',
                'ingredients': [
                    {'nom': 'Concombre', 'quantité': '4 rondelles'},
                    {'nom': 'Menthe fraîche', 'quantité': '8 feuilles'},
                    {'nom': 'Jus de citron vert', 'quantité': '3 cl'},
                    {'nom': 'Sirop d\'agave', 'quantité': '2 cl'},
                    {'nom': 'Eau gazeuse', 'quantité': '15 cl'},
                    {'nom': 'Glaçons', 'quantité': 'À volonté'}
                ],
                'music_ambiance': 'Acoustic chill, artistes comme Norah Jones ou Jack Johnson',
                'difficulty_level': 'easy',
                'alcohol_content': 'none',
                'preparation_time': 3,
                'user_prompt': 'Un cocktail sans alcool pour une après-midi en terrasse'
            }
        ]
        
        for cocktail_data in cocktails_data:
            # Créer la demande de génération
            generation_request = GenerationRequest.objects.create(
                user=test_user,
                user_prompt=cocktail_data['user_prompt'],
                context='Test automatique'
            )
            
            # Créer le cocktail
            cocktail = CocktailRecipe.objects.create(
                user=test_user,
                generation_request=generation_request,
                name=cocktail_data['name'],
                description=cocktail_data['description'],
                ingredients=cocktail_data['ingredients'],
                music_ambiance=cocktail_data['music_ambiance'],
                difficulty_level=cocktail_data['difficulty_level'],
                alcohol_content=cocktail_data['alcohol_content'],
                preparation_time=cocktail_data['preparation_time'],
                image_prompt=f"Cocktail {cocktail_data['name']} in a beautiful glass, professional photography, vibrant colors"
            )
            
            self.stdout.write(f"Cocktail créé: {cocktail.name}")
        
        self.stdout.write(self.style.SUCCESS('Données de test créées avec succès!'))
