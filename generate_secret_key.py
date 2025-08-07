"""
Générateur de SECRET_KEY Django sécurisée
"""
from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    print("🔐 Génération d'une nouvelle SECRET_KEY Django:")
    print("=" * 60)
    secret_key = get_random_secret_key()
    print(f"SECRET_KEY={secret_key}")
    print("=" * 60)
    print("✅ Copiez cette clé dans votre fichier .env pour la production !")
    print("⚠️  Ne partagez JAMAIS cette clé et ne la commitez jamais dans Git !")
