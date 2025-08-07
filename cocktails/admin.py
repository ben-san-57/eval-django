from django.contrib import admin
from .models import CocktailRecipe, GenerationRequest, CocktailTag, CocktailRecipeTag

@admin.register(GenerationRequest)
class GenerationRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_prompt_short', 'context', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user_prompt', 'context', 'user__username']
    readonly_fields = ['id', 'created_at']
    
    def user_prompt_short(self, obj):
        return obj.user_prompt[:50] + "..." if len(obj.user_prompt) > 50 else obj.user_prompt
    user_prompt_short.short_description = "Demande"

@admin.register(CocktailRecipe)
class CocktailRecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'difficulty_level', 'alcohol_content', 'is_favorite', 'rating', 'created_at']
    list_filter = ['difficulty_level', 'alcohol_content', 'is_favorite', 'rating', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'user', 'generation_request')
        }),
        ('Ingrédients et préparation', {
            'fields': ('ingredients', 'difficulty_level', 'preparation_time')
        }),
        ('Caractéristiques', {
            'fields': ('alcohol_content', 'music_ambiance', 'image_prompt')
        }),
        ('Évaluation', {
            'fields': ('is_favorite', 'rating')
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(CocktailTag)
class CocktailTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']

@admin.register(CocktailRecipeTag)
class CocktailRecipeTagAdmin(admin.ModelAdmin):
    list_display = ['cocktail', 'tag']
    list_filter = ['tag']
