"""
API d'authentification avec JWT pour l'application cocktails
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
import json
import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vue personnalisée pour obtenir le token JWT avec informations utilisateur"""
    
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Récupérer l'utilisateur
                username = request.data.get('username')
                user = User.objects.get(username=username)
                
                # Ajouter des informations utilisateur à la réponse
                response.data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'date_joined': user.date_joined.isoformat()
                }
                
                logger.info(f"✅ Connexion JWT réussie pour: {username}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion JWT: {e}")
            return Response(
                {'error': 'Erreur lors de la connexion'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    """API d'inscription avec JWT"""
    try:
        data = json.loads(request.body)
        
        # Validation des données
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        if not username or not email or not password:
            return Response(
                {'error': 'Username, email et password sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Un utilisateur avec ce nom existe déjà'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Un utilisateur avec cet email existe déjà'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"✅ Inscription réussie pour: {username}")
        
        return Response({
            'message': 'Inscription réussie',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'Données JSON invalides'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"❌ Erreur inscription: {e}")
        return Response(
            {'error': 'Erreur lors de l\'inscription'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """API de déconnexion avec blacklist du token"""
    try:
        # Récupérer le refresh token depuis les headers ou le body
        refresh_token = request.data.get("refresh_token") or request.META.get('HTTP_REFRESH_TOKEN')
        
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                logger.info(f"✅ Token blacklisté pour: {request.user.username}")
            except Exception as e:
                logger.warning(f"⚠️ Impossible de blacklister le token: {e}")
        
        # Déconnexion Django traditionnelle
        logout(request)
        logger.info(f"✅ Déconnexion réussie pour: {request.user.username}")
        
        return Response(
            {'message': 'Déconnexion réussie'}, 
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur déconnexion: {e}")
        return Response(
            {'error': 'Erreur lors de la déconnexion'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_api(request):
    """API pour récupérer le profil utilisateur"""
    try:
        user = request.user
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Erreur profil utilisateur: {e}")
        return Response(
            {'error': 'Erreur lors de la récupération du profil'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token_api(request):
    """API pour récupérer le token CSRF"""
    csrf_token = get_token(request)
    return Response({'csrfToken': csrf_token})


@method_decorator(csrf_exempt, name='dispatch')
class SecurityTestView(View):
    """Vue de test pour la sécurité"""
    
    def get(self, request):
        return JsonResponse({
            'message': 'Test de sécurité',
            'user_authenticated': request.user.is_authenticated,
            'user': request.user.username if request.user.is_authenticated else 'Anonymous',
            'csrf_token': get_token(request),
            'headers': dict(request.headers),
        })


# ============================================================================
# VUES TRADITIONNELLES DJANGO (pour compatibilité)
# ============================================================================

def login_view(request):
    """Vue de connexion traditionnelle avec CSRF"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                logger.info(f"✅ Connexion Django réussie pour: {username}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Connexion réussie',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Identifiants invalides'
                }, status=400)
                
        except Exception as e:
            logger.error(f"❌ Erreur connexion Django: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Erreur de connexion'
            }, status=500)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


@csrf_exempt
def logout_view(request):
    """Vue de déconnexion traditionnelle"""
    if request.method == 'POST':
        username = request.user.username if request.user.is_authenticated else 'Anonymous'
        logout(request)
        logger.info(f"✅ Déconnexion Django pour: {username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Déconnexion réussie'
        })
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
