from django.urls import path
from . import views

app_name = 'cocktails'

urlpatterns = [
    path('', views.home, name='home'),
    path('test/', views.test_tailwind, name='test'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('generate/', views.generate_cocktail_view, name='generate'),
    path('cocktail/<uuid:pk>/', views.cocktail_detail_view, name='cocktail_detail'),
    path('cocktail/<uuid:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('history/', views.cocktail_history_view, name='history'),
]
