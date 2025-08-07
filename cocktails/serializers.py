"""
Serializers pour l'API REST des cocktails
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CocktailRecipe, GenerationRequest


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les utilisateurs"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class GenerationRequestSerializer(serializers.ModelSerializer):
    """Serializer pour les demandes de génération"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = GenerationRequest
        fields = ['id', 'user', 'user_prompt', 'context', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class CocktailRecipeSerializer(serializers.ModelSerializer):
    """Serializer pour les recettes de cocktails"""
    
    user = UserSerializer(read_only=True)
    generation_request = GenerationRequestSerializer(read_only=True)
    ingredients_count = serializers.SerializerMethodField()
    estimated_cost = serializers.ReadOnlyField()
    
    class Meta:
        model = CocktailRecipe
        fields = [
            'id', 'user', 'generation_request', 'name', 'description',
            'ingredients', 'ingredients_count', 'music_ambiance', 
            'image_prompt', 'image_url', 'difficulty_level', 
            'alcohol_content', 'preparation_time', 'is_favorite', 
            'rating', 'estimated_cost', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'generation_request', 'estimated_cost', 
            'created_at', 'updated_at'
        ]
    
    def get_ingredients_count(self, obj):
        """Retourne le nombre d'ingrédients"""
        if isinstance(obj.ingredients, list):
            return len(obj.ingredients)
        return 0
    
    def validate_rating(self, value):
        """Valide que la note est entre 1 et 5"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("La note doit être entre 1 et 5")
        return value


class CocktailRecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de cocktails"""
    
    class Meta:
        model = CocktailRecipe
        fields = [
            'name', 'description', 'ingredients', 'music_ambiance',
            'image_prompt', 'image_url', 'difficulty_level',
            'alcohol_content', 'preparation_time'
        ]
    
    def validate_ingredients(self, value):
        """Valide le format des ingrédients"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Les ingrédients doivent être une liste")
        
        for ingredient in value:
            if not isinstance(ingredient, dict):
                raise serializers.ValidationError("Chaque ingrédient doit être un objet")
            
            if 'name' not in ingredient:
                raise serializers.ValidationError("Chaque ingrédient doit avoir un nom")
        
        return value


class CocktailRecipeListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les listes de cocktails"""
    
    ingredients_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CocktailRecipe
        fields = [
            'id', 'name', 'description', 'ingredients_count', 
            'difficulty_level', 'alcohol_content', 'preparation_time',
            'is_favorite', 'rating', 'image_url', 'created_at'
        ]
    
    def get_ingredients_count(self, obj):
        """Retourne le nombre d'ingrédients"""
        if isinstance(obj.ingredients, list):
            return len(obj.ingredients)
        return 0
