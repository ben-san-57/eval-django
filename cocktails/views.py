from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CocktailGenerationForm
from .models import CocktailRecipe, GenerationRequest
from .services.ai_factory import AIServiceFactory
import json
import logging

logger = logging.getLogger(__name__)

def home(request):
    """Page d'accueil"""
    return render(request, 'home.html')

def test_tailwind(request):
    """Page de test Tailwind"""
    return render(request, 'test_tailwind.html')

@login_required
def generate_cocktail_view(request):
    """Vue pour générer un nouveau cocktail"""
    if request.method == 'POST':
        form = CocktailGenerationForm(request.POST)
        if form.is_valid():
            try:
                user_prompt = form.cleaned_data['user_prompt']
                context = form.cleaned_data.get('context', '')
                ai_model = form.cleaned_data.get('ai_model', 'ollama')
                generate_image = form.cleaned_data.get('generate_image', False)
                
                # Créer la demande de génération avec le modèle choisi
                generation_request = GenerationRequest.objects.create(
                    user=request.user,
                    user_prompt=user_prompt,
                    context=context,
                    ai_model=ai_model,
                    generate_image=generate_image
                )
                
                # Obtenir le service IA selon le choix de l'utilisateur
                ai_service = AIServiceFactory.get_service(ai_model)
                
                # Vérifier si le service AI est disponible
                if ai_service is None:
                    messages.error(request, "Le service de génération d'IA n'est pas disponible actuellement. Veuillez réessayer plus tard.")
                    return render(request, 'cocktails/generate.html', {'form': form})
                
                # Générer le cocktail avec l'IA, en passant le choix de génération d'image
                cocktail_data = ai_service.generate_cocktail_recipe(user_prompt, context, generate_image)
                
                # Créer le cocktail en base
                cocktail = CocktailRecipe.objects.create(
                    user=request.user,
                    generation_request=generation_request,
                    name=cocktail_data['name'],
                    description=cocktail_data['description'],
                    ingredients=cocktail_data['ingredients'],
                    music_ambiance=cocktail_data.get('music_ambiance', ''),
                    image_prompt=cocktail_data.get('image_prompt', ''),
                    image_url=cocktail_data.get('image_url', ''),
                    difficulty_level=cocktail_data.get('difficulty_level', 'medium'),
                    alcohol_content=cocktail_data.get('alcohol_content', 'medium'),
                    preparation_time=cocktail_data.get('preparation_time', 5)
                )
                
                messages.success(request, f'Cocktail "{cocktail.name}" créé avec succès!')
                return redirect('cocktails:cocktail_detail', pk=cocktail.pk)
                
            except Exception as e:
                logger.error(f"Erreur lors de la génération de cocktail: {e}")
                messages.error(request, "Erreur lors de la génération du cocktail. Veuillez réessayer.")
    else:
        form = CocktailGenerationForm()
    
    return render(request, 'cocktails/generate.html', {'form': form})

def register_view(request):
    """Vue d'inscription"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé pour {username}! Vous pouvez maintenant vous connecter.')
            return redirect('cocktails:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    """Vue de connexion"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'Vous êtes maintenant connecté en tant que {username}.')
                return redirect('cocktails:home')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe invalide.')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe invalide.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('cocktails:home')

@login_required
def profile_view(request):
    """Vue du profil utilisateur"""
    # Calculer les statistiques
    total_cocktails = CocktailRecipe.objects.filter(user=request.user).count()
    favorite_cocktails = CocktailRecipe.objects.filter(user=request.user, is_favorite=True).count()
    
    context = {
        'total_cocktails': total_cocktails,
        'favorite_cocktails': favorite_cocktails,
    }
    return render(request, 'auth/profile.html', context)

@login_required
def cocktail_detail_view(request, pk):
    """Vue de détail d'un cocktail"""
    try:
        cocktail = CocktailRecipe.objects.get(pk=pk, user=request.user)
        return render(request, 'cocktails/detail.html', {'cocktail': cocktail})
    except CocktailRecipe.DoesNotExist:
        messages.error(request, "Cocktail non trouvé.")
        return redirect('cocktails:history')

