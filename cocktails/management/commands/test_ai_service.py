from django.core.management.base import BaseCommand
from cocktails.services.ai_factory import ai_service
from django.conf import settings

class Command(BaseCommand):
    help = 'Teste la configuration du service Hugging Face'

    def handle(self, *args, **options):
        self.stdout.write("🧪 Test de configuration Hugging Face...\n")
        
        # Vérifier la configuration
        self.stdout.write(f"Type de service: {settings.AI_SERVICE_TYPE}")
        self.stdout.write(f"Modèle texte: {settings.HUGGINGFACE_TEXT_MODEL}")
        self.stdout.write(f"Modèle image: {settings.HUGGINGFACE_IMAGE_MODEL}")
        
        if settings.HUGGINGFACE_API_KEY:
            self.stdout.write(self.style.SUCCESS("✅ Clé API Hugging Face configurée"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  Pas de clé API (rate limiting appliqué)"))
        
        # Test de génération
        self.stdout.write("\n🍹 Test de génération de cocktail...")
        
        try:
            result = ai_service.generate_cocktail(
                "Un cocktail fruité et rafraîchissant", 
                "Test automatique"
            )
            
            self.stdout.write(self.style.SUCCESS(f"✅ Cocktail généré: {result['name']}"))
            self.stdout.write(f"Description: {result['description'][:100]}...")
            self.stdout.write(f"Ingrédients: {len(result['ingredients'])} ingrédients")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur: {e}"))
        
        self.stdout.write("\n✅ Test terminé!")
