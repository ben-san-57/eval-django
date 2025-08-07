from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.conf import settings

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des classes CSS Tailwind à tous les champs
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cocktail-primary focus:border-transparent',
                'placeholder': field.label
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des classes CSS Tailwind
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cocktail-primary focus:border-transparent',
                'placeholder': field.label
            })

class CocktailGenerationForm(forms.Form):
    """Formulaire pour la génération de cocktails par IA"""
    
    user_prompt = forms.CharField(
        label="Décrivez votre cocktail idéal",
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cocktail-primary focus:border-transparent resize-none',
            'placeholder': 'Ex: Je veux quelque chose de fruité avec du gin, pas trop sucré...',
            'rows': 4,
        }),
        help_text="Décrivez vos envies, goûts, l'occasion ou l'ambiance souhaitée",
        max_length=500
    )
    
    context = forms.CharField(
        label="Contexte ou occasion (optionnel)",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cocktail-primary focus:border-transparent',
            'placeholder': 'Ex: Soirée entre amis, apéritif d\'été, cocktail de fête...',
        }),
        required=False,
        max_length=200
    )
    
    ai_model = forms.ChoiceField(
        label="Modèle IA",
        widget=forms.RadioSelect(attrs={
            'class': 'text-cocktail-primary focus:ring-cocktail-primary'
        }),
        help_text="Choisissez le modèle IA pour générer votre cocktail"
    )
    
    generate_image = forms.BooleanField(
        label="Générer une image du cocktail",
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-cocktail-primary bg-gray-100 border-gray-300 rounded focus:ring-cocktail-primary focus:ring-2'
        }),
        help_text="Utiliser Stability AI pour créer une image du cocktail (consomme des crédits)",
        required=False,
        initial=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Construire les choix dynamiquement selon la configuration
        available_models = getattr(settings, 'AVAILABLE_AI_MODELS', {})
        choices = []
        
        for model_key, model_info in available_models.items():
            if model_info.get('enabled', True):
                label = f"{model_info['icon']} {model_info['name']} - {model_info['description']}"
                choices.append((model_key, label))
        
        if not choices:  # Fallback si aucun modèle configuré
            choices = [('ollama', '🦙 Ollama (Local) - Modèle par défaut')]
        
        self.fields['ai_model'].choices = choices
        self.fields['ai_model'].initial = choices[0][0] if choices else 'ollama'
    
    def clean_user_prompt(self):
        prompt = self.cleaned_data['user_prompt'].strip()
        if len(prompt) < 10:
            raise forms.ValidationError("Veuillez décrire plus précisément votre demande (minimum 10 caractères).")
        return prompt
