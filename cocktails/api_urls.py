"""
URLs API pour les cocktails avec sécurité JWT
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'api'

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'cocktails', api_views.CocktailRecipeViewSet, basename='cocktail')
router.register(r'generation-requests', api_views.GenerationRequestViewSet, basename='generation-request')

urlpatterns = [
    # Endpoints sécurisés avec JWT
    path('', include(router.urls)),
    
    # Génération de cocktails
    path('generate/', api_views.generate_cocktail_api, name='generate_cocktail'),
    
    # Historique utilisateur
    path('history/', api_views.user_cocktail_history, name='user_history'),
    
    # Favoris
    path('cocktails/<uuid:pk>/favorite/', api_views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', api_views.user_favorites, name='user_favorites'),
    
    # Statistiques utilisateur
    path('stats/', api_views.user_stats, name='user_stats'),
]
