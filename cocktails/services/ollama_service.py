"""
Service IA utilisant Ollama avec Llama 3.1 et LangGraph pour la génération de cocktails
"""

import logging
import json
import random
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from cocktails.services.base_ai_service import BaseAIService
from cocktails.models import CocktailRecipe

logger = logging.getLogger(__name__)


# État du workflow de génération de cocktail
class CocktailState(BaseModel):
    user_prompt: str = Field(description="Demande originale de l'utilisateur")
    context: str = Field(default="", description="Contexte additionnel")
    cocktail_type: Optional[str] = None
    base_spirits: Optional[list] = None
    flavor_profile: Optional[str] = None
    cocktail_concept: Optional[Dict] = None
    ingredients: Optional[list] = None
    instructions: Optional[str] = None
    final_cocktail: Optional[Dict] = None
    image_prompt: Optional[str] = None


# Modèles Pydantic pour les étapes du workflow
class CocktailType(BaseModel):
    type: str = Field(description="Type de cocktail: 'alcoolisé', 'sans alcool', 'digestif', 'apéritif'")
    occasion: str = Field(description="Occasion: 'soirée', 'déjeuner', 'fête', 'détente'")

class BaseSpirits(BaseModel):
    spirits: list[str] = Field(description="Liste des alcools de base recommandés")
    reasoning: str = Field(description="Explication du choix")

class FlavorProfile(BaseModel):
    profile: str = Field(description="Profil de saveur: 'fruité', 'épicé', 'frais', 'sucré', 'amer'")
    intensity: str = Field(description="Intensité: 'léger', 'moyen', 'intense'")

class CocktailConcept(BaseModel):
    name: str = Field(description="Nom créatif du cocktail")
    description: str = Field(description="Description narrative du cocktail")
    theme: str = Field(description="Thème ou inspiration du cocktail")

class Ingredient(BaseModel):
    nom: str = Field(description="Nom de l'ingrédient")
    quantite: str = Field(description="Quantité avec unité SI obligatoire (ex: '50 ml', '10 g', '2 pincées')")
    type: str = Field(description="Type: 'alcool', 'mixer', 'garniture', 'épice', 'autre'")

class CocktailIngredients(BaseModel):
    ingredients: list[Ingredient] = Field(
        description="Liste détaillée des ingrédients avec quantités en unités SI (ml pour liquides, g pour solides)"
    )

class CocktailInstructions(BaseModel):
    instructions: str = Field(description="Instructions de préparation étape par étape")
    glass_type: str = Field(description="Type de verre recommandé")
    garnish: str = Field(description="Garniture et décoration")
    difficulty: str = Field(description="Niveau de difficulté")

class ImagePrompt(BaseModel):
    prompt: str = Field(description="Prompt pour générer l'image du cocktail")


