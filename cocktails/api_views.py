"""
Vues API sécurisées pour les cocktails avec JWT
"""

from django.contrib.auth.models import User
from django.db.models import Count, Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
import logging

from .models import CocktailRecipe, GenerationRequest
from .serializers import CocktailRecipeSerializer, GenerationRequestSerializer
from .services.ai_factory import ai_service

logger = logging.getLogger(__name__)


class CocktailRecipeViewSet(viewsets.ModelViewSet):
    """ViewSet pour les recettes de cocktails avec sécurité JWT"""
    
    serializer_class = CocktailRecipeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Retourne seulement les cocktails de l'utilisateur connecté"""
        return CocktailRecipe.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Assigne l'utilisateur connecté au cocktail créé"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle le statut favori d'un cocktail"""
        try:
            cocktail = self.get_object()
            cocktail.is_favorite = not cocktail.is_favorite
            cocktail.save()
            
            logger.info(f"✅ Favori {'ajouté' if cocktail.is_favorite else 'retiré'}: {cocktail.name}")
            
            return Response({
                'is_favorite': cocktail.is_favorite,
                'message': f'Cocktail {"ajouté aux" if cocktail.is_favorite else "retiré des"} favoris'
            })
        except Exception as e:
            logger.error(f"❌ Erreur toggle favori: {e}")
            return Response(
                {'error': 'Erreur lors de la modification des favoris'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Noter un cocktail"""
        try:
            cocktail = self.get_object()
            rating = request.data.get('rating')
            
            if not rating or not (1 <= int(rating) <= 5):
                return Response(
                    {'error': 'La note doit être entre 1 et 5'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cocktail.rating = int(rating)
            cocktail.save()
            
            logger.info(f"✅ Note attribuée: {rating}/5 pour {cocktail.name}")
            
            return Response({
                'rating': cocktail.rating,
                'message': f'Note de {rating}/5 attribuée'
            })
        except Exception as e:
            logger.error(f"❌ Erreur notation: {e}")
            return Response(
                {'error': 'Erreur lors de la notation'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GenerationRequestViewSet(viewsets.ModelViewSet):
    """ViewSet pour les demandes de génération avec sécurité JWT"""
    
    serializer_class = GenerationRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourne seulement les demandes de l'utilisateur connecté"""
        return GenerationRequest.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Assigne l'utilisateur connecté à la demande"""
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_cocktail_api(request):
    """API sécurisée pour générer un cocktail avec IA"""
    try:
        user_prompt = request.data.get('prompt')
        context = request.data.get('context', '')
        
        if not user_prompt:
            return Response(
                {'error': 'Le prompt est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"🤖 Génération cocktail API pour {request.user.username}: {user_prompt}")
        
        # Créer la demande de génération
        generation_request = GenerationRequest.objects.create(
            user=request.user,
            user_prompt=user_prompt,
            context=context
        )
        
        # Générer le cocktail avec l'IA
        cocktail_data = ai_service.generate_cocktail(user_prompt, context)
        
        # Créer le cocktail en base
        recipe = ai_service.create_cocktail_recipe(
            cocktail_data, 
            request.user, 
            generation_request
        )
        
        # Sérialiser la réponse
        serializer = CocktailRecipeSerializer(recipe)
        
        logger.info(f"✅ Cocktail généré via API: {recipe.name}")
        
        return Response({
            'cocktail': serializer.data,
            'generation_request': GenerationRequestSerializer(generation_request).data,
            'message': 'Cocktail généré avec succès'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"❌ Erreur génération cocktail API: {e}")
        return Response(
            {'error': f'Erreur lors de la génération: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_cocktail_history(request):
    """API pour récupérer l'historique des cocktails de l'utilisateur"""
    try:
        # Paramètres de pagination
        page_size = int(request.GET.get('page_size', 10))
        page = int(request.GET.get('page', 1))
        
        # Filtres
        search = request.GET.get('search', '')
        difficulty = request.GET.get('difficulty', '')
        alcohol_content = request.GET.get('alcohol_content', '')
        
        # Base queryset
        queryset = CocktailRecipe.objects.filter(user=request.user)
        
        # Appliquer les filtres
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        if alcohol_content:
            queryset = queryset.filter(alcohol_content=alcohol_content)
        
        # Ordonner par date de création
        queryset = queryset.order_by('-created_at')
        
        # Pagination manuelle
        total_count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        cocktails = queryset[start:end]
        
        # Sérialiser
        serializer = CocktailRecipeSerializer(cocktails, many=True)
        
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur historique utilisateur: {e}")
        return Response(
            {'error': 'Erreur lors de la récupération de l\'historique'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, pk):
    """API pour toggle le statut favori d'un cocktail"""
    try:
        cocktail = CocktailRecipe.objects.get(pk=pk, user=request.user)
        cocktail.is_favorite = not cocktail.is_favorite
        cocktail.save()
        
        logger.info(f"✅ Favori {'ajouté' if cocktail.is_favorite else 'retiré'}: {cocktail.name}")
        
        return Response({
            'is_favorite': cocktail.is_favorite,
            'message': f'Cocktail {"ajouté aux" if cocktail.is_favorite else "retiré des"} favoris'
        })
        
    except CocktailRecipe.DoesNotExist:
        return Response(
            {'error': 'Cocktail non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"❌ Erreur toggle favori: {e}")
        return Response(
            {'error': 'Erreur lors de la modification des favoris'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_favorites(request):
    """API pour récupérer les cocktails favoris de l'utilisateur"""
    try:
        favorites = CocktailRecipe.objects.filter(
            user=request.user, 
            is_favorite=True
        ).order_by('-created_at')
        
        serializer = CocktailRecipeSerializer(favorites, many=True)
        
        return Response({
            'favorites': serializer.data,
            'count': favorites.count()
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur favoris utilisateur: {e}")
        return Response(
            {'error': 'Erreur lors de la récupération des favoris'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """API pour récupérer les statistiques de l'utilisateur"""
    try:
        user = request.user
        now = datetime.now()
        
        # Statistiques générales
        total_cocktails = CocktailRecipe.objects.filter(user=user).count()
        total_favorites = CocktailRecipe.objects.filter(user=user, is_favorite=True).count()
        
        # Statistiques par période
        last_week = now - timedelta(days=7)
        last_month = now - timedelta(days=30)
        
        cocktails_last_week = CocktailRecipe.objects.filter(
            user=user, 
            created_at__gte=last_week
        ).count()
        
        cocktails_last_month = CocktailRecipe.objects.filter(
            user=user, 
            created_at__gte=last_month
        ).count()
        
        # Statistiques par difficulté
        difficulty_stats = CocktailRecipe.objects.filter(user=user).values(
            'difficulty_level'
        ).annotate(count=Count('id'))
        
        # Statistiques par type d'alcool
        alcohol_stats = CocktailRecipe.objects.filter(user=user).values(
            'alcohol_content'
        ).annotate(count=Count('id'))
        
        return Response({
            'user': {
                'username': user.username,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            },
            'cocktails': {
                'total': total_cocktails,
                'favorites': total_favorites,
                'last_week': cocktails_last_week,
                'last_month': cocktails_last_month,
            },
            'difficulty_distribution': list(difficulty_stats),
            'alcohol_distribution': list(alcohol_stats),
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur statistiques utilisateur: {e}")
        return Response(
            {'error': 'Erreur lors de la récupération des statistiques'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
