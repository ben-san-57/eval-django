from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid

class GenerationRequest(models.Model):
    """Modèle pour stocker les demandes de génération de cocktails"""
    AI_MODEL_CHOICES = [
        ('ollama', 'Ollama (Local)'),
        ('mistral', 'Mistral AI'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generation_requests')
    user_prompt = models.TextField(
        help_text="La demande originale de l'utilisateur"
    )
    context = models.CharField(
        max_length=200, 
        blank=True, 
        help_text="Contexte ou occasion (ex: enterrement de vie de garçon)"
    )
    ai_model = models.CharField(
        max_length=20,
        choices=AI_MODEL_CHOICES,
        default='ollama',
        help_text="Modèle IA choisi par l'utilisateur"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Demande de génération"
        verbose_name_plural = "Demandes de génération"
    
    def __str__(self):
        return f"{self.user.username} - {self.user_prompt[:50]}..."

class CocktailRecipe(models.Model):
    """Modèle pour stocker les recettes de cocktails générées par l'IA"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cocktail_recipes')
    generation_request = models.ForeignKey(
        GenerationRequest, 
        on_delete=models.CASCADE, 
        related_name='generated_cocktails'
    )
    
    # Informations du cocktail
    name = models.CharField(max_length=200, help_text="Nom créatif du cocktail")
    description = models.TextField(help_text="Histoire/description du cocktail")
    
    # Ingrédients (stocké en JSON ou TextField pour simplicité)
    ingredients = models.JSONField(
        help_text="Liste des ingrédients avec quantités"
    )
    
    # Informations supplémentaires
    music_ambiance = models.TextField(
        blank=True,
        help_text="Ambiance musicale recommandée"
    )
    image_prompt = models.TextField(
        blank=True,
        help_text="Prompt pour génération d'image (MidJourney/SDXL)"
    )
    image_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Chemin vers l'image générée du cocktail"
    )
    
    # Métadonnées
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Facile'),
            ('medium', 'Moyen'),
            ('hard', 'Difficile'),
        ],
        default='medium'
    )
    
    alcohol_content = models.CharField(
        max_length=20,
        choices=[
            ('none', 'Sans alcool'),
            ('low', 'Faible'),
            ('medium', 'Moyen'),
            ('high', 'Fort'),
        ],
        default='medium'
    )
    
    preparation_time = models.PositiveIntegerField(
        default=5,
        help_text="Temps de préparation en minutes"
    )
    
    # Favoris et notation
    is_favorite = models.BooleanField(default=False)
    rating = models.PositiveIntegerField(
        null=True, 
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        help_text="Note de 1 à 5 étoiles"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Recette de cocktail"
        verbose_name_plural = "Recettes de cocktails"
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def get_absolute_url(self):
        return reverse('cocktails:detail', kwargs={'pk': self.pk})
    
    @property
    def ingredients_list(self):
        """Retourne la liste des ingrédients sous forme lisible"""
        if isinstance(self.ingredients, list):
            return self.ingredients
        return []
    
    @property
    def estimated_cost(self):
        """Estimation du coût basé sur le nombre d'ingrédients"""
        ingredient_count = len(self.ingredients_list)
        if ingredient_count <= 3:
            return "€"
        elif ingredient_count <= 5:
            return "€€"
        else:
            return "€€€"

class CocktailTag(models.Model):
    """Tags pour catégoriser les cocktails"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(
        max_length=7, 
        default="#8B5CF6",
        help_text="Couleur hex pour l'affichage"
    )
    
    def __str__(self):
        return self.name

class CocktailRecipeTag(models.Model):
    """Table de liaison many-to-many entre cocktails et tags"""
    cocktail = models.ForeignKey(CocktailRecipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(CocktailTag, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['cocktail', 'tag']