class OllamaService(BaseAIService):
    """Service IA utilisant Ollama avec Llama 3.1 et workflow LangGraph"""
    
    def __init__(self):
        super().__init__()
        try:
            self.llm = ChatOllama(model="llama3.1")
            logger.info("🦙 Service Ollama configuré avec Llama 3.1")
            self._test_connection()
            self._build_cocktail_workflow()
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation d'Ollama: {e}")
            raise
    
    def _test_connection(self):
        """Test la connexion à Ollama"""
        try:
            test_response = self.llm.invoke("Dis bonjour")
            logger.info("✅ Connexion Ollama OK")
        except Exception as e:
            logger.error(f"❌ Impossible de se connecter à Ollama: {e}")
            raise Exception("Ollama n'est pas disponible. Assurez-vous qu'Ollama est démarré avec: ollama serve")
    
    def _build_cocktail_workflow(self):
        """Construit le workflow LangGraph pour la génération de cocktails"""
        
        # Créer le graphe d'état
        graph = StateGraph(CocktailState)
        
        # Ajouter les nœuds du workflow
        graph.add_node("analyze_request", self._analyze_request)
        graph.add_node("determine_base_spirits", self._determine_base_spirits)
        graph.add_node("define_flavor_profile", self._define_flavor_profile)
        graph.add_node("create_concept", self._create_concept)
        graph.add_node("generate_ingredients", self._generate_ingredients)
        graph.add_node("write_instructions", self._write_instructions)
        graph.add_node("finalize_cocktail", self._finalize_cocktail)
        graph.add_node("generate_image_prompt", self._generate_image_prompt_node)
        
        # Définir le point d'entrée
        graph.set_entry_point("analyze_request")
        
        # Définir les transitions
        graph.add_edge("analyze_request", "determine_base_spirits")
        graph.add_edge("determine_base_spirits", "define_flavor_profile")
        graph.add_edge("define_flavor_profile", "create_concept")
        graph.add_edge("create_concept", "generate_ingredients")
        graph.add_edge("generate_ingredients", "write_instructions")
        graph.add_edge("write_instructions", "finalize_cocktail")
        graph.add_edge("finalize_cocktail", "generate_image_prompt")
        graph.add_edge("generate_image_prompt", END)
        
        # Compiler le workflow
        self.cocktail_graph = graph.compile()
        logger.info("🔄 Workflow LangGraph de génération de cocktails initialisé")
    
    def generate_cocktail(self, user_prompt: str, context: str = "") -> Dict[str, Any]:
        """Génère un cocktail en utilisant le workflow LangGraph"""
        logger.info(f"🦙 Génération IA avec workflow LangGraph pour: '{user_prompt}'")
        
        # État initial
        initial_state = CocktailState(
            user_prompt=user_prompt,
            context=context or "Création libre"
        )
        
        try:
            # Exécuter le workflow
            final_state = self.cocktail_graph.invoke(initial_state)
            
            # Récupérer le résultat final
            cocktail_data = final_state["final_cocktail"]
            cocktail_data['image_prompt'] = final_state["image_prompt"]
            
            # Ajouter une image placeholder
            cocktail_data['image_url'] = self._generate_placeholder_image()
            
            logger.info(f"✅ Cocktail généré via workflow: {cocktail_data['name']}")
            return cocktail_data
            
        except Exception as e:
            logger.error(f"❌ Erreur génération cocktail workflow: {e}")
            raise Exception(f"Impossible de générer le cocktail: {e}")
    
    # ============================================================================
    # ÉTAPES DU WORKFLOW LANGGRAPH
    # ============================================================================
    
    def _analyze_request(self, state: CocktailState) -> CocktailState:
        """Étape 1: Analyser la demande de l'utilisateur"""
        logger.info("🔍 Étape 1: Analyse de la demande")
        
        prompt = ChatPromptTemplate.from_template("""
        Analyse cette demande de cocktail et détermine le type et l'occasion.
        
        Demande: {user_prompt}
        Contexte: {context}
        
        Détermine:
        - Le type de cocktail souhaité
        - L'occasion ou le moment de consommation
        """)
        
        structured_llm = self.llm.with_structured_output(CocktailType)
        chain = prompt | structured_llm
        
        result = chain.invoke({
            "user_prompt": state.user_prompt,
            "context": state.context
        })
        
        state.cocktail_type = result.type
        logger.info(f"   → Type détecté: {result.type}, Occasion: {result.occasion}")
        return state
    
    def _determine_base_spirits(self, state: CocktailState) -> CocktailState:
        """Étape 2: Déterminer les alcools de base"""
        logger.info("🍺 Étape 2: Sélection des alcools de base")
        
        prompt = ChatPromptTemplate.from_template("""
        Basé sur cette demande, recommande les meilleurs alcools de base.
        
        Demande: {user_prompt}
        Type de cocktail: {cocktail_type}
        Contexte: {context}
        
        Recommande 1-3 alcools de base appropriés et explique pourquoi.
        """)
        
        structured_llm = self.llm.with_structured_output(BaseSpirits)
        chain = prompt | structured_llm
        
        result = chain.invoke({
            "user_prompt": state.user_prompt,
            "cocktail_type": state.cocktail_type,
            "context": state.context
        })
        
        state.base_spirits = result.spirits
        logger.info(f"   → Alcools sélectionnés: {', '.join(result.spirits)}")
        return state
    
    def _define_flavor_profile(self, state: CocktailState) -> CocktailState:
        """Étape 3: Définir le profil de saveur"""
        logger.info("👅 Étape 3: Définition du profil de saveur")
        
        prompt = ChatPromptTemplate.from_template("""
        Définis le profil de saveur pour ce cocktail.
        
        Demande: {user_prompt}
        Alcools de base: {base_spirits}
        Type: {cocktail_type}
        
        Détermine le profil de saveur et son intensité.
        """)
        
        structured_llm = self.llm.with_structured_output(FlavorProfile)
        chain = prompt | structured_llm
        
        result = chain.invoke({
            "user_prompt": state.user_prompt,
            "base_spirits": state.base_spirits,
            "cocktail_type": state.cocktail_type
        })
        
        state.flavor_profile = result.profile
        logger.info(f"   → Profil: {result.profile} ({result.intensity})")
        return state
    
    def _create_concept(self, state: CocktailState) -> CocktailState:
        """Étape 4: Créer le concept du cocktail"""
        logger.info("💡 Étape 4: Création du concept")
        
        prompt = ChatPromptTemplate.from_template("""
        Crée un concept créatif pour ce cocktail.
        
        Demande: {user_prompt}
        Alcools: {base_spirits}
        Profil de saveur: {flavor_profile}
        Type: {cocktail_type}
        
        Invente un nom créatif, une description narrative et un thème inspirant.
        """)
        
        structured_llm = self.llm.with_structured_output(CocktailConcept)
        chain = prompt | structured_llm
        
        result = chain.invoke({
            "user_prompt": state.user_prompt,
            "base_spirits": state.base_spirits,
            "flavor_profile": state.flavor_profile,
            "cocktail_type": state.cocktail_type
        })
        
        state.cocktail_concept = {
            "name": result.name,
            "description": result.description,
            "theme": result.theme
        }
        logger.info(f"   → Concept: {result.name}")
        return state
    
    def _generate_ingredients(self, state: CocktailState) -> CocktailState:
        """Étape 5: Générer la liste des ingrédients"""
        logger.info("🧪 Étape 5: Génération des ingrédients")
        
        prompt = ChatPromptTemplate.from_template("""
        Crée la liste précise des ingrédients pour ce cocktail.
        
        Nom: {name}
        Alcools de base: {base_spirits}
        Profil de saveur: {flavor_profile}
        Description: {description}
        
        IMPORTANT: Retourne une liste de dictionnaires avec ce format exact:
        - "nom": nom de l'ingrédient
        - "quantite": quantité avec unité (ex: "50 ml", "2 cl", "1 cuillère")
        - "type": type d'ingrédient ("alcool", "mixer", "garniture", "épice", "autre")
        
        Liste tous les ingrédients avec quantités précises.
        Inclus alcools, mixers, garnitures, épices, etc.
        """)
        
        structured_llm = self.llm.with_structured_output(CocktailIngredients)
        chain = prompt | structured_llm
        
        result = chain.invoke({
            "name": state.cocktail_concept["name"],
            "base_spirits": state.base_spirits,
            "flavor_profile": state.flavor_profile,
            "description": state.cocktail_concept["description"]
        })
        
        # Convertir immédiatement les ingrédients en dictionnaires
        ingredients_list = []
        for ingredient in result.ingredients:
            if hasattr(ingredient, 'dict'):  # Si c'est un objet Pydantic
                ingredients_list.append(ingredient.dict())
            elif hasattr(ingredient, '__dict__'):  # Si c'est un autre type d'objet
                ingredients_list.append(vars(ingredient))
            elif isinstance(ingredient, dict):  # Si c'est déjà un dictionnaire
                ingredients_list.append(ingredient)
            else:  # Autre type, convertir en dict basique
                ingredients_list.append({
                    'nom': str(ingredient), 
                    'quantite': 'À doser', 
                    'type': 'autre'
                })
        
        state.ingredients = ingredients_list
        logger.info(f"   → {len(ingredients_list)} ingrédients générés")
        return state
    
    def _write_instructions(self, state: CocktailState) -> CocktailState:
        """Étape 6: Rédiger les instructions"""
        logger.info("📝 Étape 6: Rédaction des instructions")
        
        prompt = ChatPromptTemplate.from_template("""
        Écris les instructions détaillées pour préparer ce cocktail.
        
        Nom: {name}
        Ingrédients: {ingredients}
        Profil: {flavor_profile}
        
        Fournis:
        - Instructions étape par étape
        - Type de verre recommandé
        - Garniture et décoration
        - Niveau de difficulté
        """)
        
        structured_llm = self.llm.with_structured_output(CocktailInstructions)
        chain = prompt | structured_llm
        
        result = chain.invoke({
            "name": state.cocktail_concept["name"],
            "ingredients": state.ingredients,
            "flavor_profile": state.flavor_profile
        })
        
        state.instructions = result.instructions
        logger.info(f"   → Instructions rédigées ({result.difficulty})")
        return state
    
    def _finalize_cocktail(self, state: CocktailState) -> CocktailState:
        """Étape 7: Finaliser le cocktail"""
        logger.info("✨ Étape 7: Finalisation du cocktail")
        
        # Convertir les ingrédients en dictionnaires JSON sérialisables
        ingredients_list = []
        for ingredient in state.ingredients:
            if hasattr(ingredient, 'dict'):  # Si c'est un objet Pydantic
                ingredients_list.append(ingredient.dict())
            elif isinstance(ingredient, dict):  # Si c'est déjà un dictionnaire
                ingredients_list.append(ingredient)
            else:  # Autre type, convertir en string puis en dict basique
                ingredients_list.append({'nom': str(ingredient), 'quantite': '', 'type': 'autre'})
        
        # Assembler toutes les données
        final_cocktail = {
            'name': state.cocktail_concept["name"],
            'description': state.cocktail_concept["description"],
            'instructions': state.instructions,
            'ingredients': ingredients_list,  # Utiliser la liste convertie
            'theme': state.cocktail_concept["theme"],
            'flavor_profile': state.flavor_profile,
            'alcohol_content': self._estimate_alcohol_content(ingredients_list),
            'preparation_time': self._estimate_prep_time_from_ingredients(ingredients_list),
            'original_prompt': state.user_prompt,
            'created_at': datetime.now().isoformat(),
            'music_ambiance': f"Ambiance parfaite pour déguster le {state.cocktail_concept['name']}"
        }
        
        state.final_cocktail = final_cocktail
        return state
    
    def _generate_image_prompt_node(self, state: CocktailState) -> CocktailState:
        """Étape 8: Générer le prompt d'image"""
        logger.info("🎨 Étape 8: Génération du prompt d'image")
        
        prompt = ChatPromptTemplate.from_template("""
        Crée un prompt en anglais pour générer l'image de ce cocktail.
        
        Nom: {name}
        Description: {description}
        Ingrédients: {ingredients}
        Thème: {theme}
        
        Le prompt doit être descriptif et visuellement évocateur pour une IA de génération d'images.
        """)
        
        structured_llm = self.llm.with_structured_output(ImagePrompt)
        chain = prompt | structured_llm
        
        result = chain.invoke({
            "name": state.cocktail_concept["name"],
            "description": state.cocktail_concept["description"],
            "ingredients": str(state.ingredients),
            "theme": state.cocktail_concept["theme"]
        })
        
        state.image_prompt = result.prompt
        logger.info(f"   → Prompt d'image généré")
        return state
    
    # ============================================================================
    # MÉTHODES UTILITAIRES
    # ============================================================================
    
    def _estimate_alcohol_content(self, ingredients: list) -> float:
        """Estime le degré d'alcool basé sur les ingrédients"""
        alcohol_keywords = ['vodka', 'gin', 'rhum', 'whisky', 'tequila', 'cognac', 'liqueur', 'vin', 'champagne']
        
        alcohol_count = 0
        for ing in ingredients:
            ing_name = ing.get('name', '') if isinstance(ing, dict) else str(ing)
            if any(keyword in ing_name.lower() for keyword in alcohol_keywords):
                alcohol_count += 1
        
        if alcohol_count == 0:
            return 0.0
        elif alcohol_count == 1:
            return random.uniform(8.0, 15.0)
        elif alcohol_count == 2:
            return random.uniform(15.0, 25.0)
        else:
            return random.uniform(25.0, 35.0)
    
    def _estimate_prep_time_from_ingredients(self, ingredients: list) -> int:
        """Estime le temps de préparation selon le nombre d'ingrédients"""
        ingredient_count = len(ingredients)
        
        if ingredient_count <= 3:
            return random.randint(2, 5)
        elif ingredient_count <= 6:
            return random.randint(5, 10)
        else:
            return random.randint(10, 20)
    
    def generate_image_prompt(self, cocktail_name: str, description: str) -> str:
        """Génère un prompt d'image (méthode de compatibilité)"""
        return self._generate_image_prompt_simple(cocktail_name, description)
    
    def _generate_image_prompt_simple(self, cocktail_name: str, description: str) -> str:
        """Version simplifiée pour compatibilité"""
        try:
            return f"Beautiful {cocktail_name} cocktail, {description[:100]}, professional photography, colorful, appetizing"
        except Exception:
            return f"Beautiful {cocktail_name} cocktail in a glass, professional photography, colorful, appetizing"
    
    def generate_image(self, image_prompt: str) -> Optional[str]:
        """Génère une image placeholder (Ollama ne fait pas d'images)"""
        logger.info(f"🖼️ Génération d'image placeholder pour: {image_prompt[:50]}...")
        return self._generate_placeholder_image()
    
    def _generate_placeholder_image(self) -> str:
        """Génère une image placeholder puisque Ollama ne fait pas d'images"""
        placeholder_images = [
            "placeholder_2ed8a5ba.jpg",
            "placeholder_3d0a5333.jpg", 
            "placeholder_401ddb34.jpg",
            "placeholder_5c46358c.jpg",
            "placeholder_9f138c66.jpg",
            "placeholder_ba0d131b.jpg"
        ]
        return f"cocktail_images/{random.choice(placeholder_images)}"
    
    def create_cocktail_recipe(self, cocktail_data: Dict[str, Any], user, generation_request) -> CocktailRecipe:
        """Crée une instance CocktailRecipe Django à partir des données IA"""
        try:
            # Adapter les champs au modèle Django
            difficulty_mapping = {
                'facile': 'easy',
                'moyen': 'medium', 
                'difficile': 'hard',
                'easy': 'easy',
                'medium': 'medium',
                'hard': 'hard'
            }
            
            # Estimer le niveau d'alcool
            alcohol_level = 'none'
            if cocktail_data.get('alcohol_content', 0) > 0:
                if cocktail_data['alcohol_content'] < 10:
                    alcohol_level = 'low'
                elif cocktail_data['alcohol_content'] < 20:
                    alcohol_level = 'medium'
                else:
                    alcohol_level = 'high'
            
            recipe = CocktailRecipe.objects.create(
                user=user,
                generation_request=generation_request,
                name=cocktail_data['name'],
                description=cocktail_data['description'],
                ingredients=cocktail_data.get('ingredients', []),  # Stocké en JSON
                music_ambiance=cocktail_data.get('music_ambiance', ''),
                image_prompt=cocktail_data.get('image_prompt', ''),
                image_url=cocktail_data.get('image_url', ''),
                difficulty_level=difficulty_mapping.get(cocktail_data.get('difficulty', 'facile'), 'medium'),
                alcohol_content=alcohol_level,
                preparation_time=cocktail_data.get('preparation_time', 5)
            )
            
            logger.info(f"✅ Cocktail créé en DB: {recipe.name}")
            return recipe
            
        except Exception as e:
            logger.error(f"❌ Erreur création DB: {e}")
            raise