@login_required
def cocktail_history_view(request):
    """Vue de l'historique des cocktails avec filtres et pagination"""
    # Récupérer tous les cocktails de l'utilisateur
    cocktails_list = CocktailRecipe.objects.filter(user=request.user).order_by('-created_at')
    
    # Récupérer les paramètres de filtre
    filter_type = request.GET.get('filter', 'all')
    sort_by = request.GET.get('sort', 'date_desc')
    
    # Appliquer les filtres
    filtered_cocktails = cocktails_list
    if filter_type == 'favorites':
        filtered_cocktails = cocktails_list.filter(is_favorite=True)
    elif filter_type == 'alcoholic':
        filtered_cocktails = cocktails_list.exclude(alcohol_content='none')
    elif filter_type == 'non-alcoholic':
        filtered_cocktails = cocktails_list.filter(alcohol_content='none')
    # filter_type == 'all' : pas de filtrage supplémentaire
    
    # Appliquer le tri
    if sort_by == 'date_asc':
        filtered_cocktails = filtered_cocktails.order_by('created_at')
    elif sort_by == 'name_asc':
        filtered_cocktails = filtered_cocktails.order_by('name')
    elif sort_by == 'name_desc':
        filtered_cocktails = filtered_cocktails.order_by('-name')
    # sort_by == 'date_desc' : ordre par défaut déjà appliqué
    
    # Statistiques totales (sur tous les cocktails, pas seulement filtrés)
    total_cocktails = cocktails_list.count()
    cocktails_with_alcohol = cocktails_list.exclude(alcohol_content='none').count()
    cocktails_without_alcohol = cocktails_list.filter(alcohol_content='none').count()
    favorite_cocktails = cocktails_list.filter(is_favorite=True).count()
    
    # Compter les cocktails filtrés
    filtered_count = filtered_cocktails.count()
    
    # Pagination dynamique basée sur la taille d'écran
    # Grande résolution (≥1536px) : 8 cartes par page (4×2 grille)
    # Résolution moyenne (<1536px) : 6 cartes par page (3×2 grille)
    page_size = int(request.GET.get('page_size', 6))  # Default: 6 pour écrans moyens
    # Sécurité : limiter les valeurs possibles
    if page_size not in [6, 8]:
        page_size = 6
    
    paginator = Paginator(filtered_cocktails, page_size)
    page_number = request.GET.get('page', 1)
    cocktails = paginator.get_page(page_number)
    
    # Tous les cocktails non paginés pour le carousel mobile
    all_filtered_cocktails = filtered_cocktails
    
    context = {
        'cocktails': cocktails,
        'all_cocktails': all_filtered_cocktails,  # Tous les cocktails pour le mobile
        'total_cocktails': total_cocktails,
        'filtered_count': filtered_count,
        'cocktails_with_alcohol': cocktails_with_alcohol,
        'cocktails_without_alcohol': cocktails_without_alcohol,
        'favorite_cocktails': favorite_cocktails,
        'current_filter': filter_type,
        'current_sort': sort_by,
        'current_page_size': page_size,
    }
    
    return render(request, 'cocktails/history.html', context)

@login_required 
def toggle_favorite(request, pk):
    """Basculer le statut favori d'un cocktail"""
    try:
        cocktail = CocktailRecipe.objects.get(pk=pk, user=request.user)
        cocktail.is_favorite = not cocktail.is_favorite
        cocktail.save()
        
        if cocktail.is_favorite:
            messages.success(request, f'"{cocktail.name}" ajouté aux favoris!')
        else:
            messages.info(request, f'"{cocktail.name}" retiré des favoris.')
            
        return JsonResponse({
            'success': True, 
            'is_favorite': cocktail.is_favorite
        })
    except CocktailRecipe.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cocktail non trouvé'}, status=404)
