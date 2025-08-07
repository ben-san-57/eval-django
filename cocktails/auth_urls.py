"""
URLs pour l'authentification JWT
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from . import auth_views

app_name = 'auth'

urlpatterns = [
    # JWT Authentication endpoints
    path('login/', auth_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', auth_views.register_api, name='register'),
    path('logout/', auth_views.logout_api, name='logout'),
    path('profile/', auth_views.user_profile_api, name='profile'),
    
    # CSRF Token endpoint
    path('csrf/', auth_views.csrf_token_api, name='csrf_token'),
    
    # Security test endpoint
    path('test/', auth_views.SecurityTestView.as_view(), name='security_test'),
    
    # Traditional Django auth (pour compatibilité)
    path('django/login/', auth_views.login_view, name='django_login'),
    path('django/logout/', auth_views.logout_view, name='django_logout'),
]
